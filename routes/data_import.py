from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import csv
import json
import pandas as pd
from datetime import datetime, date
import os
import tempfile
from database import db
from models.customer import Customer
from models.vehicle import Vehicle
from models.reminder import Reminder

# Create data import blueprint
data_import_bp = Blueprint('data_import', __name__, url_prefix='/api/import')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_str):
    """Parse various date formats"""
    if not date_str or date_str.strip() == '':
        return None
    
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d.%m.%Y',
        '%Y.%m.%d'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None

@data_import_bp.route('/upload', methods=['POST'])
def upload_data():
    """Handle file upload and data import"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Supported: CSV, Excel, JSON, TXT'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        # Process the file based on extension
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            result = process_csv_file(filepath)
        elif file_ext in ['xlsx', 'xls']:
            result = process_excel_file(filepath)
        elif file_ext == 'json':
            result = process_json_file(filepath)
        elif file_ext == 'txt':
            result = process_text_file(filepath)
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported file format'
            }), 400
        
        # Clean up temporary file
        os.remove(filepath)
        os.rmdir(temp_dir)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

def process_csv_file(filepath):
    """Process CSV file and import data"""
    customers_added = 0
    vehicles_added = 0
    reminders_added = 0
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Process each row
                    result = process_data_row(row)
                    customers_added += result['customers']
                    vehicles_added += result['vehicles']
                    reminders_added += result['reminders']
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Data imported successfully',
            'stats': {
                'customers_added': customers_added,
                'vehicles_added': vehicles_added,
                'reminders_added': reminders_added,
                'errors': errors
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'CSV processing failed: {str(e)}'
        }

def process_excel_file(filepath):
    """Process Excel file and import data"""
    try:
        # Read Excel file
        df = pd.read_excel(filepath)
        
        customers_added = 0
        vehicles_added = 0
        reminders_added = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Convert pandas Series to dict
                row_dict = row.to_dict()
                
                # Process each row
                result = process_data_row(row_dict)
                customers_added += result['customers']
                vehicles_added += result['vehicles']
                reminders_added += result['reminders']
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Excel data imported successfully',
            'stats': {
                'customers_added': customers_added,
                'vehicles_added': vehicles_added,
                'reminders_added': reminders_added,
                'errors': errors
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Excel processing failed: {str(e)}'
        }

def process_json_file(filepath):
    """Process JSON file and import data"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        customers_added = 0
        vehicles_added = 0
        reminders_added = 0
        errors = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of objects
            for index, item in enumerate(data):
                try:
                    result = process_data_row(item)
                    customers_added += result['customers']
                    vehicles_added += result['vehicles']
                    reminders_added += result['reminders']
                except Exception as e:
                    errors.append(f"Item {index + 1}: {str(e)}")
        
        elif isinstance(data, dict):
            # Single object or nested structure
            if 'customers' in data or 'vehicles' in data:
                # Structured data
                if 'customers' in data:
                    for index, customer in enumerate(data['customers']):
                        try:
                            result = process_customer_data(customer)
                            customers_added += result['customers']
                        except Exception as e:
                            errors.append(f"Customer {index + 1}: {str(e)}")
                
                if 'vehicles' in data:
                    for index, vehicle in enumerate(data['vehicles']):
                        try:
                            result = process_vehicle_data(vehicle)
                            vehicles_added += result['vehicles']
                        except Exception as e:
                            errors.append(f"Vehicle {index + 1}: {str(e)}")
            else:
                # Single record
                result = process_data_row(data)
                customers_added += result['customers']
                vehicles_added += result['vehicles']
                reminders_added += result['reminders']
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'JSON data imported successfully',
            'stats': {
                'customers_added': customers_added,
                'vehicles_added': vehicles_added,
                'reminders_added': reminders_added,
                'errors': errors
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'JSON processing failed: {str(e)}'
        }

def process_text_file(filepath):
    """Process text file (assume CSV-like format)"""
    try:
        # Try to process as CSV first
        return process_csv_file(filepath)
    except:
        # If CSV fails, try line-by-line processing
        customers_added = 0
        vehicles_added = 0
        errors = []
        
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line_num, line in enumerate(lines, start=1):
            try:
                # Try to parse line as comma-separated values
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:  # Minimum required fields
                    row_dict = {
                        'name': parts[0] if len(parts) > 0 else '',
                        'email': parts[1] if len(parts) > 1 else '',
                        'phone': parts[2] if len(parts) > 2 else '',
                        'registration': parts[3] if len(parts) > 3 else '',
                        'make': parts[4] if len(parts) > 4 else '',
                        'model': parts[5] if len(parts) > 5 else '',
                        'mot_due': parts[6] if len(parts) > 6 else ''
                    }
                    
                    result = process_data_row(row_dict)
                    customers_added += result['customers']
                    vehicles_added += result['vehicles']
                    
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Text data imported successfully',
            'stats': {
                'customers_added': customers_added,
                'vehicles_added': vehicles_added,
                'reminders_added': 0,
                'errors': errors
            }
        }

def process_data_row(row):
    """Process a single data row and create customer/vehicle records"""
    customers_added = 0
    vehicles_added = 0
    reminders_added = 0
    
    # Normalize column names (handle various naming conventions)
    normalized_row = {}
    for key, value in row.items():
        if pd.isna(value):
            value = ''
        normalized_key = str(key).lower().strip()
        normalized_row[normalized_key] = str(value).strip() if value else ''
    
    # Extract customer information
    customer_data = extract_customer_data(normalized_row)
    vehicle_data = extract_vehicle_data(normalized_row)
    
    # Create or find customer
    customer = None
    if customer_data['email'] or customer_data['name']:
        customer = Customer.query.filter_by(email=customer_data['email']).first()
        
        if not customer and customer_data['name']:
            customer = Customer.query.filter_by(name=customer_data['name']).first()
        
        if not customer:
            customer = Customer(
                name=customer_data['name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                account=customer_data['account']
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID
            customers_added = 1
    
    # Create vehicle if registration is provided
    if vehicle_data['registration'] and customer:
        vehicle = Vehicle.query.filter_by(registration=vehicle_data['registration']).first()
        
        if not vehicle:
            vehicle = Vehicle(
                registration=vehicle_data['registration'],
                make=vehicle_data['make'],
                model=vehicle_data['model'],
                year=vehicle_data['year'],
                mot_expiry=vehicle_data['mot_expiry'],
                customer_id=customer.id
            )
            db.session.add(vehicle)
            db.session.flush()
            vehicles_added = 1
            
            # Create reminder if MOT expiry date is provided
            if vehicle_data['mot_expiry']:
                reminder = Reminder(
                    vehicle_id=vehicle.id,
                    reminder_date=vehicle_data['mot_expiry'],
                    status='scheduled'
                )
                db.session.add(reminder)
                reminders_added = 1
    
    return {
        'customers': customers_added,
        'vehicles': vehicles_added,
        'reminders': reminders_added
    }

def extract_customer_data(row):
    """Extract customer data from normalized row"""
    customer_data = {
        'name': '',
        'email': '',
        'phone': '',
        'account': ''
    }
    
    # Map various column names to customer fields
    name_fields = ['name', 'customer_name', 'full_name', 'customer', 'client_name']
    email_fields = ['email', 'email_address', 'customer_email', 'e_mail']
    phone_fields = ['phone', 'telephone', 'mobile', 'phone_number', 'contact_number']
    account_fields = ['account', 'customer_account', 'account_number', 'customer_id', 'address']
    
    for field in name_fields:
        if field in row and row[field]:
            customer_data['name'] = row[field]
            break
    
    for field in email_fields:
        if field in row and row[field]:
            customer_data['email'] = row[field]
            break
    
    for field in phone_fields:
        if field in row and row[field]:
            customer_data['phone'] = row[field]
            break
    
    for field in account_fields:
        if field in row and row[field]:
            customer_data['account'] = row[field]
            break
    
    return customer_data

def extract_vehicle_data(row):
    """Extract vehicle data from normalized row"""
    vehicle_data = {
        'registration': '',
        'make': '',
        'model': '',
        'year': None,
        'mot_expiry': None
    }
    
    # Map various column names to vehicle fields
    reg_fields = ['registration', 'reg', 'vehicle_registration', 'number_plate', 'plate']
    make_fields = ['make', 'vehicle_make', 'manufacturer', 'brand']
    model_fields = ['model', 'vehicle_model', 'car_model']
    year_fields = ['year', 'vehicle_year', 'manufacture_year', 'model_year']
    mot_fields = ['mot_due', 'mot_due_date', 'mot_expiry', 'mot_expires', 'due_date']
    
    for field in reg_fields:
        if field in row and row[field]:
            vehicle_data['registration'] = row[field].upper()
            break
    
    for field in make_fields:
        if field in row and row[field]:
            vehicle_data['make'] = row[field]
            break
    
    for field in model_fields:
        if field in row and row[field]:
            vehicle_data['model'] = row[field]
            break
    
    for field in year_fields:
        if field in row and row[field]:
            try:
                vehicle_data['year'] = int(row[field])
            except ValueError:
                pass
            break
    
    for field in mot_fields:
        if field in row and row[field]:
            vehicle_data['mot_expiry'] = parse_date(row[field])
            break
    
    return vehicle_data

def process_customer_data(customer_data):
    """Process individual customer data"""
    customer = Customer(
        name=customer_data.get('name', ''),
        email=customer_data.get('email', ''),
        phone=customer_data.get('phone', ''),
        account=customer_data.get('account', '')
    )
    db.session.add(customer)
    return {'customers': 1}

def process_vehicle_data(vehicle_data):
    """Process individual vehicle data"""
    vehicle = Vehicle(
        registration=vehicle_data.get('registration', '').upper(),
        make=vehicle_data.get('make', ''),
        model=vehicle_data.get('model', ''),
        year=vehicle_data.get('year'),
        mot_expiry=parse_date(vehicle_data.get('mot_expiry', ''))
    )
    db.session.add(vehicle)
    return {'vehicles': 1}

@data_import_bp.route('/sample-data', methods=['POST'])
def import_sample_data():
    """Import sample data for testing"""
    try:
        sample_customers = [
            {
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '01234 567890',
                'account': 'CUST001'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@email.com',
                'phone': '01234 567891',
                'account': 'CUST002'
            },
            {
                'name': 'Mike Wilson',
                'email': 'mike.wilson@email.com',
                'phone': '01234 567892',
                'account': 'CUST003'
            }
        ]
        
        sample_vehicles = [
            {
                'registration': 'AB12 CDE',
                'make': 'Ford',
                'model': 'Focus',
                'year': 2018,
                'mot_expiry': '2024-08-15',
                'customer_email': 'john.smith@email.com'
            },
            {
                'registration': 'FG34 HIJ',
                'make': 'Volkswagen',
                'model': 'Golf',
                'year': 2019,
                'mot_expiry': '2024-09-22',
                'customer_email': 'sarah.johnson@email.com'
            },
            {
                'registration': 'KL56 MNO',
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2020,
                'mot_expiry': '2024-07-10',
                'customer_email': 'mike.wilson@email.com'
            }
        ]
        
        customers_added = 0
        vehicles_added = 0
        reminders_added = 0
        
        # Add customers
        for customer_data in sample_customers:
            existing_customer = Customer.query.filter_by(email=customer_data['email']).first()
            if not existing_customer:
                customer = Customer(**customer_data)
                db.session.add(customer)
                customers_added += 1
        
        db.session.flush()
        
        # Add vehicles
        for vehicle_data in sample_vehicles:
            customer_email = vehicle_data.pop('customer_email')
            customer = Customer.query.filter_by(email=customer_email).first()
            
            if customer:
                existing_vehicle = Vehicle.query.filter_by(registration=vehicle_data['registration']).first()
                if not existing_vehicle:
                    vehicle_data['mot_expiry'] = parse_date(vehicle_data['mot_expiry'])
                    vehicle_data['customer_id'] = customer.id
                    vehicle = Vehicle(**vehicle_data)
                    db.session.add(vehicle)
                    db.session.flush()  # Get the vehicle ID
                    vehicles_added += 1
                    
                    # Add reminder
                    if vehicle_data['mot_expiry']:
                        reminder = Reminder(
                            vehicle_id=vehicle.id,
                            reminder_date=vehicle_data['mot_expiry'],
                            status='scheduled'
                        )
                        db.session.add(reminder)
                        reminders_added += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sample data imported successfully',
            'stats': {
                'customers_added': customers_added,
                'vehicles_added': vehicles_added,
                'reminders_added': reminders_added
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Sample data import failed: {str(e)}'
        }), 500

@data_import_bp.route('/template', methods=['GET'])
def download_template():
    """Provide CSV template for data import"""
    template_data = {
        'template': {
            'csv_headers': [
                'name',
                'email', 
                'phone',
                'address',
                'registration',
                'make',
                'model',
                'year',
                'mot_due_date'
            ],
            'sample_row': [
                'John Smith',
                'john.smith@email.com',
                '01234 567890',
                '123 Main Street, London, SW1A 1AA',
                'AB12 CDE',
                'Ford',
                'Focus',
                '2018',
                '2024-08-15'
            ]
        },
        'instructions': {
            'date_format': 'Use YYYY-MM-DD format for dates (e.g., 2024-08-15)',
            'registration': 'Use UK format (e.g., AB12 CDE)',
            'required_fields': ['name', 'registration'],
            'optional_fields': ['email', 'phone', 'address', 'make', 'model', 'year', 'mot_due_date']
        }
    }
    
    return jsonify(template_data)

