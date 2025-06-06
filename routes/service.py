import logging
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from models.service import Service
from models.vehicle import Vehicle
from models.customer import Customer
from models.part import Part
from models.part_usage import PartUsage
from database import db

logger = logging.getLogger(__name__)

service_bp = Blueprint('service', __name__)

# Get all services
@service_bp.route('/', methods=['GET'])
def get_services():
    """Get all services with optional filtering"""
    try:
        # Get query parameters for filtering
        vehicle_id = request.args.get('vehicle_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        service_type = request.args.get('service_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int, default=100)
        
        # Build query
        query = Service.query
        
        if vehicle_id:
            query = query.filter(Service.vehicle_id == vehicle_id)
        
        if customer_id:
            # Join with vehicle to filter by customer
            query = query.join(Vehicle).filter(Vehicle.customer_id == customer_id)
        
        if service_type:
            query = query.filter(Service.service_type == service_type)
        
        if status:
            query = query.filter(Service.status == status)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Service.service_date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Service.service_date <= end_date_obj)
        
        # Order by service date (most recent first) and apply limit
        services = query.order_by(Service.service_date.desc()).limit(limit).all()
        
        return jsonify([service.to_dict() for service in services])
        
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get services for a specific vehicle
@service_bp.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle_services(vehicle_id):
    """Get all services for a specific vehicle"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        services = Service.query.filter_by(vehicle_id=vehicle_id).order_by(Service.service_date.desc()).all()
        
        return jsonify({
            'vehicle': {
                'id': vehicle.id,
                'registration': vehicle.registration,
                'make': vehicle.make,
                'model': vehicle.model
            },
            'services': [service.to_dict() for service in services],
            'total_services': len(services),
            'total_spent': sum(float(service.total_cost or 0) for service in services)
        })
        
    except Exception as e:
        logger.error(f"Error fetching vehicle services: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get a specific service
@service_bp.route('/<int:id>', methods=['GET'])
def get_service(id):
    """Get a specific service with full details"""
    try:
        service = Service.query.get_or_404(id)
        return jsonify(service.to_dict())
        
    except Exception as e:
        logger.error(f"Error fetching service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Create a new service
@service_bp.route('/', methods=['POST'])
def create_service():
    """Create a new service record"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            return jsonify({'error': 'Vehicle ID is required'}), 400
        
        # Check if vehicle exists
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404

        service_date = data.get('service_date')
        if not service_date:
            return jsonify({'error': 'Service date is required'}), 400
        
        try:
            service_date_obj = datetime.strptime(service_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid service date format (YYYY-MM-DD required)'}), 400

        service_type = data.get('service_type', '').strip()
        if not service_type:
            return jsonify({'error': 'Service type is required'}), 400

        # Create new service
        service = Service(
            vehicle_id=vehicle_id,
            service_date=service_date_obj,
            service_type=service_type,
            description=data.get('description', '').strip(),
            labour_hours=float(data.get('labour_hours', 0)),
            labour_rate=float(data.get('labour_rate', 0)),
            technician=data.get('technician', '').strip(),
            advisories=data.get('advisories', '').strip(),
            status=data.get('status', 'completed'),
            mileage=int(data.get('mileage')) if data.get('mileage') else None,
            invoice_number=data.get('invoice_number', '').strip(),
            payment_status=data.get('payment_status', 'pending'),
            payment_method=data.get('payment_method', '').strip(),
            notes=data.get('notes', '').strip()
        )

        # Handle next service dates
        if data.get('next_service_due'):
            try:
                service.next_service_due = datetime.strptime(data['next_service_due'], '%Y-%m-%d').date()
            except ValueError:
                pass  # Ignore invalid date format
        
        if data.get('next_service_mileage'):
            service.next_service_mileage = int(data['next_service_mileage'])

        db.session.add(service)
        db.session.flush()  # Get the service ID

        # Handle parts if provided
        parts_data = data.get('parts', [])
        for part_data in parts_data:
            part_id = part_data.get('part_id')
            if part_id:
                part = Part.query.get(part_id)
                if part:
                    quantity = int(part_data.get('quantity', 1))
                    unit_cost = float(part_data.get('unit_cost', part.sell_price or 0))
                    
                    part_usage = PartUsage(
                        service_id=service.id,
                        part_id=part_id,
                        quantity=quantity,
                        unit_cost=unit_cost,
                        installation_notes=part_data.get('installation_notes', '')
                    )
                    
                    db.session.add(part_usage)
                    
                    # Update part stock
                    part.update_stock(quantity)

        # Calculate totals
        service.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Created new service for vehicle {vehicle.registration}")
        return jsonify(service.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Update a service
@service_bp.route('/<int:id>', methods=['PUT'])
def update_service(id):
    """Update an existing service record"""
    try:
        service = Service.query.get_or_404(id)
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields
        if 'service_date' in data:
            try:
                service.service_date = datetime.strptime(data['service_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid service date format'}), 400

        if 'service_type' in data:
            service.service_type = data['service_type'].strip()

        if 'description' in data:
            service.description = data['description'].strip()

        if 'labour_hours' in data:
            service.labour_hours = float(data['labour_hours'])

        if 'labour_rate' in data:
            service.labour_rate = float(data['labour_rate'])

        if 'technician' in data:
            service.technician = data['technician'].strip()

        if 'advisories' in data:
            service.advisories = data['advisories'].strip()

        if 'status' in data:
            service.status = data['status']

        if 'mileage' in data:
            service.mileage = int(data['mileage']) if data['mileage'] else None

        if 'invoice_number' in data:
            service.invoice_number = data['invoice_number'].strip()

        if 'payment_status' in data:
            service.payment_status = data['payment_status']

        if 'payment_method' in data:
            service.payment_method = data['payment_method'].strip()

        if 'notes' in data:
            service.notes = data['notes'].strip()

        # Recalculate totals
        service.calculate_totals()

        db.session.commit()

        logger.info(f"Updated service {id}")
        return jsonify(service.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete a service
@service_bp.route('/<int:id>', methods=['DELETE'])
def delete_service(id):
    """Delete a service record"""
    try:
        service = Service.query.get_or_404(id)

        # Restore part stock for any parts used
        for part_usage in service.part_usage:
            if part_usage.part:
                part_usage.part.stock_quantity += part_usage.quantity

        db.session.delete(service)
        db.session.commit()

        logger.info(f"Deleted service {id}")
        return jsonify({'message': 'Service deleted successfully'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get service statistics
@service_bp.route('/stats', methods=['GET'])
def get_service_stats():
    """Get service statistics"""
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Service.query

        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Service.service_date >= start_date_obj)

        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Service.service_date <= end_date_obj)

        services = query.all()

        # Calculate statistics
        total_services = len(services)
        total_revenue = sum(float(service.total_cost or 0) for service in services)
        total_labour_hours = sum(float(service.labour_hours or 0) for service in services)

        # Service type breakdown
        service_types = {}
        for service in services:
            service_type = service.service_type
            if service_type not in service_types:
                service_types[service_type] = {'count': 0, 'revenue': 0}
            service_types[service_type]['count'] += 1
            service_types[service_type]['revenue'] += float(service.total_cost or 0)

        # Payment status breakdown
        payment_status = {}
        for service in services:
            status = service.payment_status
            if status not in payment_status:
                payment_status[status] = {'count': 0, 'amount': 0}
            payment_status[status]['count'] += 1
            payment_status[status]['amount'] += float(service.total_cost or 0)

        return jsonify({
            'total_services': total_services,
            'total_revenue': total_revenue,
            'total_labour_hours': total_labour_hours,
            'average_service_value': total_revenue / total_services if total_services > 0 else 0,
            'service_types': service_types,
            'payment_status': payment_status
        })

    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500
