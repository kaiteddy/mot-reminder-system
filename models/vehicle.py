from database import db
from datetime import datetime, date

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    reminders = db.relationship('Reminder', backref='vehicle', lazy=True, cascade="all, delete-orphan")

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

    def to_dict(self):
        mot_status = self.mot_status()
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
            'mot_status': mot_status
        }
