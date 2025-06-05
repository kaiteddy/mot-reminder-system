from flask import Blueprint, jsonify
from database import db
from models.customer import Customer
from models.vehicle import Vehicle
from models.reminder import Reminder

# Create blueprint for data management
data_mgmt_bp = Blueprint('data_mgmt', __name__)

@data_mgmt_bp.route('/clear-all-data', methods=['POST'])
def clear_all_data():
    """Clear all data from the database - customers, vehicles, and reminders"""
    try:
        # Delete all reminders first (due to foreign key constraints)
        reminders_deleted = Reminder.query.count()
        Reminder.query.delete()
        
        # Delete all vehicles
        vehicles_deleted = Vehicle.query.count()
        Vehicle.query.delete()
        
        # Delete all customers
        customers_deleted = Customer.query.count()
        Customer.query.delete()
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully',
            'deleted': {
                'customers': customers_deleted,
                'vehicles': vehicles_deleted,
                'reminders': reminders_deleted
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to clear data: {str(e)}'
        }), 500

@data_mgmt_bp.route('/database-status', methods=['GET'])
def database_status():
    """Get current database status"""
    try:
        customer_count = Customer.query.count()
        vehicle_count = Vehicle.query.count()
        reminder_count = Reminder.query.count()
        
        return jsonify({
            'success': True,
            'counts': {
                'customers': customer_count,
                'vehicles': vehicle_count,
                'reminders': reminder_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get database status: {str(e)}'
        }), 500

