#!/usr/bin/env python3
"""
Comprehensive data mapping system for MOT Reminder System
Handles relationships: Customer -> Vehicles -> Jobs -> Line Items
"""
import pandas as pd
from datetime import datetime
from decimal import Decimal
import uuid

class ComprehensiveDataMapper:
    def __init__(self):
        self.customers = {}  # customer_account -> customer_data
        self.vehicles = {}   # vehicle_reg -> vehicle_data  
        self.jobs = {}       # doc_id -> job_data
        self.line_items = [] # list of line items
        self.reminders = []  # list of reminders
        
    def get_field_value(self, row, possible_names, default=''):
        """Get field value by trying multiple possible column names"""
        for name in possible_names:
            if name in row and row[name] is not None:
                if pd.isna(row[name]):
                    continue
                value = str(row[name]).strip()
                if value and value.lower() not in ['nan', 'none', '', 'null']:
                    return value
        return default
    
    def parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str or date_str.strip() == '':
            return None
        try:
            return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
        except ValueError:
            try:
                return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
            except ValueError:
                return None
    
    def parse_decimal(self, value_str):
        """Parse decimal values"""
        if not value_str or value_str.strip() == '':
            return Decimal('0')
        try:
            return Decimal(str(value_str).strip())
        except:
            return Decimal('0')
    
    def process_customer_data(self, row):
        """Extract and normalize customer data"""
        customer_account = self.get_field_value(row, [
            'customer_account', 'Customer Account', 'ID Customer', 'Customer ID'
        ])
        
        if not customer_account:
            # Generate customer account if missing
            customer_name = self.get_field_value(row, [
                'customer_name', 'Customer Name', 'Customer', 'Name'
            ])
            if customer_name:
                customer_account = f"CUST_{customer_name.replace(' ', '_').upper()}"
        
        customer_data = {
            'account': customer_account,
            'name': self.get_field_value(row, [
                'customer_name', 'Customer Name', 'Customer', 'Name', 'Client Name'
            ]),
            'address': self.get_field_value(row, [
                'customer_address', 'Customer Address', 'Address', 'Customer Addr'
            ]),
            'contact_number': self.get_field_value(row, [
                'contact_number', 'Contact Number', 'Phone', 'Mobile', 'Contact'
            ]),
            'email': self.get_field_value(row, [
                'email', 'Email', 'Email Address', 'customer_email'
            ]),
            'postcode': self.get_field_value(row, [
                'postcode', 'Postcode', 'Post Code', 'ZIP'
            ])
        }
        
        if customer_account and customer_data['name']:
            self.customers[customer_account] = customer_data
        
        return customer_account
    
    def process_vehicle_data(self, row, customer_account):
        """Extract and normalize vehicle data"""
        vehicle_reg = self.get_field_value(row, [
            'vehicle_reg', 'Vehicle Reg', 'Registration', 'Reg', 'Plate'
        ]).upper()
        
        if not vehicle_reg:
            return None
            
        vehicle_data = {
            'registration': vehicle_reg,
            'make': self.get_field_value(row, [
                'vehicle_make', 'Make', 'Vehicle Make', 'Manufacturer'
            ]),
            'model': self.get_field_value(row, [
                'vehicle_model', 'Model', 'Vehicle Model'
            ]),
            'year': self.get_field_value(row, [
                'year', 'Year', 'Model Year', 'vehicle_year'
            ]),
            'color': self.get_field_value(row, [
                'color', 'Color', 'Colour', 'vehicle_color'
            ]),
            'vin': self.get_field_value(row, [
                'vin', 'VIN', 'Chassis Number', 'Vehicle VIN'
            ]),
            'engine_size': self.get_field_value(row, [
                'engine_size', 'Engine Size', 'Engine'
            ]),
            'fuel_type': self.get_field_value(row, [
                'fuel_type', 'Fuel Type', 'Fuel'
            ]),
            'customer_account': customer_account,
            'mot_expiry': self.parse_date(self.get_field_value(row, [
                'mot_expiry', 'MOT Expiry', 'MOT Due', 'mot_due_date'
            ])),
            'tax_expiry': self.parse_date(self.get_field_value(row, [
                'tax_expiry', 'Tax Expiry', 'Tax Due', 'tax_due_date'
            ]))
        }
        
        self.vehicles[vehicle_reg] = vehicle_data
        return vehicle_reg
    
    def process_job_data(self, row):
        """Extract and normalize job/document data"""
        doc_id = self.get_field_value(row, [
            'id', 'ID Doc', 'Doc ID', 'Document ID', 'document_id'
        ])
        
        if not doc_id:
            doc_id = f"AUTO_{str(uuid.uuid4())[:8]}"
        
        # Process customer and vehicle
        customer_account = self.process_customer_data(row)
        vehicle_reg = self.process_vehicle_data(row, customer_account)
        
        job_data = {
            'doc_id': doc_id,
            'doc_type': self.get_field_value(row, [
                'doc_type', 'Doc Type', 'Document Type', 'Type'
            ], 'JS'),
            'doc_number': self.get_field_value(row, [
                'doc_number', 'Doc No', 'Document Number', 'Number'
            ]),
            'status': self.get_field_value(row, [
                'status', 'Status', 'Job Status'
            ]),
            'date_created': self.parse_date(self.get_field_value(row, [
                'date_created', 'Date Created', 'Created Date', 'Date'
            ])),
            'date_issued': self.parse_date(self.get_field_value(row, [
                'date_issued', 'Date Issued', 'Issued Date'
            ])),
            'date_paid': self.parse_date(self.get_field_value(row, [
                'date_paid', 'Date Paid', 'Paid Date'
            ])),
            'customer_account': customer_account,
            'vehicle_reg': vehicle_reg,
            'mileage': self.get_field_value(row, [
                'mileage', 'Mileage', 'Miles', 'Odometer'
            ]),
            # Financial data
            'labour_net': self.parse_decimal(self.get_field_value(row, [
                'labour_net', 'Sub Labour Net', 'Labour Net'
            ])),
            'labour_tax': self.parse_decimal(self.get_field_value(row, [
                'labour_tax', 'Sub Labour Tax', 'Labour Tax'
            ])),
            'labour_gross': self.parse_decimal(self.get_field_value(row, [
                'labour_gross', 'Sub Labour Gross', 'Labour Gross'
            ])),
            'parts_net': self.parse_decimal(self.get_field_value(row, [
                'parts_net', 'Sub Parts Net', 'Parts Net'
            ])),
            'parts_tax': self.parse_decimal(self.get_field_value(row, [
                'parts_tax', 'Sub Parts Tax', 'Parts Tax'
            ])),
            'parts_gross': self.parse_decimal(self.get_field_value(row, [
                'parts_gross', 'Sub Parts Gross', 'Parts Gross'
            ])),
            'mot_net': self.parse_decimal(self.get_field_value(row, [
                'mot_net', 'Sub MOT Net', 'MOT Net'
            ])),
            'mot_tax': self.parse_decimal(self.get_field_value(row, [
                'mot_tax', 'Sub MOT Tax', 'MOT Tax'
            ])),
            'mot_gross': self.parse_decimal(self.get_field_value(row, [
                'mot_gross', 'Sub MOT Gross', 'MOT Gross'
            ])),
            'total_net': self.parse_decimal(self.get_field_value(row, [
                'total_net', 'Total Net', 'Net Total'
            ])),
            'total_tax': self.parse_decimal(self.get_field_value(row, [
                'total_tax', 'VAT', 'Tax', 'Total Tax'
            ])),
            'total_gross': self.parse_decimal(self.get_field_value(row, [
                'total_gross', 'Grand Total', 'Total', 'Amount'
            ])),
            'job_description': self.get_field_value(row, [
                'description', 'Job Description', 'Work Description', 'Notes'
            ])
        }
        
        self.jobs[doc_id] = job_data
        return doc_id
    
    def process_line_item_data(self, row):
        """Extract line item data"""
        line_item = {
            'id': self.get_field_value(row, ['id', 'line_id', 'item_id']),
            'document_id': self.get_field_value(row, [
                'document_id', 'doc_id', 'job_id'
            ]),
            'doc_number': self.get_field_value(row, [
                'doc_number', 'document_number'
            ]),
            'item_type': self.get_field_value(row, [
                'item_type', 'type', 'category'
            ]),
            'description': self.get_field_value(row, [
                'description', 'item_description', 'details'
            ]),
            'quantity': self.parse_decimal(self.get_field_value(row, [
                'quantity', 'qty', 'amount'
            ])),
            'unit_price': self.parse_decimal(self.get_field_value(row, [
                'unit_price', 'price', 'rate'
            ])),
            'net_amount': self.parse_decimal(self.get_field_value(row, [
                'net_amount', 'net', 'net_total'
            ])),
            'tax_amount': self.parse_decimal(self.get_field_value(row, [
                'tax_amount', 'tax', 'vat_amount'
            ])),
            'gross_amount': self.parse_decimal(self.get_field_value(row, [
                'gross_amount', 'gross', 'total_amount'
            ])),
            'tax_rate': self.parse_decimal(self.get_field_value(row, [
                'tax_rate', 'vat_rate', 'rate'
            ]))
        }
        
        self.line_items.append(line_item)
        return line_item
    
    def process_reminder_data(self, row):
        """Extract reminder data"""
        reminder = {
            'id': self.get_field_value(row, ['id', 'reminder_id']),
            'reminder_type': self.get_field_value(row, [
                'reminder_type', 'type', 'category'
            ]),
            'due_date': self.parse_date(self.get_field_value(row, [
                'due_date', 'date_due', 'expiry_date'
            ])),
            'status': self.get_field_value(row, [
                'status', 'reminder_status'
            ]),
            'sent_date': self.parse_date(self.get_field_value(row, [
                'sent_date', 'date_sent'
            ])),
            'sent_method': self.get_field_value(row, [
                'sent_method', 'method', 'delivery_method'
            ]),
            'notes': self.get_field_value(row, [
                'notes', 'comments', 'description'
            ]),
            'customer_account': self.get_field_value(row, [
                'customer_account', 'customer_id'
            ]),
            'customer_name': self.get_field_value(row, [
                'customer_name', 'customer'
            ]),
            'vehicle_reg': self.get_field_value(row, [
                'vehicle_reg', 'registration'
            ]),
            'vehicle_make': self.get_field_value(row, [
                'vehicle_make', 'make'
            ]),
            'vehicle_model': self.get_field_value(row, [
                'vehicle_model', 'model'
            ])
        }
        
        self.reminders.append(reminder)
        return reminder
    
    def generate_summary(self):
        """Generate summary of processed data"""
        return {
            'customers': len(self.customers),
            'vehicles': len(self.vehicles),
            'jobs': len(self.jobs),
            'line_items': len(self.line_items),
            'reminders': len(self.reminders),
            'customer_sample': list(self.customers.values())[:3],
            'vehicle_sample': list(self.vehicles.values())[:3],
            'job_sample': list(self.jobs.values())[:3]
        }

def test_comprehensive_mapping():
    """Test the comprehensive mapping with sample data"""
    mapper = ComprehensiveDataMapper()
    
    # Test with documents.xlsx structure
    sample_job = {
        'id': 'F22A5CD403C3DC4780B499718DB165F4',
        'doc_number': 'JS001',
        'doc_type': 'JS',
        'date_created': '2024-01-15',
        'customer_account': 'CUST001',
        'customer_name': 'Lisa Renak',
        'vehicle_reg': 'LS18 ZZA',
        'vehicle_make': 'Ford',
        'vehicle_model': 'Focus',
        'total_gross': 216.00
    }
    
    mapper.process_job_data(sample_job)
    
    # Test with line item structure
    sample_line_item = {
        'id': 'LINE001',
        'document_id': 'F22A5CD403C3DC4780B499718DB165F4',
        'item_type': 'LABOUR',
        'description': 'MOT Test',
        'quantity': 1,
        'unit_price': 54.85,
        'gross_amount': 54.85
    }
    
    mapper.process_line_item_data(sample_line_item)
    
    summary = mapper.generate_summary()
    print("Comprehensive Mapping Test Results:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_comprehensive_mapping()
