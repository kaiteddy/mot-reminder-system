#!/usr/bin/env python3
"""
Test field mapping to debug the issue
"""
import pandas as pd

def get_field_value(row, possible_names, default=''):
    """Get field value by trying multiple possible column names"""
    for name in possible_names:
        if name in row and row[name] is not None:
            # Handle pandas NaN values
            if pd.isna(row[name]):
                continue
            value = str(row[name]).strip()
            if value and value.lower() not in ['nan', 'none', '', 'null']:
                return value
    return default

def test_documents_file():
    """Test the documents.xlsx file specifically"""
    print("Testing documents.xlsx field mapping...")
    
    # Simulate the columns from documents.xlsx based on server logs
    test_row = {
        'id': 'F22A5CD403C3DC4780B499718DB165F4',
        'doc_number': 'JS001',
        'doc_type': 'JS',
        'date_created': '2024-01-15',
        'date_issued': '2024-01-15',
        'date_paid': None,
        'status': 'UNPAID',
        'customer_account': 'CUST001',
        'customer_name': 'Lisa Renak',
        'vehicle_reg': 'LS18 ZZA',
        'vehicle_make': 'Ford',
        'vehicle_model': 'Focus',
        'labour_net': 100.00,
        'labour_tax': 20.00,
        'labour_gross': 120.00,
        'parts_net': 50.00,
        'parts_tax': 10.00,
        'parts_gross': 60.00,
        'mot_net': 30.00,
        'mot_tax': 6.00,
        'mot_gross': 36.00,
        'total_net': 180.00,
        'total_tax': 36.00,
        'total_gross': 216.00
    }
    
    print(f"Test row data: {test_row}")
    print()
    
    # Test field mappings
    field_mappings = {
        'doc_id': ['ID Doc', 'Doc ID', 'Document ID', 'id', 'ID'],
        'customer_name': ['Customer Name', 'customer_name', 'Customer', 'Name', 'Client Name'],
        'vehicle_reg': ['Vehicle Reg', 'vehicle_reg', 'Registration', 'Reg', 'Plate', 'Number Plate'],
        'make': ['Make', 'vehicle_make', 'Vehicle Make', 'Manufacturer'],
        'grand_total': ['Grand Total', 'total_gross', 'Total', 'Amount', 'Final Total'],
        'doc_no': ['Doc No', 'doc_number', 'Document Number', 'Number', 'Job Number']
    }
    
    print("Field mapping test results:")
    for field_name, possible_names in field_mappings.items():
        result = get_field_value(test_row, possible_names)
        print(f"  {field_name}: '{result}' (tried: {possible_names})")
        
        # Show which column was actually used
        found_col = None
        for col_name in possible_names:
            if col_name in test_row and test_row[col_name] is not None:
                if not pd.isna(test_row[col_name]):
                    value = str(test_row[col_name]).strip()
                    if value and value.lower() not in ['nan', 'none', '', 'null']:
                        found_col = col_name
                        break
        print(f"    -> Used column: {found_col}")
        print()

if __name__ == "__main__":
    test_documents_file()
