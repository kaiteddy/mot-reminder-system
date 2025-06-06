from database import db
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta

class PartUsage(db.Model):
    __tablename__ = 'part_usage'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total_cost = db.Column(db.Numeric(10, 2))
    warranty_start = db.Column(db.Date)
    warranty_end = db.Column(db.Date)
    warranty_mileage_start = db.Column(db.Integer)
    warranty_mileage_end = db.Column(db.Integer)
    installation_notes = db.Column(db.Text)
    is_warranty_claim = db.Column(db.Boolean, default=False)
    warranty_claim_reference = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculate_warranty_dates()
        self.calculate_total_cost()

    def calculate_warranty_dates(self):
        """Calculate warranty start and end dates based on part warranty period"""
        if self.service and self.service.service_date and self.part:
            self.warranty_start = self.service.service_date
            
            if self.part.warranty_months:
                self.warranty_end = self.warranty_start + relativedelta(months=self.part.warranty_months)
            
            # Calculate mileage warranty if applicable
            if self.service.mileage and self.part.warranty_mileage:
                self.warranty_mileage_start = self.service.mileage
                self.warranty_mileage_end = self.service.mileage + self.part.warranty_mileage

    def calculate_total_cost(self):
        """Calculate total cost based on quantity and unit cost"""
        self.total_cost = float(self.quantity or 0) * float(self.unit_cost or 0)

    def is_under_warranty(self, check_date=None, current_mileage=None):
        """Check if part is still under warranty"""
        if check_date is None:
            check_date = date.today()
        
        # Check date warranty
        date_warranty_valid = True
        if self.warranty_end:
            date_warranty_valid = check_date <= self.warranty_end
        
        # Check mileage warranty
        mileage_warranty_valid = True
        if current_mileage and self.warranty_mileage_end:
            mileage_warranty_valid = current_mileage <= self.warranty_mileage_end
        
        return date_warranty_valid and mileage_warranty_valid

    def get_warranty_status(self, current_mileage=None):
        """Get detailed warranty status information"""
        today = date.today()
        
        if not self.warranty_end:
            return {
                'status': 'no_warranty',
                'message': 'No warranty information available',
                'days_remaining': None,
                'mileage_remaining': None
            }
        
        if self.is_under_warranty(today, current_mileage):
            days_remaining = (self.warranty_end - today).days
            mileage_remaining = None
            
            if current_mileage and self.warranty_mileage_end:
                mileage_remaining = max(0, self.warranty_mileage_end - current_mileage)
            
            return {
                'status': 'valid',
                'message': f'Under warranty for {days_remaining} more days',
                'days_remaining': days_remaining,
                'mileage_remaining': mileage_remaining
            }
        else:
            return {
                'status': 'expired',
                'message': 'Warranty has expired',
                'days_remaining': 0,
                'mileage_remaining': 0
            }

    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'part_id': self.part_id,
            'part_number': self.part.part_number if self.part else None,
            'part_description': self.part.description if self.part else None,
            'quantity': self.quantity,
            'unit_cost': float(self.unit_cost) if self.unit_cost else 0.0,
            'total_cost': float(self.total_cost) if self.total_cost else 0.0,
            'warranty_start': self.warranty_start.isoformat() if self.warranty_start else None,
            'warranty_end': self.warranty_end.isoformat() if self.warranty_end else None,
            'warranty_mileage_start': self.warranty_mileage_start,
            'warranty_mileage_end': self.warranty_mileage_end,
            'installation_notes': self.installation_notes,
            'is_warranty_claim': self.is_warranty_claim,
            'warranty_claim_reference': self.warranty_claim_reference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
