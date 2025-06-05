from flask import Blueprint, jsonify, request, current_app
from database import db
from models.customer import Customer
from models.vehicle import Vehicle
from models.reminder import Reminder
from datetime import datetime
import re

# Enhanced customer blueprint
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def get_customers():
    """Get all customers with vehicle counts"""
    try:
        customers = Customer.query.all()
        customers_data = []
        
        for customer in customers:
            customer_dict = customer.to_dict()
            
            # Add vehicle count
            vehicle_count = Vehicle.query.filter_by(customer_id=customer.id).count()
            customer_dict['vehicle_count'] = vehicle_count
            
            # Add vehicles list
            vehicles = Vehicle.query.filter_by(customer_id=customer.id).all()
            customer_dict['vehicles'] = [v.to_dict() for v in vehicles]
            
            customers_data.append(customer_dict)
        
        return jsonify({
            'success': True,
            'customers': customers_data,
            'count': len(customers_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching customers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch customers',
            'message': str(e)
        }), 500

@customer_bp.route('/<int:id>')
def get_customer(id):
    """Get single customer with full details"""
    try:
        customer = Customer.query.get_or_404(id)
        customer_dict = customer.to_dict()
        
        # Add vehicles
        vehicles = Vehicle.query.filter_by(customer_id=id).all()
        customer_dict['vehicles'] = [v.to_dict() for v in vehicles]
        
        # Add reminders for customer's vehicles
        vehicle_ids = [v.id for v in vehicles]
        reminders = Reminder.query.filter(Reminder.vehicle_id.in_(vehicle_ids)).all()
        customer_dict['reminders'] = [r.to_dict() for r in reminders]
        
        return jsonify({
            'success': True,
            'customer': customer_dict,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching customer {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch customer',
            'message': str(e)
        }), 500

@customer_bp.route('/', methods=['POST'])
def create_customer():
    """Create new customer with validation"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Customer name is required'
            }), 400
        
        # Validate email format if provided
        email = data.get('email')
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate phone format if provided
        phone = data.get('phone')
        if phone and not re.match(r'^[\d\s\+\-\(\)]+$', phone):
            return jsonify({
                'success': False,
                'error': 'Invalid phone format'
            }), 400
        
        customer = Customer(
            name=data['name'].strip(),
            email=email.strip() if email else None,
            phone=phone.strip() if phone else None,
            account=data.get('account')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'message': 'Customer created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating customer: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create customer',
            'message': str(e)
        }), 500

@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    """Update customer with validation"""
    try:
        customer = Customer.query.get_or_404(id)
        data = request.json
        
        # Update fields if provided
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({
                    'success': False,
                    'error': 'Customer name cannot be empty'
                }), 400
            customer.name = data['name'].strip()
        
        if 'email' in data:
            email = data['email']
            if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400
            customer.email = email.strip() if email else None
        
        if 'phone' in data:
            phone = data['phone']
            if phone and not re.match(r'^[\d\s\+\-\(\)]+$', phone):
                return jsonify({
                    'success': False,
                    'error': 'Invalid phone format'
                }), 400
            customer.phone = phone.strip() if phone else None
        
        if 'account' in data:
            customer.account = data['account']
        
        customer.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'message': 'Customer updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating customer {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update customer',
            'message': str(e)
        }), 500

@customer_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Delete customer and handle associated vehicles"""
    try:
        customer = Customer.query.get_or_404(id)
        
        # Check for associated vehicles
        vehicles = Vehicle.query.filter_by(customer_id=id).all()
        if vehicles:
            return jsonify({
                'success': False,
                'error': f'Cannot delete customer with {len(vehicles)} associated vehicles',
                'vehicles': [v.registration for v in vehicles]
            }), 409
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting customer {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete customer',
            'message': str(e)
        }), 500

@customer_bp.route('/search')
def search_customers():
    """Search customers by name, email, or phone"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Search in name, email, and phone fields
        customers = Customer.query.filter(
            db.or_(
                Customer.name.ilike(f'%{query}%'),
                Customer.email.ilike(f'%{query}%'),
                Customer.phone.ilike(f'%{query}%')
            )
        ).all()
        
        customers_data = []
        for customer in customers:
            customer_dict = customer.to_dict()
            vehicle_count = Vehicle.query.filter_by(customer_id=customer.id).count()
            customer_dict['vehicle_count'] = vehicle_count
            customers_data.append(customer_dict)
        
        return jsonify({
            'success': True,
            'customers': customers_data,
            'count': len(customers_data),
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error searching customers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'message': str(e)
        }), 500

@customer_bp.route('/stats')
def get_customer_stats():
    """Get customer statistics"""
    try:
        total_customers = Customer.query.count()
        customers_with_email = Customer.query.filter(Customer.email.isnot(None)).count()
        customers_with_phone = Customer.query.filter(Customer.phone.isnot(None)).count()
        customers_with_vehicles = db.session.query(Customer.id).join(Vehicle).distinct().count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_customers,
                'with_email': customers_with_email,
                'with_phone': customers_with_phone,
                'with_vehicles': customers_with_vehicles
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting customer stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get customer statistics',
            'message': str(e)
        }), 500

