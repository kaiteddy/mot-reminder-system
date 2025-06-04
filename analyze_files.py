#!/usr/bin/env python3
"""
File analyzer to examine Excel/CSV files and create proper field mapping
"""
import pandas as pd
import os
import glob

def analyze_file(file_path):
    """Analyze a single file and show its structure"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Read the file
        if file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        print(f"Shape: {df.shape} (rows x columns)")
        print(f"\nColumn Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. '{col}'")
        
        print(f"\nFirst 3 rows of data:")
        for i in range(min(3, len(df))):
            print(f"\nRow {i+1}:")
            for col in df.columns[:10]:  # Show first 10 columns
                value = df.iloc[i][col]
                if pd.isna(value):
                    value = "NaN"
                print(f"  {col}: {value}")
            if len(df.columns) > 10:
                print(f"  ... and {len(df.columns) - 10} more columns")
        
        print(f"\nData Types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
            
        return df.columns.tolist()
        
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return []

def create_field_mapping(all_columns):
    """Create comprehensive field mapping based on all discovered columns"""
    print(f"\n{'='*60}")
    print("CREATING COMPREHENSIVE FIELD MAPPING")
    print(f"{'='*60}")
    
    # All unique columns found across files
    unique_columns = set()
    for cols in all_columns.values():
        unique_columns.update(cols)
    
    print(f"All unique columns found:")
    for i, col in enumerate(sorted(unique_columns), 1):
        print(f"  {i:2d}. '{col}'")
    
    # Create mapping
    field_mapping = {
        'doc_id': ['ID Doc', 'Doc ID', 'Document ID', 'id', 'ID'],
        'doc_type': ['Doc Type', 'doc_type', 'Document Type', 'Type'],
        'doc_no': ['Doc No', 'doc_number', 'Document Number', 'Number', 'Job Number'],
        'date_created': ['Date Created', 'date_created', 'Created Date', 'Date'],
        'date_issued': ['Date Issued', 'date_issued', 'Issued Date', 'Issue Date'],
        'date_paid': ['Date Paid', 'date_paid', 'Paid Date', 'Payment Date'],
        'customer_id_external': ['ID Customer', 'customer_account', 'Customer ID', 'Customer'],
        'customer_name': ['Customer Name', 'customer_name', 'Customer', 'Name', 'Client Name'],
        'customer_address': ['Customer Address', 'customer_address', 'Address', 'Customer Addr'],
        'contact_number': ['Contact Number', 'contact_number', 'Phone', 'Mobile', 'Contact', 'Phone Number'],
        'vehicle_id_external': ['ID Vehicle', 'Vehicle ID', 'Vehicle'],
        'vehicle_reg': ['Vehicle Reg', 'vehicle_reg', 'Registration', 'Reg', 'Plate', 'Number Plate'],
        'make': ['Make', 'vehicle_make', 'Vehicle Make', 'Manufacturer'],
        'model': ['Model', 'vehicle_model', 'Vehicle Model'],
        'vin': ['VIN', 'Chassis Number', 'Vehicle VIN'],
        'mileage': ['Mileage', 'Miles', 'Odometer'],
        'sub_labour_net': ['Sub Labour Net', 'labour_net', 'Labour Net', 'Labor Net'],
        'sub_labour_tax': ['Sub Labour Tax', 'labour_tax', 'Labour Tax', 'Labor Tax'],
        'sub_labour_gross': ['Sub Labour Gross', 'labour_gross', 'Labour Gross', 'Labor Gross'],
        'sub_parts_net': ['Sub Parts Net', 'parts_net', 'Parts Net'],
        'sub_parts_tax': ['Sub Parts Tax', 'parts_tax', 'Parts Tax'],
        'sub_parts_gross': ['Sub Parts Gross', 'parts_gross', 'Parts Gross'],
        'sub_mot_net': ['Sub MOT Net', 'mot_net', 'MOT Net'],
        'sub_mot_tax': ['Sub MOT Tax', 'mot_tax', 'MOT Tax'],
        'sub_mot_gross': ['Sub MOT Gross', 'mot_gross', 'MOT Gross'],
        'vat': ['VAT', 'total_tax', 'Tax', 'Sales Tax'],
        'grand_total': ['Grand Total', 'total_gross', 'Total', 'Amount', 'Final Total'],
        'job_description': ['Job Description', 'Description', 'Work Description', 'Notes']
    }
    
    print(f"\nField mapping analysis:")
    for field_name, possible_names in field_mapping.items():
        found_matches = []
        for col in unique_columns:
            if col in possible_names:
                found_matches.append(col)
        
        if found_matches:
            print(f"  ✅ {field_name}: {found_matches}")
        else:
            print(f"  ❌ {field_name}: No matches found")
    
    return field_mapping

def main():
    """Main function to analyze all files"""
    print("MOT Reminder System - File Analyzer")
    print("Looking for Excel/CSV files in uploads directory...")
    
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"Creating {uploads_dir} directory...")
        os.makedirs(uploads_dir)
    
    # Look for files
    file_patterns = [
        os.path.join(uploads_dir, "*.xlsx"),
        os.path.join(uploads_dir, "*.xls"), 
        os.path.join(uploads_dir, "*.csv"),
        "*.xlsx",  # Also check root directory
        "*.xls",
        "*.csv"
    ]
    
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern))
    
    if not all_files:
        print(f"\nNo Excel/CSV files found!")
        print(f"Please copy your files to:")
        print(f"  - {os.path.abspath(uploads_dir)}/")
        print(f"  - Or the current directory: {os.path.abspath('.')}")
        return
    
    print(f"\nFound {len(all_files)} files:")
    for f in all_files:
        print(f"  - {f}")
    
    # Analyze each file
    all_columns = {}
    for file_path in all_files:
        columns = analyze_file(file_path)
        if columns:
            all_columns[file_path] = columns
    
    # Create comprehensive mapping
    if all_columns:
        create_field_mapping(all_columns)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
