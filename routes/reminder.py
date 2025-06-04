from flask import Blueprint, jsonify, request
from models.reminder import Reminder
from models.vehicle import Vehicle
from models.customer import Customer
from datetime import datetime, timedelta, date
from database import db
import uuid

reminder_bp = Blueprint('reminder', __name__)

# Get all reminders
@reminder_bp.route('/', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([reminder.to_dict() for reminder in reminders])

# Get reminders due now
@reminder_bp.route('/due', methods=['GET'])
def get_due_reminders():
    # Get reminders that are due (scheduled and reminder_date <= today)
    today = datetime.now().date()
    due_reminders = Reminder.query.filter(
        Reminder.status == 'scheduled',
        Reminder.reminder_date <= today
    ).all()

    result = []
    for reminder in due_reminders:
        reminder_dict = reminder.to_dict()

        # Add vehicle and customer info
        vehicle = Vehicle.query.get(reminder.vehicle_id)
        if vehicle:
            reminder_dict['vehicle'] = vehicle.to_dict()

            if vehicle.customer_id:
                customer = Customer.query.get(vehicle.customer_id)
                if customer:
                    reminder_dict['customer'] = customer.to_dict()

        result.append(reminder_dict)

    return jsonify(result)

# Get a specific reminder
@reminder_bp.route('/<int:id>', methods=['GET'])
def get_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    return jsonify(reminder.to_dict())

# Create a new reminder
@reminder_bp.route('/', methods=['POST'])
def create_reminder():
    data = request.json

    # Validate required fields
    if not data.get('vehicle_id'):
        return jsonify({'error': 'Vehicle ID is required'}), 400

    if not data.get('reminder_date'):
        return jsonify({'error': 'Reminder date is required'}), 400

    # Check if vehicle exists
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    # Parse reminder date
    try:
        reminder_date = datetime.fromisoformat(data['reminder_date'])
    except ValueError:
        return jsonify({'error': 'Invalid reminder date format'}), 400

    # Create new reminder
    reminder = Reminder(
        vehicle_id=data['vehicle_id'],
        reminder_date=reminder_date,
        status=data.get('status', 'scheduled')
    )

    db.session.add(reminder)
    db.session.commit()

    return jsonify(reminder.to_dict()), 201

# Update a reminder
@reminder_bp.route('/<int:id>', methods=['PUT'])
def update_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    data = request.json

    # Update fields
    if 'vehicle_id' in data:
        # Check if vehicle exists
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        reminder.vehicle_id = data['vehicle_id']

    if 'reminder_date' in data:
        try:
            reminder.reminder_date = datetime.fromisoformat(data['reminder_date'])
        except ValueError:
            return jsonify({'error': 'Invalid reminder date format'}), 400

    if 'status' in data:
        reminder.status = data['status']

        # If status is changed to 'sent', update sent_at timestamp
        if data['status'] == 'sent':
            reminder.sent_at = datetime.utcnow()

    db.session.commit()

    return jsonify(reminder.to_dict())

# Get reminder details
@reminder_bp.route('/<int:reminder_id>/details', methods=['GET'])
def get_reminder_details(reminder_id):
    """Get detailed information about a reminder including vehicle, customer, and DVLA data"""
    reminder = Reminder.query.get_or_404(reminder_id)

    # Get vehicle
    vehicle = Vehicle.query.get(reminder.vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    # Get customer
    customer = None
    if vehicle.customer_id:
        customer = Customer.query.get(vehicle.customer_id)

    # Get DVLA data
    dvla_data = {}
    try:
        from services.dvla_service import DVLAService
        dvla_service = DVLAService()
        dvla_data = dvla_service.get_vehicle_data(vehicle.registration)
    except Exception as e:
        print(f"Error fetching DVLA data: {e}")
        dvla_data = {}

    return jsonify({
        'reminder': reminder.to_dict(),
        'vehicle': vehicle.to_dict(),
        'customer': customer.to_dict() if customer else None,
        'dvla_data': dvla_data
    })

# Delete a reminder
@reminder_bp.route('/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    db.session.delete(reminder)
    db.session.commit()

    return jsonify({'message': 'Reminder deleted successfully'})

# Schedule reminders for vehicles with upcoming MOT expiry using DVLA verification
@reminder_bp.route('/schedule', methods=['POST'])
def schedule_reminders():
    """Schedule reminders using real-time DVLA verification"""
    # Get all vehicles (we'll verify MOT dates with DVLA)
    vehicles = Vehicle.query.filter(Vehicle.customer_id.isnot(None)).all()

    today = datetime.now().date()
    reminders_created = 0
    dvla_verified = 0
    dvla_errors = 0
    invalid_reminders_removed = 0

    # Import DVLA service
    try:
        from services.dvla_api_service import DVLAApiService
        dvla_service = DVLAApiService()
    except Exception as e:
        return jsonify({'error': f'DVLA service unavailable: {str(e)}'}), 500

    for vehicle in vehicles:
        try:
            # Get real-time DVLA data for this vehicle
            dvla_data = dvla_service.get_vehicle_details(vehicle.registration)

            if dvla_data and dvla_data.get('motExpiryDate'):
                dvla_verified += 1

                # Parse DVLA MOT expiry date
                dvla_mot_expiry = datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date()

                # Update vehicle with DVLA data if different
                if vehicle.mot_expiry != dvla_mot_expiry:
                    print(f"Updating {vehicle.registration}: {vehicle.mot_expiry} -> {dvla_mot_expiry}")
                    vehicle.mot_expiry = dvla_mot_expiry
                    vehicle.dvla_verified_at = datetime.utcnow()

                # Calculate days until MOT expiry using DVLA data
                days_until_expiry = (dvla_mot_expiry - today).days

                # Remove any existing invalid reminders for this vehicle
                invalid_reminders = Reminder.query.filter(
                    Reminder.vehicle_id == vehicle.id,
                    Reminder.status.in_(['scheduled', 'sent'])
                ).all()

                for invalid_reminder in invalid_reminders:
                    # Check if this reminder is still valid based on DVLA data
                    if days_until_expiry > 30:  # MOT is not due within 30 days
                        db.session.delete(invalid_reminder)
                        invalid_reminders_removed += 1
                        print(f"Removed invalid reminder for {vehicle.registration} (MOT valid for {days_until_expiry} days)")

                # Only create reminders for vehicles that actually need them (within 30 days or overdue)
                if days_until_expiry <= 30:
                    # Check if valid reminder already exists
                    existing_reminder = Reminder.query.filter(
                        Reminder.vehicle_id == vehicle.id,
                        Reminder.status.in_(['scheduled', 'sent'])
                    ).first()

                    if not existing_reminder:
                        # Create reminder with DVLA-verified data
                        reminder = Reminder(
                            vehicle_id=vehicle.id,
                            reminder_date=today,
                            status='scheduled'
                        )

                        db.session.add(reminder)
                        reminders_created += 1

                        print(f"Created DVLA-verified reminder for {vehicle.registration}: MOT expires {dvla_mot_expiry} ({days_until_expiry} days)")
                else:
                    print(f"Skipped {vehicle.registration}: MOT valid for {days_until_expiry} days")
            else:
                dvla_errors += 1
                print(f"No DVLA data available for {vehicle.registration}")

        except Exception as e:
            dvla_errors += 1
            print(f"Error processing {vehicle.registration}: {e}")

    db.session.commit()

    return jsonify({
        'message': f'Scheduled {reminders_created} DVLA-verified reminders',
        'reminders_created': reminders_created,
        'invalid_reminders_removed': invalid_reminders_removed,
        'dvla_verified': dvla_verified,
        'dvla_errors': dvla_errors,
        'total_vehicles': len(vehicles)
    })

# Process reminders (send emails/SMS)
@reminder_bp.route('/process', methods=['POST'])
def process_reminders():
    # Get all scheduled reminders due today or earlier
    today = datetime.now().date()
    due_reminders = Reminder.query.filter(
        Reminder.status == 'scheduled',
        Reminder.reminder_date <= today
    ).all()

    processed_count = 0

    for reminder in due_reminders:
        # Get vehicle and customer info
        vehicle = Vehicle.query.get(reminder.vehicle_id)
        if not vehicle or not vehicle.customer_id:
            reminder.status = 'failed'
            continue

        customer = Customer.query.get(vehicle.customer_id)
        if not customer:
            reminder.status = 'failed'
            continue

        # In a real implementation, this would send emails or SMS
        # For local development, we'll just mark them as sent

        reminder.status = 'sent'
        reminder.sent_at = datetime.utcnow()
        processed_count += 1

    db.session.commit()

    return jsonify({
        'message': f'Processed {processed_count} reminders',
        'reminders_processed': processed_count
    })

# Email template endpoints
@reminder_bp.route('/templates/email', methods=['GET', 'POST'])
def email_template():
    if request.method == 'POST':
        data = request.json
        # In a real implementation, this would save the template to the database
        return jsonify({'message': 'Email template saved'})
    else:
        # Return default template
        default_template = """
        Dear {customer_name},

        This is a reminder that the MOT for your {vehicle_make} {vehicle_model} (Registration: {vehicle_registration}) is due to expire on {mot_expiry_date}.

        Please contact us to schedule an appointment.

        Thank you,
        Your Garage
        """
        return jsonify({'template': default_template})

# SMS template endpoints
@reminder_bp.route('/templates/sms', methods=['GET', 'POST'])
def sms_template():
    if request.method == 'POST':
        data = request.json
        # In a real implementation, this would save the template to the database
        return jsonify({'message': 'SMS template saved'})
    else:
        # Return default template
        default_template = """MOT Reminder: Your {vehicle_make} {vehicle_model} (Reg: {vehicle_registration}) MOT expires on {mot_expiry_date}. Please contact us to book."""
        return jsonify({'template': default_template})

# New enhanced reminder management endpoints
@reminder_bp.route('/review/<batch_id>', methods=['GET'])
def review_batch(batch_id):
    """Get all vehicles for review after upload"""
    # Get all vehicles that need reminders (MOT expiring within 60 days or expired)
    vehicles = Vehicle.query.filter(
        Vehicle.mot_expiry.isnot(None)
    ).all()

    # Filter vehicles that need attention
    review_vehicles = []
    duplicates = []

    for vehicle in vehicles:
        days_until_expiry = vehicle.days_until_mot_expiry()
        if days_until_expiry is not None and days_until_expiry <= 60:  # 60 days or expired
            vehicle_data = vehicle.to_dict()

            # Check for existing reminders
            existing_reminder = Reminder.query.filter_by(
                vehicle_id=vehicle.id,
                status='scheduled'
            ).first()

            if existing_reminder:
                duplicates.append({
                    'vehicle': vehicle_data,
                    'existing_reminder': existing_reminder.to_dict()
                })
            else:
                review_vehicles.append(vehicle_data)

    return jsonify({
        'batch_id': batch_id,
        'vehicles_for_review': review_vehicles,
        'duplicates': duplicates,
        'total_count': len(review_vehicles) + len(duplicates)
    })

@reminder_bp.route('/generate-batch', methods=['POST'])
def generate_reminders_batch():
    """Generate reminders for selected vehicles"""
    data = request.json
    vehicle_ids = data.get('vehicle_ids', [])
    batch_id = data.get('batch_id')

    if not vehicle_ids:
        return jsonify({'error': 'No vehicles selected'}), 400

    # Archive previous reminders for these vehicles
    previous_reminders = Reminder.query.filter(
        Reminder.vehicle_id.in_(vehicle_ids),
        Reminder.status.in_(['scheduled', 'sent'])
    ).all()

    for reminder in previous_reminders:
        reminder.status = 'archived'
        reminder.archived_at = datetime.utcnow()

    # Create new reminders
    created_reminders = []
    for vehicle_id in vehicle_ids:
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle and vehicle.mot_expiry:
            # Calculate reminder date (30 days before expiry, or today if already past)
            reminder_date = vehicle.mot_expiry - timedelta(days=30)
            if reminder_date < date.today():
                reminder_date = date.today()

            reminder = Reminder(
                vehicle_id=vehicle_id,
                reminder_date=reminder_date,
                review_batch_id=batch_id,
                status='scheduled'
            )
            db.session.add(reminder)
            created_reminders.append(reminder)

    db.session.commit()

    return jsonify({
        'message': f'Created {len(created_reminders)} reminders',
        'archived_count': len(previous_reminders),
        'created_count': len(created_reminders),
        'batch_id': batch_id
    })

@reminder_bp.route('/bulk-action', methods=['POST'])
def bulk_reminder_action():
    """Perform bulk actions on reminders"""
    data = request.json
    reminder_ids = data.get('reminder_ids', [])
    action = data.get('action')  # 'send', 'archive', 'delete'

    if not reminder_ids or not action:
        return jsonify({'error': 'Missing reminder IDs or action'}), 400

    reminders = Reminder.query.filter(Reminder.id.in_(reminder_ids)).all()
    processed_count = 0

    for reminder in reminders:
        if action == 'send':
            reminder.status = 'sent'
            reminder.sent_at = datetime.utcnow()
            processed_count += 1
        elif action == 'archive':
            reminder.status = 'archived'
            reminder.archived_at = datetime.utcnow()
            processed_count += 1
        elif action == 'delete':
            db.session.delete(reminder)
            processed_count += 1

    db.session.commit()

    return jsonify({
        'message': f'{action.title()}d {processed_count} reminders',
        'processed_count': processed_count
    })

@reminder_bp.route('/clear-all', methods=['POST'])
def clear_all_reminders():
    """Clear all reminders from the database"""
    try:
        # Get count before deletion
        reminder_count = Reminder.query.count()

        # Delete all reminders
        Reminder.query.delete()
        db.session.commit()

        return jsonify({
            'message': f'Successfully cleared {reminder_count} reminders',
            'cleared_count': reminder_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to clear reminders: {str(e)}'
        }), 500

@reminder_bp.route('/cleanup-invalid', methods=['POST'])
def cleanup_invalid_reminders():
    """Remove invalid reminders and regenerate with DVLA verification"""
    try:
        from services.dvla_api_service import DVLAApiService
        dvla_service = DVLAApiService()
    except Exception as e:
        return jsonify({'error': f'DVLA service unavailable: {str(e)}'}), 500

    today = date.today()
    invalid_reminders_removed = 0
    vehicles_updated = 0
    new_reminders_created = 0
    dvla_errors = 0

    # Get all active reminders
    active_reminders = Reminder.query.filter(
        Reminder.status.in_(['scheduled', 'sent'])
    ).all()

    for reminder in active_reminders:
        vehicle = Vehicle.query.get(reminder.vehicle_id)
        if not vehicle:
            continue

        try:
            # Get DVLA data
            dvla_data = dvla_service.get_vehicle_details(vehicle.registration)

            if dvla_data and dvla_data.get('motExpiryDate'):
                dvla_mot_expiry = datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date()

                # Update vehicle MOT date if different
                if vehicle.mot_expiry != dvla_mot_expiry:
                    vehicle.mot_expiry = dvla_mot_expiry
                    vehicle.dvla_verified_at = datetime.now()
                    vehicles_updated += 1

                # Calculate days until expiry based on DVLA data
                days_until_expiry = (dvla_mot_expiry - today).days

                # Remove reminder if MOT is not due within 30 days
                if days_until_expiry > 30:
                    db.session.delete(reminder)
                    invalid_reminders_removed += 1
            else:
                dvla_errors += 1

        except Exception as e:
            dvla_errors += 1
            print(f"Error processing {vehicle.registration}: {e}")

    # Create new reminders for vehicles that need them
    vehicles_needing_reminders = Vehicle.query.filter(
        Vehicle.customer_id.isnot(None),
        Vehicle.mot_expiry.isnot(None)
    ).all()

    for vehicle in vehicles_needing_reminders:
        if vehicle.mot_expiry:
            days_until_expiry = (vehicle.mot_expiry - today).days

            if days_until_expiry <= 30:
                # Check if reminder already exists
                existing_reminder = Reminder.query.filter(
                    Reminder.vehicle_id == vehicle.id,
                    Reminder.status.in_(['scheduled', 'sent'])
                ).first()

                if not existing_reminder:
                    reminder = Reminder(
                        vehicle_id=vehicle.id,
                        reminder_date=today,
                        status='scheduled'
                    )
                    db.session.add(reminder)
                    new_reminders_created += 1

    db.session.commit()

    return jsonify({
        'message': 'Invalid reminders cleanup completed',
        'invalid_reminders_removed': invalid_reminders_removed,
        'vehicles_updated': vehicles_updated,
        'new_reminders_created': new_reminders_created,
        'dvla_errors': dvla_errors
    })
