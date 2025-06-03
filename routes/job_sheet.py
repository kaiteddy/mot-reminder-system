from flask import Blueprint, request, jsonify
from database import db
from models.job_sheet import JobSheet
from models.customer import Customer
from models.vehicle import Vehicle
from datetime import datetime, date
import csv
import io
from decimal import Decimal, InvalidOperation

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

    # Read file content
    file_content = file.read().decode('utf-8')
    file.seek(0)  # Reset file pointer

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
        csv_reader = csv.DictReader(io.StringIO(file_content))
        processed = 0
        created = 0
        updated = 0

        for row in csv_reader:
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
        csv_reader = csv.DictReader(io.StringIO(file_content))
        processed = 0
        created = 0
        updated = 0

        for row in csv_reader:
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
    """Process job sheet data file"""
    try:
        csv_reader = csv.DictReader(io.StringIO(file_content))
        processed = 0
        created = 0
        updated = 0

        for row in csv_reader:
            try:
                result = process_job_sheet_row(row)
                processed += 1
                if result['action'] == 'created':
                    created += 1
                elif result['action'] == 'updated':
                    updated += 1
            except Exception as e:
                print(f"Error processing job sheet row: {e}")

        return {
            'filename': file.filename,
            'type': 'job_sheets',
            'processed': processed,
            'created': created,
            'updated': updated,
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
        # Read file content
        file_content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        results = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': [],
            'linked_customers': 0,
            'linked_vehicles': 0
        }

        for row_num, row in enumerate(csv_reader, start=2):
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

def process_job_sheet_row(row_data):
    """Process a single job sheet row from CSV"""

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

    # Extract data from row
    doc_id = row_data.get('ID Doc', '').strip()
    if not doc_id:
        raise ValueError("Missing required field: ID Doc")

    # Check if job sheet already exists
    existing_job_sheet = JobSheet.query.filter_by(doc_id=doc_id).first()

    # Prepare job sheet data
    job_sheet_data = {
        'doc_id': doc_id,
        'doc_type': row_data.get('Doc Type', '').strip(),
        'doc_no': row_data.get('Doc No', '').strip(),
        'date_created': parse_date(row_data.get('Date Created')),
        'date_issued': parse_date(row_data.get('Date Issued')),
        'date_paid': parse_date(row_data.get('Date Paid')),
        'customer_id_external': row_data.get('ID Customer', '').strip(),
        'customer_name': row_data.get('Customer Name', '').strip(),
        'customer_address': row_data.get('Customer Address', '').strip(),
        'contact_number': row_data.get('Contact Number', '').strip(),
        'vehicle_id_external': row_data.get('ID Vehicle', '').strip(),
        'vehicle_reg': row_data.get('Vehicle Reg', '').strip().upper(),
        'make': row_data.get('Make', '').strip(),
        'model': row_data.get('Model', '').strip(),
        'vin': row_data.get('VIN', '').strip(),
        'mileage': parse_int(row_data.get('Mileage')),
        'sub_labour_net': parse_decimal(row_data.get('Sub Labour Net')),
        'sub_labour_tax': parse_decimal(row_data.get('Sub Labour Tax')),
        'sub_labour_gross': parse_decimal(row_data.get('Sub Labour Gross')),
        'sub_parts_net': parse_decimal(row_data.get('Sub Parts Net')),
        'sub_parts_tax': parse_decimal(row_data.get('Sub Parts Tax')),
        'sub_parts_gross': parse_decimal(row_data.get('Sub Parts Gross')),
        'sub_mot_net': parse_decimal(row_data.get('Sub MOT Net')),
        'sub_mot_tax': parse_decimal(row_data.get('Sub MOT Tax')),
        'sub_mot_gross': parse_decimal(row_data.get('Sub MOT Gross')),
        'vat': parse_decimal(row_data.get('VAT')),
        'grand_total': parse_decimal(row_data.get('Grand Total')),
        'job_description': row_data.get('Job Description', '').strip()
    }

    # Try to link with existing customers and vehicles
    linked_customer_id = None
    linked_vehicle_id = None
    customer_linked = False
    vehicle_linked = False

    # Link customer by name (fuzzy matching)
    if job_sheet_data['customer_name']:
        customer = Customer.query.filter(
            Customer.name.ilike(f"%{job_sheet_data['customer_name']}%")
        ).first()
        if customer:
            linked_customer_id = customer.id
            customer_linked = True

    # Link vehicle by registration
    if job_sheet_data['vehicle_reg']:
        vehicle = Vehicle.query.filter_by(
            registration=job_sheet_data['vehicle_reg']
        ).first()
        if vehicle:
            linked_vehicle_id = vehicle.id
            vehicle_linked = True

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
            'customer_linked': customer_linked,
            'vehicle_linked': vehicle_linked
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
            'customer_linked': customer_linked,
            'vehicle_linked': vehicle_linked
        }

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
