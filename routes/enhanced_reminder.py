from flask import Blueprint, jsonify, request, current_app
from database import db
from models.reminder import Reminder
from models.vehicle import Vehicle
from models.customer import Customer
from datetime import datetime, date, timedelta

# Enhanced reminder blueprint
reminder_bp = Blueprint('reminder', __name__)

@reminder_bp.route('/')
def get_reminders():
    """Get all reminders with vehicle and customer info"""
    try:
        reminders = Reminder.query.all()
        reminders_data = []
        
        for reminder in reminders:
            reminder_dict = reminder.to_dict()
            
            # Add vehicle information
            if reminder.vehicle_id:
                vehicle = Vehicle.query.get(reminder.vehicle_id)
                if vehicle:
                    reminder_dict['vehicle'] = {
                        'id': vehicle.id,
                        'registration': vehicle.registration,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'mot_expiry': vehicle.mot_expiry.isoformat() if vehicle.mot_expiry else None
                    }
                    
                    # Add customer information
                    if vehicle.customer_id:
                        customer = Customer.query.get(vehicle.customer_id)
                        if customer:
                            reminder_dict['customer'] = {
                                'id': customer.id,
                                'name': customer.name,
                                'email': customer.email,
                                'phone': customer.phone
                            }
            
            reminders_data.append(reminder_dict)
        
        return jsonify({
            'success': True,
            'reminders': reminders_data,
            'count': len(reminders_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching reminders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch reminders',
            'message': str(e)
        }), 500

@reminder_bp.route('/due')
def get_due_reminders():
    """Get reminders that are due now"""
    try:
        today = date.today()
        due_reminders = Reminder.query.filter(
            Reminder.reminder_date <= today,
            Reminder.status == 'scheduled'
        ).all()
        
        reminders_data = []
        for reminder in due_reminders:
            reminder_dict = reminder.to_dict()
            
            # Add vehicle and customer info
            if reminder.vehicle_id:
                vehicle = Vehicle.query.get(reminder.vehicle_id)
                if vehicle:
                    reminder_dict['vehicle'] = vehicle.to_dict()
                    if vehicle.customer_id:
                        customer = Customer.query.get(vehicle.customer_id)
                        if customer:
                            reminder_dict['customer'] = customer.to_dict()
            
            reminders_data.append(reminder_dict)
        
        return jsonify({
            'success': True,
            'reminders': reminders_data,
            'count': len(reminders_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching due reminders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch due reminders',
            'message': str(e)
        }), 500

@reminder_bp.route('/upcoming')
def get_upcoming_reminders():
    """Get reminders due in the next 30 days"""
    try:
        today = date.today()
        future_date = today + timedelta(days=30)
        
        upcoming_reminders = Reminder.query.filter(
            Reminder.reminder_date.between(today, future_date),
            Reminder.status == 'scheduled'
        ).all()
        
        reminders_data = []
        for reminder in upcoming_reminders:
            reminder_dict = reminder.to_dict()
            
            # Add vehicle and customer info
            if reminder.vehicle_id:
                vehicle = Vehicle.query.get(reminder.vehicle_id)
                if vehicle:
                    reminder_dict['vehicle'] = vehicle.to_dict()
                    if vehicle.customer_id:
                        customer = Customer.query.get(vehicle.customer_id)
                        if customer:
                            reminder_dict['customer'] = customer.to_dict()
            
            reminders_data.append(reminder_dict)
        
        return jsonify({
            'success': True,
            'reminders': reminders_data,
            'count': len(reminders_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching upcoming reminders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch upcoming reminders',
            'message': str(e)
        }), 500

@reminder_bp.route('/', methods=['POST'])
def create_reminder():
    """Create new reminder"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('vehicle_id'):
            return jsonify({
                'success': False,
                'error': 'Vehicle ID is required'
            }), 400
        
        if not data.get('reminder_date'):
            return jsonify({
                'success': False,
                'error': 'Reminder date is required'
            }), 400
        
        # Validate vehicle exists
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({
                'success': False,
                'error': 'Vehicle not found'
            }), 404
        
        reminder = Reminder(
            vehicle_id=data['vehicle_id'],
            reminder_date=datetime.strptime(data['reminder_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'scheduled'),
            reminder_type=data.get('reminder_type', 'mot_expiry'),
            message=data.get('message')
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reminder': reminder.to_dict(),
            'message': 'Reminder created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format. Use YYYY-MM-DD'
        }), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating reminder: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create reminder',
            'message': str(e)
        }), 500

@reminder_bp.route('/<int:id>', methods=['PUT'])
def update_reminder(id):
    """Update reminder"""
    try:
        reminder = Reminder.query.get_or_404(id)
        data = request.json
        
        # Update fields if provided
        if 'reminder_date' in data:
            reminder.reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%d').date()
        if 'status' in data:
            reminder.status = data['status']
        if 'reminder_type' in data:
            reminder.reminder_type = data['reminder_type']
        if 'message' in data:
            reminder.message = data['message']
        if 'sent_at' in data and data['sent_at']:
            reminder.sent_at = datetime.strptime(data['sent_at'], '%Y-%m-%d %H:%M:%S')
        
        reminder.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reminder': reminder.to_dict(),
            'message': 'Reminder updated successfully'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format'
        }), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating reminder {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update reminder',
            'message': str(e)
        }), 500

@reminder_bp.route('/<int:id>/send', methods=['POST'])
def send_reminder(id):
    """Mark reminder as sent"""
    try:
        reminder = Reminder.query.get_or_404(id)
        
        reminder.status = 'sent'
        reminder.sent_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reminder': reminder.to_dict(),
            'message': 'Reminder marked as sent'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending reminder {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send reminder',
            'message': str(e)
        }), 500

@reminder_bp.route('/bulk-schedule', methods=['POST'])
def bulk_schedule_reminders():
    """Schedule reminders for multiple vehicles"""
    try:
        data = request.json
        vehicle_ids = data.get('vehicle_ids', [])
        days_before = data.get('days_before', 30)
        
        if not vehicle_ids:
            return jsonify({
                'success': False,
                'error': 'No vehicle IDs provided'
            }), 400
        
        created_reminders = []
        errors = []
        
        for vehicle_id in vehicle_ids:
            try:
                vehicle = Vehicle.query.get(vehicle_id)
                if not vehicle or not vehicle.mot_expiry:
                    errors.append(f"Vehicle {vehicle_id}: No MOT expiry date")
                    continue
                
                # Calculate reminder date
                reminder_date = vehicle.mot_expiry - timedelta(days=days_before)
                
                # Check if reminder already exists
                existing = Reminder.query.filter_by(
                    vehicle_id=vehicle_id,
                    reminder_date=reminder_date
                ).first()
                
                if existing:
                    errors.append(f"Vehicle {vehicle_id}: Reminder already exists")
                    continue
                
                reminder = Reminder(
                    vehicle_id=vehicle_id,
                    reminder_date=reminder_date,
                    status='scheduled',
                    reminder_type='mot_expiry'
                )
                
                db.session.add(reminder)
                created_reminders.append(reminder)
                
            except Exception as e:
                errors.append(f"Vehicle {vehicle_id}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'created': len(created_reminders),
            'errors': errors,
            'reminders': [r.to_dict() for r in created_reminders]
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk schedule: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Bulk scheduling failed',
            'message': str(e)
        }), 500

@reminder_bp.route('/stats')
def get_reminder_stats():
    """Get reminder statistics"""
    try:
        total_reminders = Reminder.query.count()
        
        # Count by status
        scheduled = Reminder.query.filter_by(status='scheduled').count()
        sent = Reminder.query.filter_by(status='sent').count()
        failed = Reminder.query.filter_by(status='failed').count()
        
        # Count due reminders
        today = date.today()
        due_today = Reminder.query.filter(
            Reminder.reminder_date <= today,
            Reminder.status == 'scheduled'
        ).count()
        
        # Count upcoming reminders (next 7 days)
        next_week = today + timedelta(days=7)
        upcoming = Reminder.query.filter(
            Reminder.reminder_date.between(today + timedelta(days=1), next_week),
            Reminder.status == 'scheduled'
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_reminders,
                'scheduled': scheduled,
                'sent': sent,
                'failed': failed,
                'due_today': due_today,
                'upcoming_week': upcoming
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting reminder stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get reminder statistics',
            'message': str(e)
        }), 500

