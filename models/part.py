from database import db
from datetime import datetime, timezone

class Part(db.Model):
    __tablename__ = 'parts'

    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Engine, Brakes, Suspension, etc.
    supplier = db.Column(db.String(100))
    supplier_part_number = db.Column(db.String(100))
    cost_price = db.Column(db.Numeric(10, 2), default=0.0)
    sell_price = db.Column(db.Numeric(10, 2), default=0.0)
    stock_quantity = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    warranty_months = db.Column(db.Integer, default=12)
    warranty_mileage = db.Column(db.Integer)  # Warranty mileage limit
    location = db.Column(db.String(100))  # Storage location in garage
    barcode = db.Column(db.String(100))
    weight = db.Column(db.Float)  # Weight in kg
    dimensions = db.Column(db.String(100))  # L x W x H
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    usage_records = db.relationship('PartUsage', backref='part', cascade="all, delete-orphan")

    def is_low_stock(self):
        """Check if part is below minimum stock level"""
        return self.stock_quantity <= self.minimum_stock

    def calculate_markup(self):
        """Calculate markup percentage"""
        if self.cost_price and self.cost_price > 0:
            return ((float(self.sell_price or 0) - float(self.cost_price)) / float(self.cost_price)) * 100
        return 0

    def update_stock(self, quantity_used):
        """Update stock quantity when part is used"""
        self.stock_quantity = max(0, self.stock_quantity - quantity_used)

    def to_dict(self):
        return {
            'id': self.id,
            'part_number': self.part_number,
            'description': self.description,
            'category': self.category,
            'supplier': self.supplier,
            'supplier_part_number': self.supplier_part_number,
            'cost_price': float(self.cost_price) if self.cost_price else 0.0,
            'sell_price': float(self.sell_price) if self.sell_price else 0.0,
            'stock_quantity': self.stock_quantity,
            'minimum_stock': self.minimum_stock,
            'warranty_months': self.warranty_months,
            'warranty_mileage': self.warranty_mileage,
            'location': self.location,
            'barcode': self.barcode,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'is_active': self.is_active,
            'notes': self.notes,
            'is_low_stock': self.is_low_stock(),
            'markup_percentage': self.calculate_markup(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_summary(self):
        """Get a summary of the part for display in lists"""
        return {
            'id': self.id,
            'part_number': self.part_number,
            'description': self.description,
            'category': self.category,
            'supplier': self.supplier,
            'sell_price': float(self.sell_price) if self.sell_price else 0.0,
            'stock_quantity': self.stock_quantity,
            'is_low_stock': self.is_low_stock()
        }
