from database import db
from datetime import datetime, date, timezone

class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    reminder_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, sent, failed, archived
    sent_at = db.Column(db.DateTime)
    archived_at = db.Column(db.DateTime)
    review_batch_id = db.Column(db.String(50))  # To group reminders by upload batch
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'reminder_date': self.reminder_date.isoformat() if self.reminder_date else None,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'review_batch_id': self.review_batch_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
