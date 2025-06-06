import logging
from flask import Blueprint, jsonify, request
from models.customer import Customer
from models.vehicle import Vehicle
from models.service import Service
from models.part import Part
from database import db

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

@search_bp.route('/global', methods=['GET'])
def global_search():
    """Perform a global search across all entities"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        limit = request.args.get('limit', type=int, default=20)
        search_term = f"%{query}%"
        
        results = {
            'customers': [],
            'vehicles': [],
            'services': [],
            'parts': [],
            'total_results': 0
        }
        
        # Search customers
        customers = Customer.query.filter(
            db.or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.phone.ilike(search_term)
            )
        ).limit(limit).all()
        
        results['customers'] = [{
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'type': 'customer'
        } for customer in customers]
        
        # Search vehicles
        vehicles = Vehicle.query.filter(
            db.or_(
                Vehicle.registration.ilike(search_term),
                Vehicle.make.ilike(search_term),
                Vehicle.model.ilike(search_term)
            )
        ).limit(limit).all()
        
        results['vehicles'] = [{
            'id': vehicle.id,
            'registration': vehicle.registration,
            'make': vehicle.make,
            'model': vehicle.model,
            'customer_name': vehicle.customer.name if vehicle.customer else None,
            'type': 'vehicle'
        } for vehicle in vehicles]
        
        # Search services
        services = Service.query.filter(
            db.or_(
                Service.description.ilike(search_term),
                Service.technician.ilike(search_term),
                Service.invoice_number.ilike(search_term)
            )
        ).limit(limit).all()
        
        results['services'] = [{
            'id': service.id,
            'service_date': service.service_date.isoformat() if service.service_date else None,
            'service_type': service.service_type,
            'description': service.description[:100] + '...' if service.description and len(service.description) > 100 else service.description,
            'vehicle_registration': service.vehicle.registration if service.vehicle else None,
            'total_cost': float(service.total_cost) if service.total_cost else 0.0,
            'type': 'service'
        } for service in services]
        
        # Search parts
        parts = Part.query.filter(
            db.and_(
                Part.is_active == True,
                db.or_(
                    Part.part_number.ilike(search_term),
                    Part.description.ilike(search_term),
                    Part.supplier_part_number.ilike(search_term)
                )
            )
        ).limit(limit).all()
        
        results['parts'] = [{
            'id': part.id,
            'part_number': part.part_number,
            'description': part.description,
            'supplier': part.supplier,
            'stock_quantity': part.stock_quantity,
            'type': 'part'
        } for part in parts]
        
        results['total_results'] = len(results['customers']) + len(results['vehicles']) + len(results['services']) + len(results['parts'])
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in global search: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@search_bp.route('/customers', methods=['GET'])
def search_customers():
    """Search customers specifically"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = request.args.get('limit', type=int, default=50)
        search_term = f"%{query}%"
        
        customers = Customer.query.filter(
            db.or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.phone.ilike(search_term)
            )
        ).limit(limit).all()
        
        return jsonify([{
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'vehicle_count': len(customer.vehicles) if customer.vehicles else 0,
            'created_at': customer.created_at.isoformat()
        } for customer in customers])
        
    except Exception as e:
        logger.error(f"Error searching customers: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@search_bp.route('/vehicles', methods=['GET'])
def search_vehicles():
    """Search vehicles specifically"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = request.args.get('limit', type=int, default=50)
        search_term = f"%{query}%"
        
        vehicles = Vehicle.query.filter(
            db.or_(
                Vehicle.registration.ilike(search_term),
                Vehicle.make.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.color.ilike(search_term)
            )
        ).limit(limit).all()
        
        return jsonify([{
            'id': vehicle.id,
            'registration': vehicle.registration,
            'make': vehicle.make,
            'model': vehicle.model,
            'color': vehicle.color,
            'year': vehicle.year,
            'mot_expiry': vehicle.mot_expiry.isoformat() if vehicle.mot_expiry else None,
            'customer_name': vehicle.customer.name if vehicle.customer else None,
            'customer_id': vehicle.customer_id,
            'service_count': len(vehicle.services) if vehicle.services else 0,
            'mot_status': vehicle.mot_status()
        } for vehicle in vehicles])
        
    except Exception as e:
        logger.error(f"Error searching vehicles: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@search_bp.route('/services', methods=['GET'])
def search_services():
    """Search services specifically"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = request.args.get('limit', type=int, default=50)
        search_term = f"%{query}%"
        
        services = Service.query.filter(
            db.or_(
                Service.description.ilike(search_term),
                Service.technician.ilike(search_term),
                Service.invoice_number.ilike(search_term),
                Service.service_type.ilike(search_term)
            )
        ).order_by(Service.service_date.desc()).limit(limit).all()
        
        return jsonify([{
            'id': service.id,
            'service_date': service.service_date.isoformat() if service.service_date else None,
            'service_type': service.service_type,
            'description': service.description,
            'technician': service.technician,
            'total_cost': float(service.total_cost) if service.total_cost else 0.0,
            'status': service.status,
            'vehicle_registration': service.vehicle.registration if service.vehicle else None,
            'customer_name': service.vehicle.customer.name if service.vehicle and service.vehicle.customer else None
        } for service in services])
        
    except Exception as e:
        logger.error(f"Error searching services: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@search_bp.route('/parts', methods=['GET'])
def search_parts():
    """Search parts specifically"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = request.args.get('limit', type=int, default=50)
        active_only = request.args.get('active_only', type=bool, default=True)
        search_term = f"%{query}%"
        
        query_filter = db.or_(
            Part.part_number.ilike(search_term),
            Part.description.ilike(search_term),
            Part.supplier_part_number.ilike(search_term),
            Part.supplier.ilike(search_term)
        )
        
        if active_only:
            query_filter = db.and_(Part.is_active == True, query_filter)
        
        parts = Part.query.filter(query_filter).limit(limit).all()
        
        return jsonify([{
            'id': part.id,
            'part_number': part.part_number,
            'description': part.description,
            'category': part.category,
            'supplier': part.supplier,
            'sell_price': float(part.sell_price) if part.sell_price else 0.0,
            'stock_quantity': part.stock_quantity,
            'is_low_stock': part.is_low_stock(),
            'is_active': part.is_active
        } for part in parts])
        
    except Exception as e:
        logger.error(f"Error searching parts: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions based on partial input"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify([])
        
        limit = request.args.get('limit', type=int, default=10)
        search_term = f"{query}%"  # Prefix search for suggestions
        
        suggestions = []
        
        # Vehicle registrations
        vehicles = Vehicle.query.filter(
            Vehicle.registration.ilike(search_term)
        ).limit(limit // 2).all()
        
        for vehicle in vehicles:
            suggestions.append({
                'text': vehicle.registration,
                'type': 'vehicle',
                'label': f"{vehicle.registration} - {vehicle.make} {vehicle.model}",
                'id': vehicle.id
            })
        
        # Customer names
        customers = Customer.query.filter(
            Customer.name.ilike(search_term)
        ).limit(limit // 2).all()
        
        for customer in customers:
            suggestions.append({
                'text': customer.name,
                'type': 'customer',
                'label': f"{customer.name} - {customer.email or customer.phone or 'No contact'}",
                'id': customer.id
            })
        
        return jsonify(suggestions[:limit])
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return jsonify({'error': 'Internal server error'}), 500
