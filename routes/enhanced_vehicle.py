from flask import Blueprint, jsonify, request, current_app
from database import db
from models.vehicle import Vehicle
from models.customer import Customer
from models.reminder import Reminder
from services.dvla_api_service import DVLAApiService
from services.ocr_service import OCRService
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

# Enhanced vehicle blueprint with better API responses
vehicle_bp = Blueprint('vehicle', __name__)
dvla_api = DVLAApiService()
ocr_service = OCRService()

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@vehicle_bp.route('/')
def get_vehicles():
    """Get all vehicles with enhanced data including customer info and MOT status"""
    try:
        vehicles = Vehicle.query.all()
        vehicles_data = []
        
        for vehicle in vehicles:
            vehicle_dict = vehicle.to_dict()
            
            # Add customer information
            if vehicle.customer_id:
                customer = Customer.query.get(vehicle.customer_id)
                if customer:
                    vehicle_dict['customer'] = {
                        'id': customer.id,
                        'name': customer.name,
                        'email': customer.email,
                        'phone': customer.phone
                    }
            
            # Add MOT status calculation
            if vehicle.mot_expiry:
                vehicle_dict['mot_status'] = vehicle.mot_status()
                vehicle_dict['days_until_expiry'] = vehicle.days_until_mot_expiry()
            
            vehicles_data.append(vehicle_dict)
        
        return jsonify({
            'success': True,
            'vehicles': vehicles_data,
            'count': len(vehicles_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching vehicles: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch vehicles',
            'message': str(e)
        }), 500

@vehicle_bp.route('/<int:id>')
def get_vehicle(id):
    """Get single vehicle with full details"""
    try:
        vehicle = Vehicle.query.get_or_404(id)
        vehicle_dict = vehicle.to_dict()
        
        # Add customer information
        if vehicle.customer_id:
            customer = Customer.query.get(vehicle.customer_id)
            if customer:
                vehicle_dict['customer'] = customer.to_dict()
        
        # Add reminders
        reminders = Reminder.query.filter_by(vehicle_id=id).all()
        vehicle_dict['reminders'] = [r.to_dict() for r in reminders]
        
        # Add MOT status
        if vehicle.mot_expiry:
            vehicle_dict['mot_status'] = vehicle.mot_status()
            vehicle_dict['days_until_expiry'] = vehicle.days_until_mot_expiry()
        
        return jsonify({
            'success': True,
            'vehicle': vehicle_dict,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching vehicle {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch vehicle',
            'message': str(e)
        }), 500

@vehicle_bp.route('/', methods=['POST'])
def create_vehicle():
    """Create new vehicle with validation"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('registration'):
            return jsonify({
                'success': False,
                'error': 'Registration is required'
            }), 400
        
        # Check if vehicle already exists
        existing = Vehicle.query.filter_by(registration=data['registration']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Vehicle with this registration already exists'
            }), 409
        
        vehicle = Vehicle(
            registration=data['registration'].upper(),
            make=data.get('make'),
            model=data.get('model'),
            color=data.get('color'),
            year=data.get('year'),
            mot_expiry=data.get('mot_expiry'),
            customer_id=data.get('customer_id')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vehicle': vehicle.to_dict(),
            'message': 'Vehicle created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating vehicle: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create vehicle',
            'message': str(e)
        }), 500

@vehicle_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle(id):
    """Update vehicle with validation"""
    try:
        vehicle = Vehicle.query.get_or_404(id)
        data = request.json
        
        # Update fields if provided
        if 'registration' in data:
            vehicle.registration = data['registration'].upper()
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'color' in data:
            vehicle.color = data['color']
        if 'year' in data:
            vehicle.year = data['year']
        if 'mot_expiry' in data:
            vehicle.mot_expiry = data['mot_expiry']
        if 'customer_id' in data:
            vehicle.customer_id = data['customer_id']
        
        vehicle.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vehicle': vehicle.to_dict(),
            'message': 'Vehicle updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating vehicle {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update vehicle',
            'message': str(e)
        }), 500

@vehicle_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    """Delete vehicle and associated reminders"""
    try:
        vehicle = Vehicle.query.get_or_404(id)
        
        # Delete associated reminders
        Reminder.query.filter_by(vehicle_id=id).delete()
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting vehicle {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete vehicle',
            'message': str(e)
        }), 500

@vehicle_bp.route('/dvla-lookup/<registration>')
def dvla_lookup(registration):
    """Enhanced DVLA lookup with better error handling"""
    try:
        # Clean registration
        clean_reg = registration.replace(' ', '').upper()
        
        # Perform DVLA lookup
        dvla_data = dvla_api.get_vehicle_data(clean_reg)
        
        if dvla_data:
            # Update vehicle if it exists
            vehicle = Vehicle.query.filter_by(registration=clean_reg).first()
            if vehicle:
                vehicle.make = dvla_data.get('make', vehicle.make)
                vehicle.model = dvla_data.get('model', vehicle.model)
                vehicle.color = dvla_data.get('colour', vehicle.color)
                vehicle.year = dvla_data.get('yearOfManufacture', vehicle.year)
                vehicle.mot_expiry = dvla_data.get('motExpiryDate', vehicle.mot_expiry)
                vehicle.dvla_verified_at = datetime.now()
                db.session.commit()
            
            return jsonify({
                'success': True,
                'data': dvla_data,
                'message': 'DVLA data retrieved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No data found for this registration'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error in DVLA lookup for {registration}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'DVLA lookup failed',
            'message': str(e)
        }), 500

@vehicle_bp.route('/bulk-dvla-check', methods=['POST'])
def bulk_dvla_check():
    """Perform bulk DVLA checks for multiple vehicles"""
    try:
        data = request.json
        registrations = data.get('registrations', [])
        
        if not registrations:
            return jsonify({
                'success': False,
                'error': 'No registrations provided'
            }), 400
        
        results = []
        for reg in registrations:
            try:
                clean_reg = reg.replace(' ', '').upper()
                dvla_data = dvla_api.get_vehicle_data(clean_reg)
                
                results.append({
                    'registration': clean_reg,
                    'success': bool(dvla_data),
                    'data': dvla_data
                })
            except Exception as e:
                results.append({
                    'registration': reg,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(registrations),
            'successful': len([r for r in results if r['success']])
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk DVLA check: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Bulk DVLA check failed',
            'message': str(e)
        }), 500

@vehicle_bp.route('/ocr-upload', methods=['POST'])
def ocr_upload():
    """Enhanced OCR upload with better error handling"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            try:
                # Perform OCR
                extracted_text = ocr_service.extract_text(filepath)
                registration = ocr_service.extract_registration(extracted_text)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'registration': registration,
                    'extracted_text': extracted_text,
                    'message': 'OCR processing completed'
                })
                
            except Exception as ocr_error:
                # Clean up uploaded file on error
                if os.path.exists(filepath):
                    os.remove(filepath)
                raise ocr_error
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error in OCR upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'OCR processing failed',
            'message': str(e)
        }), 500

@vehicle_bp.route('/stats')
def get_vehicle_stats():
    """Get vehicle statistics for dashboard"""
    try:
        total_vehicles = Vehicle.query.count()
        
        # Count vehicles by MOT status
        vehicles = Vehicle.query.all()
        status_counts = {
            'expired': 0,
            'expires_today': 0,
            'expires_soon': 0,
            'due_soon': 0,
            'current': 0
        }
        
        for vehicle in vehicles:
            if vehicle.mot_expiry:
                status = vehicle.mot_status()
                if status in status_counts:
                    status_counts[status] += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_vehicles,
                'by_status': status_counts
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting vehicle stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get vehicle statistics',
            'message': str(e)
        }), 500

