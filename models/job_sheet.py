from database import db
from datetime import datetime, timezone, date
from decimal import Decimal

class JobSheet(db.Model):
    __tablename__ = 'job_sheets'

    id = db.Column(db.Integer, primary_key=True)
    
    # Document Information
    doc_id = db.Column(db.String(100), unique=True, nullable=False)  # ID Doc
    doc_type = db.Column(db.String(10), nullable=False)  # Doc Type (JS = Job Sheet)
    doc_no = db.Column(db.String(20), nullable=False)  # Doc No
    date_created = db.Column(db.Date)  # Date Created
    date_issued = db.Column(db.Date)  # Date Issued
    date_paid = db.Column(db.Date)  # Date Paid
    
    # Customer Information
    customer_id_external = db.Column(db.String(100))  # ID Customer (external system)
    customer_name = db.Column(db.String(200))  # Customer Name
    customer_address = db.Column(db.Text)  # Customer Address
    contact_number = db.Column(db.String(50))  # Contact Number
    
    # Vehicle Information
    vehicle_id_external = db.Column(db.String(100))  # ID Vehicle (external system)
    vehicle_reg = db.Column(db.String(20))  # Vehicle Reg
    make = db.Column(db.String(50))  # Make
    model = db.Column(db.String(50))  # Model
    vin = db.Column(db.String(50))  # VIN
    mileage = db.Column(db.Integer)  # Mileage
    
    # Financial Information - Labour
    sub_labour_net = db.Column(db.Numeric(10, 2), default=0)  # Sub Labour Net
    sub_labour_tax = db.Column(db.Numeric(10, 2), default=0)  # Sub Labour Tax
    sub_labour_gross = db.Column(db.Numeric(10, 2), default=0)  # Sub Labour Gross
    
    # Financial Information - Parts
    sub_parts_net = db.Column(db.Numeric(10, 2), default=0)  # Sub Parts Net
    sub_parts_tax = db.Column(db.Numeric(10, 2), default=0)  # Sub Parts Tax
    sub_parts_gross = db.Column(db.Numeric(10, 2), default=0)  # Sub Parts Gross
    
    # Financial Information - MOT
    sub_mot_net = db.Column(db.Numeric(10, 2), default=0)  # Sub MOT Net
    sub_mot_tax = db.Column(db.Numeric(10, 2), default=0)  # Sub MOT Tax
    sub_mot_gross = db.Column(db.Numeric(10, 2), default=0)  # Sub MOT Gross
    
    # Totals
    vat = db.Column(db.Numeric(10, 2), default=0)  # VAT
    grand_total = db.Column(db.Numeric(10, 2), default=0)  # Grand Total
    
    # Job Information
    job_description = db.Column(db.Text)  # Job Description
    
    # System fields
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys to link with existing system
    linked_customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    linked_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    
    # Relationships
    linked_customer = db.relationship('Customer', backref='job_sheets')
    linked_vehicle = db.relationship('Vehicle', backref='job_sheets')

    def to_dict(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'doc_type': self.doc_type,
            'doc_no': self.doc_no,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_issued': self.date_issued.isoformat() if self.date_issued else None,
            'date_paid': self.date_paid.isoformat() if self.date_paid else None,
            'customer_id_external': self.customer_id_external,
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'contact_number': self.contact_number,
            'vehicle_id_external': self.vehicle_id_external,
            'vehicle_reg': self.vehicle_reg,
            'make': self.make,
            'model': self.model,
            'vin': self.vin,
            'mileage': self.mileage,
            'sub_labour_net': float(self.sub_labour_net) if self.sub_labour_net else 0,
            'sub_labour_tax': float(self.sub_labour_tax) if self.sub_labour_tax else 0,
            'sub_labour_gross': float(self.sub_labour_gross) if self.sub_labour_gross else 0,
            'sub_parts_net': float(self.sub_parts_net) if self.sub_parts_net else 0,
            'sub_parts_tax': float(self.sub_parts_tax) if self.sub_parts_tax else 0,
            'sub_parts_gross': float(self.sub_parts_gross) if self.sub_parts_gross else 0,
            'sub_mot_net': float(self.sub_mot_net) if self.sub_mot_net else 0,
            'sub_mot_tax': float(self.sub_mot_tax) if self.sub_mot_tax else 0,
            'sub_mot_gross': float(self.sub_mot_gross) if self.sub_mot_gross else 0,
            'vat': float(self.vat) if self.vat else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'job_description': self.job_description,
            'linked_customer_id': self.linked_customer_id,
            'linked_vehicle_id': self.linked_vehicle_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_financial_summary(self):
        """Get a summary of financial information"""
        return {
            'labour_total': float(self.sub_labour_gross) if self.sub_labour_gross else 0,
            'parts_total': float(self.sub_parts_gross) if self.sub_parts_gross else 0,
            'mot_total': float(self.sub_mot_gross) if self.sub_mot_gross else 0,
            'vat_amount': float(self.vat) if self.vat else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'is_paid': self.date_paid is not None
        }

    def is_mot_job(self):
        """Check if this job sheet includes MOT work"""
        return (self.sub_mot_gross and float(self.sub_mot_gross) > 0) or \
               (self.job_description and 'MOT' in self.job_description.upper())
