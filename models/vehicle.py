from database import db
from datetime import datetime, date, timezone

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(20), nullable=False, unique=True)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(30))
    year = db.Column(db.Integer)
    mot_expiry = db.Column(db.Date)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    dvla_verified_at = db.Column(db.DateTime, nullable=True)  # Track when last verified with DVLA

    # Relationships
    reminders = db.relationship('Reminder', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    services = db.relationship('Service', back_populates='vehicle', lazy=True, cascade="all, delete-orphan", order_by="desc(Service.service_date)")

    def days_until_mot_expiry(self):
        """Calculate days until MOT expiry (negative if expired)"""
        if not self.mot_expiry:
            return None
        today = date.today()
        delta = self.mot_expiry - today
        return delta.days

    def mot_status(self):
        """Get MOT status with urgency level"""
        days = self.days_until_mot_expiry()
        if days is None:
            return {'status': 'unknown', 'urgency': 'none', 'message': 'No MOT date'}

        if days < 0:
            return {
                'status': 'expired',
                'urgency': 'critical',
                'message': f'Expired {abs(days)} days ago'
            }
        elif days == 0:
            return {
                'status': 'expires_today',
                'urgency': 'critical',
                'message': 'Expires today'
            }
        elif days <= 7:
            return {
                'status': 'expires_soon',
                'urgency': 'high',
                'message': f'Expires in {days} days'
            }
        elif days <= 30:
            return {
                'status': 'due_soon',
                'urgency': 'medium',
                'message': f'Due in {days} days'
            }
        else:
            return {
                'status': 'current',
                'urgency': 'low',
                'message': f'Valid for {days} days'
            }

    def get_last_service(self):
        """Get the most recent service record"""
        if self.services:
            return self.services[0]  # Already ordered by service_date desc
        return None

    def get_service_history_summary(self):
        """Get a summary of service history"""
        if not self.services:
            return {
                'total_services': 0,
                'last_service_date': None,
                'total_spent': 0.0,
                'last_mileage': None
            }

        total_spent = sum(float(service.total_cost or 0) for service in self.services)
        last_service = self.get_last_service()

        return {
            'total_services': len(self.services),
            'last_service_date': last_service.service_date.isoformat() if last_service and last_service.service_date else None,
            'total_spent': total_spent,
            'last_mileage': last_service.mileage if last_service else None
        }

    def to_dict(self):
        mot_status = self.mot_status()
        service_summary = self.get_service_history_summary()

        return {
            'id': self.id,
            'registration': self.registration,
            'make': self.make,
            'model': self.model,
            'color': self.color,
            'year': self.year,
            'mot_expiry': self.mot_expiry.isoformat() if self.mot_expiry else None,
            'customer_id': self.customer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'days_until_mot_expiry': self.days_until_mot_expiry(),
            'mot_status': mot_status,
            'service_history': service_summary
        }
