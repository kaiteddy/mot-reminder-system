from flask import Blueprint, jsonify, request
from models.customer import Customer
from models.vehicle import Vehicle
from database import db

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
    data = request.json

    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    # Create new customer
    customer = Customer(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone')
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify(customer.to_dict()), 201

# Update a customer
@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.json

    # Update fields
    if 'name' in data:
        customer.name = data['name']
    if 'email' in data:
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']

    db.session.commit()

    return jsonify(customer.to_dict())

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
