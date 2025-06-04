"""
Batch DVLA Verification Service

This service handles batch processing of DVLA vehicle verification with:
- Progress tracking
- Queue management
- Rate limiting
- Background processing
- Status monitoring
"""

import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from database import db
from models.vehicle import Vehicle
from models.job_sheet import JobSheet
from services.dvla_api_service import DVLAApiService


class BatchStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class BatchProgress:
    total_vehicles: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    customers_linked: int = 0
    customers_created: int = 0
    current_registration: str = ""
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BatchDVLAService:
    """Service for batch DVLA verification with progress tracking and queue management"""
    
    def __init__(self):
        self.dvla_api = DVLAApiService()
        self._status = BatchStatus.IDLE
        self._progress = BatchProgress()
        self._thread: Optional[threading.Thread] = None
        self._stop_requested = False
        self._lock = threading.Lock()
        
        # Rate limiting settings
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.batch_size = 50  # Process in batches of 50
        self.max_retries = 3
        
    def get_status(self) -> Dict:
        """Get current batch processing status"""
        with self._lock:
            return {
                'status': self._status.value,
                'progress': asdict(self._progress),
                'is_running': self._status == BatchStatus.RUNNING,
                'can_start': self._status in [BatchStatus.IDLE, BatchStatus.COMPLETED, BatchStatus.ERROR, BatchStatus.STOPPED]
            }
    
    def start_batch_verification(self, verification_type: str = 'all') -> Dict:
        """
        Start batch DVLA verification process
        
        Args:
            verification_type: 'all', 'missing_mot', 'unverified', 'job_sheets'
        """
        with self._lock:
            if self._status == BatchStatus.RUNNING:
                return {
                    'success': False,
                    'message': 'Batch verification is already running'
                }
            
            # Reset progress
            self._progress = BatchProgress()
            self._stop_requested = False
            self._status = BatchStatus.RUNNING
            
            # Get vehicles to process
            vehicles = self._get_vehicles_for_verification(verification_type)
            self._progress.total_vehicles = len(vehicles)
            self._progress.start_time = datetime.now()
            
            if not vehicles:
                self._status = BatchStatus.COMPLETED
                return {
                    'success': True,
                    'message': 'No vehicles found for verification',
                    'total_vehicles': 0
                }
            
            # Start background thread
            self._thread = threading.Thread(
                target=self._process_batch,
                args=(vehicles,),
                daemon=True
            )
            self._thread.start()
            
            return {
                'success': True,
                'message': f'Started batch verification for {len(vehicles)} vehicles',
                'total_vehicles': len(vehicles),
                'verification_type': verification_type
            }
    
    def stop_batch_verification(self) -> Dict:
        """Stop the current batch verification process"""
        with self._lock:
            if self._status != BatchStatus.RUNNING:
                return {
                    'success': False,
                    'message': 'No batch verification is currently running'
                }
            
            self._stop_requested = True
            self._status = BatchStatus.STOPPED
            
            return {
                'success': True,
                'message': 'Batch verification stop requested'
            }
    
    def _get_vehicles_for_verification(self, verification_type: str) -> List[Vehicle]:
        """Get list of vehicles that need DVLA verification"""
        try:
            if verification_type == 'all':
                # All vehicles in the database
                return Vehicle.query.all()
            
            elif verification_type == 'missing_mot':
                # Vehicles without MOT expiry date
                return Vehicle.query.filter(
                    (Vehicle.mot_expiry.is_(None)) |
                    (Vehicle.mot_expiry == '')
                ).all()
            
            elif verification_type == 'unverified':
                # Vehicles that haven't been verified with DVLA recently
                cutoff_date = datetime.now() - timedelta(days=30)
                return Vehicle.query.filter(
                    (Vehicle.dvla_verified_at.is_(None)) |
                    (Vehicle.dvla_verified_at < cutoff_date)
                ).all()
            
            elif verification_type == 'job_sheets':
                # Vehicles from job sheets that aren't in vehicles table
                return self._get_job_sheet_vehicles()
            
            else:
                return []
                
        except Exception as e:
            print(f"Error getting vehicles for verification: {e}")
            return []
    
    def _get_job_sheet_vehicles(self) -> List[Vehicle]:
        """Get vehicles from job sheets that need to be created/verified"""
        try:
            # Get unique registrations from job sheets
            unique_regs = db.session.query(JobSheet.vehicle_reg).filter(
                JobSheet.vehicle_reg.isnot(None),
                JobSheet.vehicle_reg != ''
            ).distinct().all()
            
            vehicles = []
            for (reg,) in unique_regs:
                if not reg:
                    continue
                    
                # Check if vehicle already exists
                existing = Vehicle.query.filter_by(registration=reg.upper()).first()
                if not existing:
                    # Create placeholder vehicle for processing
                    vehicle = Vehicle(registration=reg.upper())
                    vehicles.append(vehicle)
                    
            return vehicles
            
        except Exception as e:
            print(f"Error getting job sheet vehicles: {e}")
            return []
    
    def _process_batch(self, vehicles: List[Vehicle]):
        """Process batch of vehicles in background thread"""
        try:
            for i, vehicle in enumerate(vehicles):
                # Check if stop was requested
                if self._stop_requested:
                    break
                
                with self._lock:
                    self._progress.current_registration = vehicle.registration
                    self._progress.processed = i + 1
                    
                    # Update estimated completion
                    if i > 0:
                        elapsed = datetime.now() - self._progress.start_time
                        avg_time_per_vehicle = elapsed.total_seconds() / i
                        remaining_vehicles = len(vehicles) - i
                        estimated_seconds = remaining_vehicles * avg_time_per_vehicle
                        self._progress.estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
                
                # Process single vehicle
                success = self._process_single_vehicle(vehicle)
                
                with self._lock:
                    if success:
                        self._progress.successful += 1
                    else:
                        self._progress.failed += 1
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
            
            # Mark as completed
            with self._lock:
                if not self._stop_requested:
                    self._status = BatchStatus.COMPLETED
                    
        except Exception as e:
            with self._lock:
                self._status = BatchStatus.ERROR
                self._progress.errors.append(f"Batch processing error: {str(e)}")
            print(f"Batch processing error: {e}")
    
    def _process_single_vehicle(self, vehicle: Vehicle) -> bool:
        """Process a single vehicle with DVLA verification and customer linking"""
        try:
            # Get DVLA data
            dvla_data = self.dvla_api.get_vehicle_details(vehicle.registration)

            if not dvla_data or not dvla_data.get('registrationNumber'):
                with self._lock:
                    self._progress.errors.append(f"No DVLA data found for {vehicle.registration}")
                return False

            # Update vehicle with DVLA data
            updated = self._update_vehicle_with_dvla_data(vehicle, dvla_data)

            # Link customer information from job sheets if not already linked
            customer_linked = self._link_customer_from_job_sheets(vehicle)

            if updated or customer_linked:
                # Mark as verified
                vehicle.dvla_verified_at = datetime.now()
                db.session.commit()
                return True
            else:
                with self._lock:
                    self._progress.skipped += 1
                return True

        except Exception as e:
            with self._lock:
                self._progress.errors.append(f"Error processing {vehicle.registration}: {str(e)}")
            print(f"Error processing {vehicle.registration}: {e}")
            return False
    
    def _update_vehicle_with_dvla_data(self, vehicle: Vehicle, dvla_data: Dict) -> bool:
        """Update vehicle with DVLA data, returns True if any updates were made"""
        updated = False
        
        try:
            # Update MOT expiry if missing or different
            if dvla_data.get('motExpiryDate'):
                new_mot_expiry = datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date()
                if not vehicle.mot_expiry or vehicle.mot_expiry != new_mot_expiry:
                    vehicle.mot_expiry = new_mot_expiry
                    updated = True
            
            # Update other fields if missing
            if not vehicle.make and dvla_data.get('make'):
                vehicle.make = dvla_data['make']
                updated = True
                
            if not vehicle.model and dvla_data.get('model'):
                vehicle.model = dvla_data['model']
                updated = True
                
            if not vehicle.color and dvla_data.get('primaryColour'):
                vehicle.color = dvla_data['primaryColour']
                updated = True
                
            if not vehicle.year and dvla_data.get('yearOfManufacture'):
                vehicle.year = int(dvla_data['yearOfManufacture'])
                updated = True
            
            return updated
            
        except Exception as e:
            print(f"Error updating vehicle {vehicle.registration} with DVLA data: {e}")
            return False

    def _link_customer_from_job_sheets(self, vehicle: Vehicle) -> bool:
        """Link customer information from job sheets if vehicle doesn't have a customer"""
        if vehicle.customer_id:
            return False  # Already has a customer

        from models.customer import Customer

        # Find job sheets for this vehicle
        job_sheets = JobSheet.query.filter_by(vehicle_reg=vehicle.registration.upper()).all()

        if not job_sheets:
            return False

        # Try to find a customer from the job sheets
        for job_sheet in job_sheets:
            customer = None

            # First try to find by external customer ID
            if job_sheet.customer_id_external:
                customer = Customer.query.filter_by(account=job_sheet.customer_id_external).first()

            # If not found, try by name
            if not customer and job_sheet.customer_name:
                customer = Customer.query.filter(
                    Customer.name.ilike(f"%{job_sheet.customer_name}%")
                ).first()

            # If still not found, create a new customer
            if not customer and job_sheet.customer_name:
                customer = Customer(
                    name=job_sheet.customer_name,
                    phone=job_sheet.contact_number,
                    account=job_sheet.customer_id_external
                )
                db.session.add(customer)
                db.session.flush()  # Get the ID

                with self._lock:
                    self._progress.customers_created += 1

            # Link the customer to the vehicle
            if customer:
                vehicle.customer_id = customer.id

                # Also update the job sheet linking
                job_sheet.linked_customer_id = customer.id
                job_sheet.linked_vehicle_id = vehicle.id

                with self._lock:
                    self._progress.customers_linked += 1

                return True

        return False
