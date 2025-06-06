import re
import logging
from flask import Blueprint, jsonify, request
from models.customer import Customer
from models.vehicle import Vehicle
from database import db

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)

# Get all customers
@customer_bp.route('/', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

# Get a specific customer
@customer_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify(customer.to_dict())

# Create a new customer
@customer_bp.route('/', methods=['POST'])
def create_customer():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        if len(name) > 100:
            return jsonify({'error': 'Name must be less than 100 characters'}), 400

        # Validate email if provided
        email = data.get('email', '').strip() if data.get('email') else None
        if email:
            if len(email) > 100:
                return jsonify({'error': 'Email must be less than 100 characters'}), 400
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[-1]:
                return jsonify({'error': 'Invalid email format'}), 400

        # Validate phone if provided
        phone = data.get('phone', '').strip() if data.get('phone') else None
        if phone:
            if len(phone) > 20:
                return jsonify({'error': 'Phone must be less than 20 characters'}), 400

        # Create new customer
        customer = Customer(
            name=name,
            email=email,
            phone=phone
        )

        db.session.add(customer)
        db.session.commit()

        logger.info(f"Created new customer: {customer.name}")
        return jsonify(customer.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating customer: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Update a customer
@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields with validation
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Name cannot be empty'}), 400
            if len(name) > 100:
                return jsonify({'error': 'Name must be less than 100 characters'}), 400
            customer.name = name

        if 'email' in data:
            email = data['email'].strip() if data['email'] else None
            if email:
                if len(email) > 100:
                    return jsonify({'error': 'Email must be less than 100 characters'}), 400
                if '@' not in email or '.' not in email.split('@')[-1]:
                    return jsonify({'error': 'Invalid email format'}), 400
            customer.email = email

        if 'phone' in data:
            phone = data['phone'].strip() if data['phone'] else None
            if phone and len(phone) > 20:
                return jsonify({'error': 'Phone must be less than 20 characters'}), 400
            customer.phone = phone

        db.session.commit()
        logger.info(f"Updated customer: {customer.name}")
        return jsonify(customer.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating customer {id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete a customer
@customer_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)

    # Check if customer has vehicles
    if customer.vehicles:
        return jsonify({'error': 'Cannot delete customer with associated vehicles'}), 400

    db.session.delete(customer)
    db.session.commit()

    return jsonify({'message': 'Customer deleted successfully'})

# Get customer's vehicles
@customer_bp.route('/<int:id>/vehicles', methods=['GET'])
def get_customer_vehicles(id):
    customer = Customer.query.get_or_404(id)
    vehicles = Vehicle.query.filter_by(customer_id=customer.id).all()

    return jsonify([vehicle.to_dict() for vehicle in vehicles])
