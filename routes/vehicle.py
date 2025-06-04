from flask import Blueprint, jsonify, request, current_app
from database import db
from models.vehicle import Vehicle
from services.dvla_api_service import DVLAApiService
from services.ocr_service import OCRService
import os
import uuid
from werkzeug.utils import secure_filename

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
    vehicles = Vehicle.query.all()
    return jsonify([v.to_dict() for v in vehicles])

@vehicle_bp.route('/<int:id>')
def get_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    return jsonify(vehicle.to_dict())

@vehicle_bp.route('/', methods=['POST'])
def create_vehicle():
    data = request.json
    vehicle = Vehicle(
        registration=data['registration'],
        make=data.get('make'),
        model=data.get('model'),
        color=data.get('color'),
        year=data.get('year'),
        mot_expiry=data.get('mot_expiry'),
        customer_id=data.get('customer_id')
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify(vehicle.to_dict()), 201

@vehicle_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.json

    vehicle.registration = data.get('registration', vehicle.registration)
    vehicle.make = data.get('make', vehicle.make)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.color = data.get('color', vehicle.color)
    vehicle.year = data.get('year', vehicle.year)
    vehicle.mot_expiry = data.get('mot_expiry', vehicle.mot_expiry)
    vehicle.customer_id = data.get('customer_id', vehicle.customer_id)

    db.session.commit()
    return jsonify(vehicle.to_dict())

@vehicle_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted'})

@vehicle_bp.route('/lookup/<registration>')
def lookup_vehicle(registration):
    vehicle_data = dvla_api.get_vehicle_details(registration)
    return jsonify(vehicle_data)

@vehicle_bp.route('/<int:id>/check', methods=['POST'])
def check_vehicle(id):
    from services.cross_check_service import CrossCheckService

    vehicle = Vehicle.query.get_or_404(id)
    cross_check = CrossCheckService()
    result = cross_check.check_vehicle(vehicle)

    return jsonify(result)

@vehicle_bp.route('/<int:id>/update-from-dvla', methods=['POST'])
def update_from_dvla(id):
    from services.cross_check_service import CrossCheckService

    vehicle = Vehicle.query.get_or_404(id)
    cross_check = CrossCheckService()
    updated_vehicle = cross_check.update_vehicle_from_dvla(vehicle)

    db.session.commit()
    return jsonify(updated_vehicle.to_dict())

@vehicle_bp.route('/ocr/upload', methods=['POST'])
def upload_image_for_ocr():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process image with OCR
        try:
            results = ocr_service.process_image(filepath)

            # Add file path to results for reference
            results['image_path'] = filename

            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File type not allowed'}), 400

@vehicle_bp.route('/ocr/verify', methods=['POST'])
def verify_registration():
    data = request.json
    registration = data.get('registration')

    if not registration:
        return jsonify({'error': 'Registration is required'}), 400

    # Verify with DVLA
    is_valid, vehicle_data = ocr_service.verify_with_dvla(registration)

    return jsonify({
        'registration': registration,
        'is_valid': is_valid,
        'vehicle_data': vehicle_data
    })

@vehicle_bp.route('/csv/upload', methods=['POST'])
def upload_csv():
    """Enhanced CSV upload with DVLA cross-checking"""
    import uuid
    from datetime import datetime

    data = request.json
    csv_data = data.get('csv_data', [])

    if not csv_data:
        return jsonify({'error': 'No CSV data provided'}), 400

    # Create a unique batch ID for this upload session
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    results = {
        'processed': 0,
        'errors': [],
        'vehicles_created': [],
        'customers_created': [],
        'dvla_lookups': [],
        'batch_id': batch_id,
        'redirect_to_review': True
    }

    for row_index, row_data in enumerate(csv_data):
        try:
            result = process_csv_row_with_dvla(row_data, row_index + 1)

            if result['success']:
                results['processed'] += 1
                results['vehicles_created'].append(result['vehicle'])

                if result.get('customer_created'):
                    results['customers_created'].append(result['customer'])

                results['dvla_lookups'].append({
                    'registration': result['registration'],
                    'dvla_found': result['dvla_found'],
                    'dvla_data': result.get('dvla_data'),
                    'csv_data': result.get('csv_data')
                })
            else:
                results['errors'].append(f"Row {row_index + 1}: {result['error']}")

        except Exception as e:
            results['errors'].append(f"Row {row_index + 1}: {str(e)}")

    # After processing all vehicles, automatically create reminders for vehicles that need them
    from models.reminder import Reminder
    from datetime import date, timedelta

    created_reminders = 0
    for vehicle_data in results['vehicles_created']:
        # vehicles_created contains vehicle dictionaries directly
        if not isinstance(vehicle_data, dict) or 'id' not in vehicle_data:
            continue  # Skip invalid entries

        vehicle_id = vehicle_data['id']

        # Check if vehicle has MOT expiry and needs a reminder
        if vehicle_data.get('mot_expiry'):
            try:
                mot_expiry = datetime.strptime(vehicle_data['mot_expiry'], '%Y-%m-%d').date()
                days_until_expiry = (mot_expiry - date.today()).days

                # Create reminder if MOT expires within 60 days or has expired
                if days_until_expiry <= 60:
                    # Check if reminder already exists
                    existing_reminder = Reminder.query.filter_by(
                        vehicle_id=vehicle_id,
                        status='scheduled'
                    ).first()

                    if not existing_reminder:
                        # Calculate reminder date (30 days before expiry, or today if already past)
                        reminder_date = mot_expiry - timedelta(days=30)
                        if reminder_date < date.today():
                            reminder_date = date.today()

                        reminder = Reminder(
                            vehicle_id=vehicle_id,
                            reminder_date=reminder_date,
                            review_batch_id=batch_id,
                            status='scheduled'
                        )
                        db.session.add(reminder)
                        created_reminders += 1
            except Exception as e:
                print(f"Error creating reminder for vehicle {vehicle_id}: {e}")

    if created_reminders > 0:
        try:
            db.session.commit()
            results['reminders_created'] = created_reminders
        except Exception as e:
            print(f"Error committing reminders: {e}")
            db.session.rollback()
            results['reminders_created'] = 0
    else:
        results['reminders_created'] = 0

    return jsonify(results)

def parse_customer_data(customer_string):
    """Parse customer data from the specific format: 'Name t: phone m: mobile e: email'"""
    if not customer_string or customer_string.strip() == '-':
        return None

    customer_info = {
        'name': '',
        'phone': '',
        'email': ''
    }

    try:
        # Split by common patterns
        parts = customer_string.strip()

        # Extract name (everything before 't:' or first contact info)
        if ' t:' in parts:
            name_part = parts.split(' t:')[0].strip()
        elif ' m:' in parts:
            name_part = parts.split(' m:')[0].strip()
        elif ' e:' in parts:
            name_part = parts.split(' e:')[0].strip()
        else:
            name_part = parts

        customer_info['name'] = name_part

        # Extract phone numbers (look for patterns like 'm: 07...' or 't: 8203...')
        import re

        # Mobile phone pattern (m: followed by number)
        mobile_match = re.search(r'm:\s*([0-9\s]+)', parts)
        if mobile_match:
            customer_info['phone'] = mobile_match.group(1).strip()

        # If no mobile, try landline (t: followed by number)
        if not customer_info['phone']:
            landline_match = re.search(r't:\s*([0-9\s]+)', parts)
            if landline_match:
                customer_info['phone'] = landline_match.group(1).strip()

        # Extract email (e: followed by email)
        email_match = re.search(r'e:\s*([^\s]+@[^\s]+)', parts)
        if email_match:
            customer_info['email'] = email_match.group(1).strip()

        # Clean up phone number (remove extra spaces)
        if customer_info['phone']:
            customer_info['phone'] = re.sub(r'\s+', '', customer_info['phone'])

        return customer_info

    except Exception as e:
        print(f"Error parsing customer data '{customer_string}': {e}")
        return {'name': customer_string.strip(), 'phone': '', 'email': ''}

def process_csv_row_with_dvla(row_data, row_number):
    """Process a single CSV row with DVLA lookup and cross-checking"""
    from datetime import datetime

    registration = row_data.get('registration', '').strip()

    if not registration:
        return {'success': False, 'error': 'Registration is required'}

    # Step 1: Lookup vehicle in DVLA
    dvla_data = dvla_api.get_vehicle_details(registration)
    dvla_found = dvla_data and 'registrationNumber' in dvla_data

    # Step 2: Prepare vehicle data, prioritizing DVLA data
    vehicle_data = {
        'registration': registration
    }

    # Helper function to parse date strings
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            # Handle various date formats
            if 'T' in date_str:  # ISO format from DVLA
                return datetime.fromisoformat(date_str.split('T')[0]).date()
            elif '/' in date_str:  # DD/MM/YYYY format from your data
                return datetime.strptime(date_str, '%d/%m/%Y').date()
            else:  # YYYY-MM-DD format from CSV
                return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    # Use DVLA data as primary source, fall back to CSV data
    if dvla_found:
        vehicle_data.update({
            'make': dvla_data.get('make', row_data.get('make', '')),
            'model': dvla_data.get('model', row_data.get('model', '')),
            'color': dvla_data.get('primaryColour', row_data.get('color', '')),
            'year': dvla_data.get('yearOfManufacture', row_data.get('year'))
        })

        # Use DVLA MOT expiry if available, otherwise use CSV
        if dvla_data.get('motExpiryDate'):
            vehicle_data['mot_expiry'] = parse_date(dvla_data['motExpiryDate'])
        elif row_data.get('work_due') or row_data.get('Work Due'):
            # Handle your data format where MOT expiry is in 'Work Due' column
            work_due = row_data.get('work_due') or row_data.get('Work Due')
            vehicle_data['mot_expiry'] = parse_date(work_due)
        elif row_data.get('mot_expiry'):
            vehicle_data['mot_expiry'] = parse_date(row_data.get('mot_expiry'))
    else:
        # No DVLA data found, use CSV data
        vehicle_data.update({
            'make': row_data.get('make') or row_data.get('Make', ''),
            'model': row_data.get('model', ''),
            'color': row_data.get('color', ''),
            'year': int(row_data.get('year')) if row_data.get('year') and str(row_data.get('year')).isdigit() else None,
            'mot_expiry': parse_date(row_data.get('work_due') or row_data.get('Work Due') or row_data.get('mot_expiry'))
        })

    # Step 3: Handle customer - parse from the specific format
    customer_id = None
    customer_created = False
    customer_data = None

    # Try different column names for customer data
    customer_string = row_data.get('customer') or row_data.get('Customer') or row_data.get('customer_name')

    if customer_string:
        # Parse the customer data from the specific format
        parsed_customer = parse_customer_data(customer_string)

        if parsed_customer and parsed_customer['name']:
            from models.customer import Customer

            # Check if customer exists (search by name)
            existing_customer = Customer.query.filter(
                Customer.name.ilike(f"%{parsed_customer['name'].strip()}%")
            ).first()

            if existing_customer:
                customer_id = existing_customer.id
                customer_data = existing_customer.to_dict()

                # Update existing customer with new contact info if provided
                if parsed_customer['phone'] and not existing_customer.phone:
                    existing_customer.phone = parsed_customer['phone']
                if parsed_customer['email'] and not existing_customer.email:
                    existing_customer.email = parsed_customer['email']
            else:
                # Create new customer
                new_customer = Customer(
                    name=parsed_customer['name'].strip(),
                    email=parsed_customer['email'].strip() if parsed_customer['email'] else None,
                    phone=parsed_customer['phone'].strip() if parsed_customer['phone'] else None
                )
                db.session.add(new_customer)
                db.session.flush()  # Get the ID without committing
                customer_id = new_customer.id
                customer_created = True
                customer_data = new_customer.to_dict()

    vehicle_data['customer_id'] = customer_id

    # Step 4: Check if vehicle already exists
    existing_vehicle = Vehicle.query.filter_by(registration=registration).first()
    if existing_vehicle:
        # Update existing vehicle with new data (DVLA data takes precedence)
        try:
            existing_vehicle.make = vehicle_data.get('make') or existing_vehicle.make
            existing_vehicle.model = vehicle_data.get('model') or existing_vehicle.model
            existing_vehicle.color = vehicle_data.get('color') or existing_vehicle.color
            existing_vehicle.year = vehicle_data.get('year') or existing_vehicle.year
            existing_vehicle.mot_expiry = vehicle_data.get('mot_expiry') or existing_vehicle.mot_expiry

            # Update customer if provided
            if vehicle_data.get('customer_id'):
                existing_vehicle.customer_id = vehicle_data.get('customer_id')

            db.session.commit()

            return {
                'success': True,
                'vehicle': existing_vehicle.to_dict(),
                'customer': customer_data,
                'customer_created': customer_created,
                'registration': registration,
                'dvla_found': dvla_found,
                'dvla_data': dvla_data if dvla_found else None,
                'csv_data': row_data,
                'action': 'updated'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to update existing vehicle {registration}: {str(e)}'
            }

    # Step 5: Create new vehicle
    try:
        vehicle = Vehicle(
            registration=vehicle_data['registration'],
            make=vehicle_data.get('make'),
            model=vehicle_data.get('model'),
            color=vehicle_data.get('color'),
            year=vehicle_data.get('year'),
            mot_expiry=vehicle_data.get('mot_expiry'),
            customer_id=vehicle_data.get('customer_id')
        )

        db.session.add(vehicle)
        db.session.commit()

        return {
            'success': True,
            'vehicle': vehicle.to_dict(),
            'customer': customer_data,
            'customer_created': customer_created,
            'registration': registration,
            'dvla_found': dvla_found,
            'dvla_data': dvla_data if dvla_found else None,
            'csv_data': row_data,
            'action': 'created'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Failed to create vehicle {registration}: {str(e)}'
        }

@vehicle_bp.route('/dvla-batch-status', methods=['GET'])
def get_batch_status():
    """Get the status of the current batch DVLA verification process"""
    from services.batch_dvla_service import BatchDVLAService

    batch_service = BatchDVLAService()
    status = batch_service.get_status()
    return jsonify(status)

@vehicle_bp.route('/dvla-batch-start', methods=['POST'])
def start_batch_dvla_verification():
    """Start batch DVLA verification for all vehicles"""
    from services.batch_dvla_service import BatchDVLAService

    data = request.get_json() or {}
    verification_type = data.get('type', 'all')  # 'all', 'missing_mot', 'unverified'

    batch_service = BatchDVLAService()
    result = batch_service.start_batch_verification(verification_type)

    return jsonify(result)

@vehicle_bp.route('/dvla-batch-stop', methods=['POST'])
def stop_batch_dvla_verification():
    """Stop the current batch DVLA verification process"""
    from services.batch_dvla_service import BatchDVLAService

    batch_service = BatchDVLAService()
    result = batch_service.stop_batch_verification()

    return jsonify(result)

@vehicle_bp.route('/dvla-lookup-all', methods=['POST'])
def dvla_lookup_all_vehicles():
    """Legacy endpoint - redirects to new batch system"""
    from services.batch_dvla_service import BatchDVLAService

    batch_service = BatchDVLAService()
    result = batch_service.start_batch_verification('all')

    return jsonify(result)

@vehicle_bp.route('/count', methods=['GET'])
def get_vehicle_count():
    """Get count of vehicles for different verification types"""
    verification_type = request.args.get('type', 'all')

    try:
        if verification_type == 'all':
            count = Vehicle.query.count()
        elif verification_type == 'missing_mot':
            count = Vehicle.query.filter(
                (Vehicle.mot_expiry.is_(None)) |
                (Vehicle.mot_expiry == '')
            ).count()
        elif verification_type == 'unverified':
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            count = Vehicle.query.filter(
                (Vehicle.dvla_verified_at.is_(None)) |
                (Vehicle.dvla_verified_at < cutoff_date)
            ).count()
        elif verification_type == 'job_sheets':
            # Count unique registrations from job sheets not in vehicles table
            from models.job_sheet import JobSheet
            unique_regs = db.session.query(JobSheet.vehicle_reg).filter(
                JobSheet.vehicle_reg.isnot(None),
                JobSheet.vehicle_reg != ''
            ).distinct().all()

            count = 0
            for (reg,) in unique_regs:
                if reg and not Vehicle.query.filter_by(registration=reg.upper()).first():
                    count += 1
        else:
            count = 0

        return jsonify({'count': count})

    except Exception as e:
        return jsonify({'error': str(e), 'count': 0}), 500

@vehicle_bp.route('/clear-all', methods=['POST'])
def clear_all_vehicles():
    """Clear all vehicles from the database"""
    try:
        # Get count before deletion
        vehicle_count = Vehicle.query.count()

        # Also clear related reminders first to avoid foreign key issues
        from models.reminder import Reminder
        reminder_count = Reminder.query.count()
        Reminder.query.delete()

        # Delete all vehicles
        Vehicle.query.delete()
        db.session.commit()

        return jsonify({
            'message': f'Successfully cleared {vehicle_count} vehicles and {reminder_count} related reminders',
            'cleared_vehicles': vehicle_count,
            'cleared_reminders': reminder_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to clear vehicles: {str(e)}'
        }), 500

@vehicle_bp.route('/<int:id>/details', methods=['GET'])
def get_vehicle_details(id):
    """Get detailed vehicle information including DVLA data, customer details, and reminders"""
    try:
        vehicle = Vehicle.query.get_or_404(id)

        # Get customer details if associated
        customer_data = None
        if vehicle.customer_id:
            from models.customer import Customer
            customer = Customer.query.get(vehicle.customer_id)
            if customer:
                customer_data = {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone
                }

        # Get DVLA data for this vehicle
        dvla_data = None
        try:
            dvla_service = DVLAApiService()
            dvla_response = dvla_service.get_vehicle_details(vehicle.registration)
            if dvla_response:
                dvla_data = {
                    'make': dvla_response.get('make'),
                    'model': dvla_response.get('model'),
                    'colour': dvla_response.get('primaryColour'),
                    'year': dvla_response.get('yearOfManufacture'),
                    'fuel_type': dvla_response.get('fuelType'),
                    'engine_capacity': dvla_response.get('engineCapacity'),
                    'co2_emissions': dvla_response.get('co2Emissions'),
                    'mot_expiry': dvla_response.get('motExpiryDate'),
                    'mot_status': dvla_response.get('motStatus'),
                    'mot_test_date': dvla_response.get('motTestDate'),
                    'mot_test_number': dvla_response.get('motTestNumber'),
                    'mot_test_mileage': dvla_response.get('motTestMileage'),
                    'first_used_date': dvla_response.get('firstUsedDate'),
                    'dvla_id': dvla_response.get('dvlaId'),
                    'mot_defects': dvla_response.get('motDefects', [])
                }
        except Exception as e:
            print(f"Error fetching DVLA data: {e}")
            dvla_data = None

        # Get all reminders for this vehicle
        from models.reminder import Reminder
        reminders = Reminder.query.filter_by(vehicle_id=vehicle.id).all()
        reminders_data = []
        for reminder in reminders:
            reminder_dict = {
                'id': reminder.id,
                'reminder_date': reminder.reminder_date.strftime('%d-%m-%Y') if reminder.reminder_date else None,
                'status': reminder.status,
                'created_at': reminder.created_at.strftime('%d-%m-%Y %H:%M') if reminder.created_at else None,
                'sent_at': reminder.sent_at.strftime('%d-%m-%Y %H:%M') if reminder.sent_at else None
            }
            reminders_data.append(reminder_dict)

        # Format vehicle data with proper date formatting
        vehicle_data = {
            'id': vehicle.id,
            'registration': vehicle.registration,
            'make': vehicle.make,
            'model': vehicle.model,
            'color': vehicle.color,
            'year': vehicle.year,
            'mot_expiry': vehicle.mot_expiry.strftime('%d-%m-%Y') if vehicle.mot_expiry else None,
            'customer_id': vehicle.customer_id,
            'created_at': vehicle.created_at.strftime('%d-%m-%Y %H:%M') if vehicle.created_at else None,
            'updated_at': vehicle.updated_at.strftime('%d-%m-%Y %H:%M') if vehicle.updated_at else None
        }

        return jsonify({
            'vehicle': vehicle_data,
            'customer': customer_data,
            'dvla_data': dvla_data,
            'reminders': reminders_data
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to get vehicle details: {str(e)}'
        }), 500
