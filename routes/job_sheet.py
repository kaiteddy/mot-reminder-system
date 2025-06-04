from flask import Blueprint, request, jsonify
from database import db
from models.job_sheet import JobSheet
from models.customer import Customer
from models.vehicle import Vehicle
from datetime import datetime, date
import csv
import io
from decimal import Decimal, InvalidOperation
import pandas as pd

job_sheet_bp = Blueprint('job_sheet', __name__)

@job_sheet_bp.route('/', methods=['GET'])
def get_job_sheets():
    """Get all job sheets with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Optional filters
    customer_name = request.args.get('customer_name')
    vehicle_reg = request.args.get('vehicle_reg')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    doc_type = request.args.get('doc_type')

    query = JobSheet.query

    # Apply filters
    if customer_name:
        query = query.filter(JobSheet.customer_name.ilike(f'%{customer_name}%'))
    if vehicle_reg:
        query = query.filter(JobSheet.vehicle_reg.ilike(f'%{vehicle_reg}%'))
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(JobSheet.date_created >= date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(JobSheet.date_created <= date_to_obj)
        except ValueError:
            pass
    if doc_type:
        query = query.filter(JobSheet.doc_type == doc_type)

    # Order by date created (newest first)
    query = query.order_by(JobSheet.date_created.desc())

    # Paginate
    job_sheets = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'job_sheets': [js.to_dict() for js in job_sheets.items],
        'total': job_sheets.total,
        'pages': job_sheets.pages,
        'current_page': page,
        'per_page': per_page
    })

@job_sheet_bp.route('/<int:job_sheet_id>', methods=['GET'])
def get_job_sheet(job_sheet_id):
    """Get a specific job sheet"""
    job_sheet = JobSheet.query.get_or_404(job_sheet_id)
    return jsonify(job_sheet.to_dict())

@job_sheet_bp.route('/upload-bulk', methods=['POST'])
def upload_bulk_files():
    """Upload multiple files at once with intelligent processing"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    # Process files in optimal order
    results = {
        'total_files': len(files),
        'processed_files': 0,
        'customers_processed': 0,
        'vehicles_processed': 0,
        'job_sheets_processed': 0,
        'dvla_lookups': None,
        'errors': [],
        'file_results': []
    }

    try:
        # Categorize files by type
        customer_files = []
        vehicle_files = []
        job_sheet_files = []
        other_files = []

        for file in files:
            filename = file.filename.lower()
            if 'customer' in filename:
                customer_files.append(file)
            elif 'vehicle' in filename or 'mot_due' in filename:
                vehicle_files.append(file)
            elif any(keyword in filename for keyword in ['document', 'job', 'line_item', 'reminder']):
                job_sheet_files.append(file)
            else:
                other_files.append(file)

        # Process in order: customers -> vehicles -> job sheets -> others
        all_files_ordered = customer_files + vehicle_files + job_sheet_files + other_files

        for file in all_files_ordered:
            try:
                file_result = process_single_file(file)
                results['file_results'].append(file_result)
                results['processed_files'] += 1

                # Update counters based on file type
                if file_result.get('type') == 'customers':
                    results['customers_processed'] += file_result.get('processed', 0)
                elif file_result.get('type') == 'vehicles':
                    results['vehicles_processed'] += file_result.get('processed', 0)
                elif file_result.get('type') == 'job_sheets':
                    results['job_sheets_processed'] += file_result.get('processed', 0)

            except Exception as e:
                error_msg = f"Error processing {file.filename}: {str(e)}"
                results['errors'].append(error_msg)
                print(error_msg)

        # Perform DVLA lookup if requested
        auto_dvla = request.form.get('auto_dvla_lookup', 'true').lower() == 'true'
        if auto_dvla and (results['vehicles_processed'] > 0 or results['job_sheets_processed'] > 0):
            try:
                dvla_results = trigger_dvla_lookup_for_job_sheets()
                results['dvla_lookups'] = dvla_results
            except Exception as e:
                results['errors'].append(f"DVLA lookup error: {str(e)}")

        # Perform data linking if requested
        auto_link = request.form.get('auto_link_data', 'true').lower() == 'true'
        if auto_link:
            try:
                link_results = perform_data_linking()
                results['linking_results'] = link_results
            except Exception as e:
                results['errors'].append(f"Data linking error: {str(e)}")

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Failed to process files: {str(e)}'}), 500

def process_single_file(file):
    """Process a single file and determine its type"""
    filename = file.filename.lower()

    # Handle Excel files differently from CSV files
    if filename.endswith(('.xlsx', '.xls')):
        # For Excel files, pass the file object directly
        file_content = None
        file.seek(0)  # Reset file pointer
    else:
        # For CSV files, read as text
        try:
            file_content = file.read().decode('utf-8')
            file.seek(0)  # Reset file pointer
        except UnicodeDecodeError:
            # Try different encodings
            file.seek(0)
            try:
                file_content = file.read().decode('latin-1')
                file.seek(0)
            except UnicodeDecodeError:
                file.seek(0)
                file_content = file.read().decode('cp1252')
                file.seek(0)

    # Determine file type based on filename and content
    if 'customer' in filename:
        return process_customer_file(file, file_content)
    elif 'vehicle' in filename or 'mot_due' in filename:
        return process_vehicle_file(file, file_content)
    else:
        # Default to job sheet processing
        return process_job_sheet_file(file, file_content)

def process_customer_file(file, file_content):
    """Process customer data file"""
    try:
        # Handle Excel files
        if file.filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            rows = df.to_dict('records')
        else:
            # Handle CSV files
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)

        processed = 0
        created = 0
        updated = 0

        for row in rows:
            # Process customer row (simplified)
            processed += 1
            # Add customer processing logic here

        return {
            'filename': file.filename,
            'type': 'customers',
            'processed': processed,
            'created': created,
            'updated': updated,
            'success': True
        }
    except Exception as e:
        return {
            'filename': file.filename,
            'type': 'customers',
            'success': False,
            'error': str(e)
        }

def process_vehicle_file(file, file_content):
    """Process vehicle data file"""
    try:
        # Handle Excel files
        if file.filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            rows = df.to_dict('records')
        else:
            # Handle CSV files
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)

        processed = 0
        created = 0
        updated = 0

        for row in rows:
            # Process vehicle row (simplified)
            processed += 1
            # Add vehicle processing logic here

        return {
            'filename': file.filename,
            'type': 'vehicles',
            'processed': processed,
            'created': created,
            'updated': updated,
            'success': True
        }
    except Exception as e:
        return {
            'filename': file.filename,
            'type': 'vehicles',
            'success': False,
            'error': str(e)
        }

def process_job_sheet_file(file, file_content):
    """Process job sheet data file with comprehensive relationship handling"""
    try:
        # Handle Excel files
        if file.filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            rows = df.to_dict('records')
        else:
            # Handle CSV files
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)

        processed = 0
        created = 0
        updated = 0
        customers_created = 0
        vehicles_created = 0

        # Debug: Print column names for the first row
        if rows:
            print(f"Available columns in {file.filename}: {list(rows[0].keys())}")

        for row in rows:
            try:
                result = process_job_sheet_row_comprehensive(row)
                processed += 1
                if result['action'] == 'created':
                    created += 1
                elif result['action'] == 'updated':
                    updated += 1

                if result.get('customer_created'):
                    customers_created += 1
                if result.get('vehicle_created'):
                    vehicles_created += 1

            except Exception as e:
                print(f"Error processing job sheet row: {e}")
                print(f"Row data keys: {list(row.keys()) if row else 'No row data'}")

        return {
            'filename': file.filename,
            'type': 'job_sheets',
            'processed': processed,
            'created': created,
            'updated': updated,
            'customers_created': customers_created,
            'vehicles_created': vehicles_created,
            'success': True
        }
    except Exception as e:
        return {
            'filename': file.filename,
            'type': 'job_sheets',
            'success': False,
            'error': str(e)
        }

def perform_data_linking():
    """Link all data together"""
    # Implementation for linking customers, vehicles, and job sheets
    return {
        'customers_linked': 0,
        'vehicles_linked': 0,
        'job_sheets_linked': 0
    }

@job_sheet_bp.route('/upload', methods=['POST'])
def upload_job_sheets():
    """Upload job sheets from CSV/Excel file (single file)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Handle Excel files
        if file.filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            rows = df.to_dict('records')
        else:
            # Handle CSV files
            try:
                file_content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                try:
                    file_content = file.read().decode('latin-1')
                except UnicodeDecodeError:
                    file.seek(0)
                    file_content = file.read().decode('cp1252')

            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)

        results = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': [],
            'linked_customers': 0,
            'linked_vehicles': 0
        }

        # Debug: Print column names for the first row
        if rows:
            print(f"Available columns in uploaded file: {list(rows[0].keys())}")
            print(f"First row sample data: {dict(list(rows[0].items())[:5])}")

            # Test field mapping on first row
            print("=== FIELD MAPPING TEST ===")
            test_row = rows[0]
            field_mapping = {
                'customer_name': ['Customer Name', 'customer_name', 'Customer', 'Name', 'Client Name'],
                'vehicle_reg': ['Vehicle Reg', 'vehicle_reg', 'Registration', 'Reg', 'Plate', 'Number Plate'],
                'make': ['Make', 'vehicle_make', 'Vehicle Make', 'Manufacturer'],
                'grand_total': ['Grand Total', 'total_gross', 'Total', 'Amount', 'Final Total'],
                'doc_no': ['Doc No', 'doc_number', 'Document Number', 'Number', 'Job Number']
            }

            for field_name, possible_names in field_mapping.items():
                found_col = None
                for col_name in possible_names:
                    if col_name in test_row:
                        found_col = col_name
                        break
                print(f"  {field_name}: {found_col} -> '{test_row.get(found_col, 'NOT_FOUND')}'")
            print("=== END FIELD MAPPING TEST ===")

        for row_num, row in enumerate(rows, start=2):
            try:
                result = process_job_sheet_row(row)
                results['processed'] += 1

                if result['action'] == 'created':
                    results['created'] += 1
                elif result['action'] == 'updated':
                    results['updated'] += 1

                if result.get('customer_linked'):
                    results['linked_customers'] += 1
                if result.get('vehicle_linked'):
                    results['linked_vehicles'] += 1

            except Exception as e:
                error_msg = f"Row {row_num}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"Error processing row {row_num}: {e}")
                print(f"Row data keys: {list(row.keys()) if row else 'No row data'}")

        # After processing, trigger DVLA lookup for all new vehicles
        if results['created'] > 0 or results['updated'] > 0:
            try:
                dvla_results = trigger_dvla_lookup_for_job_sheets()
                results['dvla_lookups'] = dvla_results
            except Exception as e:
                print(f"Error during DVLA lookup: {e}")
                results['dvla_error'] = str(e)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

def trigger_dvla_lookup_for_job_sheets():
    """Trigger DVLA lookup for all vehicles from job sheets that aren't in the vehicles table"""
    from models.vehicle import Vehicle
    from routes.vehicle import lookup_vehicle_dvla

    # Get all unique vehicle registrations from job sheets
    unique_regs = db.session.query(JobSheet.vehicle_reg).filter(
        JobSheet.vehicle_reg.isnot(None),
        JobSheet.vehicle_reg != ''
    ).distinct().all()

    dvla_results = {
        'checked': 0,
        'found': 0,
        'created': 0,
        'updated': 0,
        'errors': []
    }

    for (reg,) in unique_regs:
        if not reg:
            continue

        try:
            dvla_results['checked'] += 1

            # Check if vehicle already exists
            existing_vehicle = Vehicle.query.filter_by(registration=reg.upper()).first()

            if not existing_vehicle:
                # Try to get DVLA data and create vehicle
                dvla_data = lookup_vehicle_dvla(reg)

                if dvla_data and dvla_data.get('registrationNumber'):
                    dvla_results['found'] += 1

                    # Create new vehicle with DVLA data
                    new_vehicle = Vehicle(
                        registration=dvla_data['registrationNumber'].upper(),
                        make=dvla_data.get('make'),
                        model=dvla_data.get('model'),
                        color=dvla_data.get('primaryColour'),
                        year=int(dvla_data.get('yearOfManufacture')) if dvla_data.get('yearOfManufacture') else None,
                        mot_expiry=datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date() if dvla_data.get('motExpiryDate') else None
                    )

                    db.session.add(new_vehicle)
                    db.session.commit()
                    dvla_results['created'] += 1

                    # Update job sheet linking
                    job_sheets = JobSheet.query.filter_by(vehicle_reg=reg.upper()).all()
                    for js in job_sheets:
                        js.linked_vehicle_id = new_vehicle.id
                    db.session.commit()

            else:
                # Update existing vehicle with DVLA data if MOT expiry is missing
                if not existing_vehicle.mot_expiry:
                    dvla_data = lookup_vehicle_dvla(reg)

                    if dvla_data and dvla_data.get('motExpiryDate'):
                        dvla_results['found'] += 1
                        existing_vehicle.mot_expiry = datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date()

                        # Update other fields if missing
                        if not existing_vehicle.make and dvla_data.get('make'):
                            existing_vehicle.make = dvla_data['make']
                        if not existing_vehicle.model and dvla_data.get('model'):
                            existing_vehicle.model = dvla_data['model']
                        if not existing_vehicle.color and dvla_data.get('primaryColour'):
                            existing_vehicle.color = dvla_data['primaryColour']
                        if not existing_vehicle.year and dvla_data.get('yearOfManufacture'):
                            existing_vehicle.year = int(dvla_data['yearOfManufacture'])

                        db.session.commit()
                        dvla_results['updated'] += 1

                # Link job sheets to existing vehicle
                job_sheets = JobSheet.query.filter(
                    JobSheet.vehicle_reg == reg.upper(),
                    JobSheet.linked_vehicle_id.is_(None)
                ).all()
                for js in job_sheets:
                    js.linked_vehicle_id = existing_vehicle.id
                db.session.commit()

        except Exception as e:
            error_msg = f"Error processing {reg}: {str(e)}"
            dvla_results['errors'].append(error_msg)
            print(error_msg)

    return dvla_results

def process_job_sheet_row_comprehensive(row_data):
    """Process a single job sheet row with comprehensive customer/vehicle handling"""

    # Field mapping for flexible column names
    def get_field_value(row, possible_names, default=''):
        """Get field value by trying multiple possible column names"""
        import pandas as pd
        for name in possible_names:
            if name in row and row[name] is not None:
                # Handle pandas NaN values
                if pd.isna(row[name]):
                    continue
                value = str(row[name]).strip()
                if value and value.lower() not in ['nan', 'none', '', 'null']:
                    return value
        return default

    # Extract customer information - PRESERVE EXISTING IDs
    customer_created = False
    customer_account = get_field_value(row_data, ['customer_account', 'Customer Account', 'ID Customer'])
    customer_name = get_field_value(row_data, ['customer_name', 'Customer Name', 'Customer', 'Name'])

    linked_customer_id = None
    if customer_account:
        # Try to find existing customer by their EXISTING account ID
        existing_customer = Customer.query.filter_by(account=customer_account).first()

        if not existing_customer and customer_name:
            # Create new customer with the EXISTING account ID from the file
            new_customer = Customer(
                account=customer_account,  # Use the exact ID from the file
                name=customer_name,
                address=get_field_value(row_data, ['customer_address', 'Customer Address', 'Address']),
                contact_number=get_field_value(row_data, ['contact_number', 'Contact Number', 'Phone']),
                email=get_field_value(row_data, ['email', 'Email', 'customer_email']),
                postcode=get_field_value(row_data, ['postcode', 'Postcode', 'Post Code'])
            )
            db.session.add(new_customer)
            db.session.flush()  # Get the ID
            linked_customer_id = new_customer.id
            customer_created = True
            print(f"Created new customer: {customer_name} (Account: {customer_account}, DB ID: {linked_customer_id})")
        elif existing_customer:
            linked_customer_id = existing_customer.id
            print(f"Found existing customer: {customer_name} (Account: {customer_account}, DB ID: {linked_customer_id})")
    elif customer_name:
        # Fallback: try to find by name if no account ID
        existing_customer = Customer.query.filter(Customer.name.ilike(f"%{customer_name}%")).first()
        if existing_customer:
            linked_customer_id = existing_customer.id
            print(f"Found customer by name: {customer_name} (DB ID: {linked_customer_id})")

    # Next, ensure vehicle exists
    vehicle_created = False
    vehicle_reg = get_field_value(row_data, ['vehicle_reg', 'Vehicle Reg', 'Registration', 'Reg']).upper()
    linked_vehicle_id = None

    # Add parse_int function that was missing
    def parse_int(value_str):
        if not value_str or value_str.strip() == '':
            return None
        try:
            return int(float(str(value_str).strip()))
        except (ValueError, TypeError):
            return None

    if vehicle_reg:
        existing_vehicle = Vehicle.query.filter_by(registration=vehicle_reg).first()

        if not existing_vehicle:
            # Create new vehicle
            new_vehicle = Vehicle(
                registration=vehicle_reg,
                make=get_field_value(row_data, ['vehicle_make', 'Make', 'Vehicle Make']),
                model=get_field_value(row_data, ['vehicle_model', 'Model', 'Vehicle Model']),
                year=parse_int(get_field_value(row_data, ['year', 'Year', 'Model Year'])),
                color=get_field_value(row_data, ['color', 'Color', 'Colour']),
                customer_id=linked_customer_id
            )
            db.session.add(new_vehicle)
            db.session.flush()  # Get the ID
            linked_vehicle_id = new_vehicle.id
            vehicle_created = True
            print(f"Created new vehicle: {vehicle_reg} (ID: {linked_vehicle_id})")
        else:
            linked_vehicle_id = existing_vehicle.id
            # Update customer link if missing
            if not existing_vehicle.customer_id and linked_customer_id:
                existing_vehicle.customer_id = linked_customer_id

    # Now process the job sheet using the original logic but with proper relationships
    return process_job_sheet_row_original(row_data, linked_customer_id, linked_vehicle_id, customer_created, vehicle_created)

def process_job_sheet_row_original(row_data, linked_customer_id=None, linked_vehicle_id=None, customer_created=False, vehicle_created=False):
    """Original job sheet processing logic with relationship IDs"""

    # Field mapping for flexible column names
    def get_field_value(row, possible_names, default=''):
        """Get field value by trying multiple possible column names"""
        import pandas as pd
        for name in possible_names:
            if name in row and row[name] is not None:
                # Handle pandas NaN values
                if pd.isna(row[name]):
                    continue
                value = str(row[name]).strip()
                if value and value.lower() not in ['nan', 'none', '', 'null']:
                    return value
        return default

    # Parse dates
    def parse_date(date_str):
        if not date_str or date_str.strip() == '':
            return None
        try:
            # Try DD/MM/YYYY format first
            return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
        except ValueError:
            try:
                # Try YYYY-MM-DD format
                return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
            except ValueError:
                return None

    # Parse decimal values
    def parse_decimal(value_str):
        if not value_str or value_str.strip() == '':
            return Decimal('0')
        try:
            return Decimal(str(value_str).strip())
        except (InvalidOperation, ValueError):
            return Decimal('0')

    # Parse integer values
    def parse_int(value_str):
        if not value_str or value_str.strip() == '':
            return None
        try:
            return int(float(str(value_str).strip()))
        except (ValueError, TypeError):
            return None

    # Extract data from row with flexible field mapping - PRESERVE EXISTING IDs
    doc_id = get_field_value(row_data, ['id', 'ID Doc', 'Doc ID', 'Document ID', 'document_id'])
    if not doc_id:
        # Generate a unique doc_id if not provided
        import uuid
        doc_id = f"AUTO_{str(uuid.uuid4())[:8]}"

    # Check if job sheet already exists
    existing_job_sheet = JobSheet.query.filter_by(doc_id=doc_id).first()

    # Extract key fields with debug logging - Updated field mapping
    customer_name = get_field_value(row_data, ['customer_name', 'Customer Name', 'Customer', 'Name', 'Client Name'])
    vehicle_reg = get_field_value(row_data, ['vehicle_reg', 'Vehicle Reg', 'Registration', 'Reg', 'Plate', 'Number Plate'])
    make = get_field_value(row_data, ['vehicle_make', 'Make', 'Vehicle Make', 'Manufacturer'])

    # Debug: Print first few rows to see what's being extracted
    if doc_id.startswith('F22A5CD4') or doc_id.startswith('7E816AA1'):
        print(f"DEBUG - Doc ID: {doc_id}")
        print(f"DEBUG - Customer Name: '{customer_name}' (extracted successfully)")
        print(f"DEBUG - Vehicle Reg: '{vehicle_reg}' (extracted successfully)")
        print(f"DEBUG - Make: '{make}' (extracted successfully)")
        print(f"DEBUG - Available keys: {list(row_data.keys())[:10]}")

        # Show which columns were actually used
        customer_col = None
        for col in ['Customer Name', 'customer_name', 'Customer', 'Name', 'Client Name']:
            if col in row_data and row_data[col]:
                customer_col = col
                break
        print(f"DEBUG - Customer column used: {customer_col}")

        vehicle_col = None
        for col in ['Vehicle Reg', 'vehicle_reg', 'Registration', 'Reg', 'Plate', 'Number Plate']:
            if col in row_data and row_data[col]:
                vehicle_col = col
                break
        print(f"DEBUG - Vehicle Reg column used: {vehicle_col}")

        make_col = None
        for col in ['Make', 'vehicle_make', 'Vehicle Make', 'Manufacturer']:
            if col in row_data and row_data[col]:
                make_col = col
                break
        print(f"DEBUG - Make column used: {make_col}")

    # Prepare job sheet data with flexible field mapping - PRESERVE EXISTING IDs
    job_sheet_data = {
        'doc_id': doc_id,
        'doc_type': get_field_value(row_data, ['doc_type', 'Doc Type', 'Document Type', 'Type'], 'JS'),
        'doc_no': get_field_value(row_data, ['doc_number', 'Doc No', 'Document Number', 'Number', 'Job Number']),
        'date_created': parse_date(get_field_value(row_data, ['date_created', 'Date Created', 'Created Date', 'Date'])),
        'date_issued': parse_date(get_field_value(row_data, ['date_issued', 'Date Issued', 'Issued Date', 'Issue Date'])),
        'date_paid': parse_date(get_field_value(row_data, ['date_paid', 'Date Paid', 'Paid Date', 'Payment Date'])),
        'customer_id_external': get_field_value(row_data, ['customer_account', 'ID Customer', 'Customer ID', 'Customer']),
        'customer_name': customer_name,
        'customer_address': get_field_value(row_data, ['customer_address', 'Customer Address', 'Address', 'Customer Addr']),
        'contact_number': get_field_value(row_data, ['contact_number', 'Contact Number', 'Phone', 'Mobile', 'Contact', 'Phone Number']),
        'vehicle_id_external': get_field_value(row_data, ['ID Vehicle', 'Vehicle ID', 'Vehicle']),
        'vehicle_reg': vehicle_reg.upper() if vehicle_reg else '',
        'make': make,
        'model': get_field_value(row_data, ['vehicle_model', 'Model', 'Vehicle Model']),
        'vin': get_field_value(row_data, ['VIN', 'Chassis Number', 'Vehicle VIN']),
        'mileage': parse_int(get_field_value(row_data, ['Mileage', 'Miles', 'Odometer'])),
        'sub_labour_net': parse_decimal(get_field_value(row_data, ['labour_net', 'Sub Labour Net', 'Labour Net', 'Labor Net'])),
        'sub_labour_tax': parse_decimal(get_field_value(row_data, ['labour_tax', 'Sub Labour Tax', 'Labour Tax', 'Labor Tax'])),
        'sub_labour_gross': parse_decimal(get_field_value(row_data, ['labour_gross', 'Sub Labour Gross', 'Labour Gross', 'Labor Gross'])),
        'sub_parts_net': parse_decimal(get_field_value(row_data, ['parts_net', 'Sub Parts Net', 'Parts Net'])),
        'sub_parts_tax': parse_decimal(get_field_value(row_data, ['parts_tax', 'Sub Parts Tax', 'Parts Tax'])),
        'sub_parts_gross': parse_decimal(get_field_value(row_data, ['parts_gross', 'Sub Parts Gross', 'Parts Gross'])),
        'sub_mot_net': parse_decimal(get_field_value(row_data, ['mot_net', 'Sub MOT Net', 'MOT Net'])),
        'sub_mot_tax': parse_decimal(get_field_value(row_data, ['mot_tax', 'Sub MOT Tax', 'MOT Tax'])),
        'sub_mot_gross': parse_decimal(get_field_value(row_data, ['mot_gross', 'Sub MOT Gross', 'MOT Gross'])),
        'vat': parse_decimal(get_field_value(row_data, ['total_tax', 'VAT', 'Tax', 'Sales Tax'])),
        'grand_total': parse_decimal(get_field_value(row_data, ['total_gross', 'Grand Total', 'Total', 'Amount', 'Final Total'])),
        'job_description': get_field_value(row_data, ['Job Description', 'Description', 'Work Description', 'Notes'])
    }

    # Use the provided relationship IDs instead of trying to find them again
    job_sheet_data['linked_customer_id'] = linked_customer_id
    job_sheet_data['linked_vehicle_id'] = linked_vehicle_id

    if existing_job_sheet:
        # Update existing job sheet
        for key, value in job_sheet_data.items():
            if hasattr(existing_job_sheet, key):
                setattr(existing_job_sheet, key, value)

        existing_job_sheet.updated_at = datetime.utcnow()
        db.session.commit()

        return {
            'success': True,
            'action': 'updated',
            'job_sheet': existing_job_sheet.to_dict(),
            'customer_created': customer_created,
            'vehicle_created': vehicle_created,
            'customer_linked': linked_customer_id is not None,
            'vehicle_linked': linked_vehicle_id is not None
        }
    else:
        # Create new job sheet
        job_sheet = JobSheet(**job_sheet_data)
        db.session.add(job_sheet)
        db.session.commit()

        return {
            'success': True,
            'action': 'created',
            'job_sheet': job_sheet.to_dict(),
            'customer_created': customer_created,
            'vehicle_created': vehicle_created,
            'customer_linked': linked_customer_id is not None,
            'vehicle_linked': linked_vehicle_id is not None
        }

def process_job_sheet_row(row_data):
    """Process a single job sheet row from CSV - Legacy function"""
    return process_job_sheet_row_comprehensive(row_data)

@job_sheet_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for job sheets"""

    # Date range filter
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = JobSheet.query

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(JobSheet.date_created >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(JobSheet.date_created <= date_to_obj)
        except ValueError:
            pass

    job_sheets = query.all()

    # Calculate analytics
    total_jobs = len(job_sheets)
    total_revenue = sum(float(js.grand_total) for js in job_sheets if js.grand_total)
    paid_jobs = len([js for js in job_sheets if js.date_paid])
    unpaid_jobs = total_jobs - paid_jobs

    # MOT specific analytics
    mot_jobs = [js for js in job_sheets if js.is_mot_job()]
    mot_revenue = sum(float(js.sub_mot_gross) for js in mot_jobs if js.sub_mot_gross)

    # Customer analytics
    unique_customers = len(set(js.customer_name for js in job_sheets if js.customer_name))
    linked_customers = len([js for js in job_sheets if js.linked_customer_id])

    # Vehicle analytics
    unique_vehicles = len(set(js.vehicle_reg for js in job_sheets if js.vehicle_reg))
    linked_vehicles = len([js for js in job_sheets if js.linked_vehicle_id])

    return jsonify({
        'total_jobs': total_jobs,
        'total_revenue': total_revenue,
        'paid_jobs': paid_jobs,
        'unpaid_jobs': unpaid_jobs,
        'payment_rate': (paid_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        'mot_jobs': len(mot_jobs),
        'mot_revenue': mot_revenue,
        'unique_customers': unique_customers,
        'linked_customers': linked_customers,
        'customer_link_rate': (linked_customers / total_jobs * 100) if total_jobs > 0 else 0,
        'unique_vehicles': unique_vehicles,
        'linked_vehicles': linked_vehicles,
        'vehicle_link_rate': (linked_vehicles / total_jobs * 100) if total_jobs > 0 else 0
    })

@job_sheet_bp.route('/link-data', methods=['POST'])
def link_existing_data():
    """Attempt to link existing job sheets with customers and vehicles"""

    results = {
        'customers_linked': 0,
        'vehicles_linked': 0,
        'errors': []
    }

    # Get all unlinked job sheets
    unlinked_job_sheets = JobSheet.query.filter(
        (JobSheet.linked_customer_id.is_(None)) |
        (JobSheet.linked_vehicle_id.is_(None))
    ).all()

    for job_sheet in unlinked_job_sheets:
        try:
            # Try to link customer
            if not job_sheet.linked_customer_id and job_sheet.customer_name:
                customer = Customer.query.filter(
                    Customer.name.ilike(f"%{job_sheet.customer_name}%")
                ).first()
                if customer:
                    job_sheet.linked_customer_id = customer.id
                    results['customers_linked'] += 1

            # Try to link vehicle
            if not job_sheet.linked_vehicle_id and job_sheet.vehicle_reg:
                vehicle = Vehicle.query.filter_by(
                    registration=job_sheet.vehicle_reg
                ).first()
                if vehicle:
                    job_sheet.linked_vehicle_id = vehicle.id
                    results['vehicles_linked'] += 1

            db.session.commit()

        except Exception as e:
            results['errors'].append(f"Error linking job sheet {job_sheet.doc_id}: {str(e)}")
            db.session.rollback()

    return jsonify(results)

@job_sheet_bp.route('/clear-all', methods=['POST'])
def clear_all_job_sheets():
    """Clear all job sheets (for development/testing)"""
    try:
        JobSheet.query.delete()
        db.session.commit()
        return jsonify({'message': 'All job sheets cleared successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to clear job sheets: {str(e)}'}), 500
