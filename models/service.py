from database import db
from datetime import datetime, timezone

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)  # MOT, Service, Repair, Diagnostic
    description = db.Column(db.Text)
    labour_hours = db.Column(db.Float, default=0.0)
    labour_rate = db.Column(db.Numeric(10, 2), default=0.0)
    labour_cost = db.Column(db.Numeric(10, 2), default=0.0)
    parts_cost = db.Column(db.Numeric(10, 2), default=0.0)
    total_cost = db.Column(db.Numeric(10, 2), default=0.0)
    vat_amount = db.Column(db.Numeric(10, 2), default=0.0)
    technician = db.Column(db.String(100))
    advisories = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # completed, pending, cancelled, in_progress
    mileage = db.Column(db.Integer)
    next_service_due = db.Column(db.Date)
    next_service_mileage = db.Column(db.Integer)
    invoice_number = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    vehicle = db.relationship('Vehicle', back_populates='services')
    part_usage = db.relationship('PartUsage', backref='service', cascade="all, delete-orphan")

    def calculate_totals(self):
        """Calculate total costs including labour and parts"""
        self.labour_cost = float(self.labour_hours or 0) * float(self.labour_rate or 0)
        
        # Calculate parts cost from part usage
        parts_total = sum(
            float(usage.quantity or 0) * float(usage.unit_cost or 0) 
            for usage in self.part_usage
        )
        self.parts_cost = parts_total
        
        # Calculate subtotal and VAT
        subtotal = float(self.labour_cost or 0) + float(self.parts_cost or 0)
        self.vat_amount = subtotal * 0.20  # 20% VAT
        self.total_cost = subtotal + float(self.vat_amount or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'service_type': self.service_type,
            'description': self.description,
            'labour_hours': float(self.labour_hours) if self.labour_hours else 0.0,
            'labour_rate': float(self.labour_rate) if self.labour_rate else 0.0,
            'labour_cost': float(self.labour_cost) if self.labour_cost else 0.0,
            'parts_cost': float(self.parts_cost) if self.parts_cost else 0.0,
            'total_cost': float(self.total_cost) if self.total_cost else 0.0,
            'vat_amount': float(self.vat_amount) if self.vat_amount else 0.0,
            'technician': self.technician,
            'advisories': self.advisories,
            'status': self.status,
            'mileage': self.mileage,
            'next_service_due': self.next_service_due.isoformat() if self.next_service_due else None,
            'next_service_mileage': self.next_service_mileage,
            'invoice_number': self.invoice_number,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parts_used': [usage.to_dict() for usage in self.part_usage] if self.part_usage else []
        }

    def get_summary(self):
        """Get a summary of the service for display in lists"""
        return {
            'id': self.id,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'service_type': self.service_type,
            'description': self.description[:100] + '...' if self.description and len(self.description) > 100 else self.description,
            'total_cost': float(self.total_cost) if self.total_cost else 0.0,
            'status': self.status,
            'technician': self.technician,
            'mileage': self.mileage
        }
