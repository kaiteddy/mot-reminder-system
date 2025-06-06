import logging
from flask import Blueprint, jsonify, request
from models.part import Part
from models.part_usage import PartUsage
from database import db

logger = logging.getLogger(__name__)

parts_bp = Blueprint('parts', __name__)

# Get all parts
@parts_bp.route('/', methods=['GET'])
def get_parts():
    """Get all parts with optional filtering"""
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        supplier = request.args.get('supplier')
        low_stock = request.args.get('low_stock', type=bool)
        active_only = request.args.get('active_only', type=bool, default=True)
        search = request.args.get('search', '').strip()
        limit = request.args.get('limit', type=int, default=100)
        
        # Build query
        query = Part.query
        
        if active_only:
            query = query.filter(Part.is_active == True)
        
        if category:
            query = query.filter(Part.category == category)
        
        if supplier:
            query = query.filter(Part.supplier == supplier)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Part.part_number.ilike(search_term),
                    Part.description.ilike(search_term),
                    Part.supplier_part_number.ilike(search_term)
                )
            )
        
        # Get parts
        parts = query.order_by(Part.part_number).limit(limit).all()
        
        # Filter for low stock if requested
        if low_stock:
            parts = [part for part in parts if part.is_low_stock()]
        
        return jsonify([part.to_dict() for part in parts])
        
    except Exception as e:
        logger.error(f"Error fetching parts: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get a specific part
@parts_bp.route('/<int:id>', methods=['GET'])
def get_part(id):
    """Get a specific part with usage history"""
    try:
        part = Part.query.get_or_404(id)
        
        # Get usage history
        usage_history = PartUsage.query.filter_by(part_id=id).order_by(PartUsage.created_at.desc()).limit(20).all()
        
        part_data = part.to_dict()
        part_data['usage_history'] = [usage.to_dict() for usage in usage_history]
        
        return jsonify(part_data)
        
    except Exception as e:
        logger.error(f"Error fetching part: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Create a new part
@parts_bp.route('/', methods=['POST'])
def create_part():
    """Create a new part"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        part_number = data.get('part_number', '').strip()
        if not part_number:
            return jsonify({'error': 'Part number is required'}), 400
        
        if len(part_number) > 100:
            return jsonify({'error': 'Part number must be less than 100 characters'}), 400

        # Check if part number already exists
        existing_part = Part.query.filter_by(part_number=part_number).first()
        if existing_part:
            return jsonify({'error': 'Part number already exists'}), 409

        description = data.get('description', '').strip()
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        if len(description) > 200:
            return jsonify({'error': 'Description must be less than 200 characters'}), 400

        # Validate numeric fields
        try:
            cost_price = float(data.get('cost_price', 0))
            sell_price = float(data.get('sell_price', 0))
            stock_quantity = int(data.get('stock_quantity', 0))
            minimum_stock = int(data.get('minimum_stock', 0))
            warranty_months = int(data.get('warranty_months', 12))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid numeric values provided'}), 400

        # Create new part
        part = Part(
            part_number=part_number,
            description=description,
            category=data.get('category', '').strip(),
            supplier=data.get('supplier', '').strip(),
            supplier_part_number=data.get('supplier_part_number', '').strip(),
            cost_price=cost_price,
            sell_price=sell_price,
            stock_quantity=stock_quantity,
            minimum_stock=minimum_stock,
            warranty_months=warranty_months,
            warranty_mileage=int(data.get('warranty_mileage')) if data.get('warranty_mileage') else None,
            location=data.get('location', '').strip(),
            barcode=data.get('barcode', '').strip(),
            weight=float(data.get('weight')) if data.get('weight') else None,
            dimensions=data.get('dimensions', '').strip(),
            notes=data.get('notes', '').strip()
        )

        db.session.add(part)
        db.session.commit()
        
        logger.info(f"Created new part: {part_number}")
        return jsonify(part.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating part: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Update a part
@parts_bp.route('/<int:id>', methods=['PUT'])
def update_part(id):
    """Update an existing part"""
    try:
        part = Part.query.get_or_404(id)
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields with validation
        if 'part_number' in data:
            new_part_number = data['part_number'].strip()
            if new_part_number != part.part_number:
                # Check if new part number already exists
                existing_part = Part.query.filter_by(part_number=new_part_number).first()
                if existing_part:
                    return jsonify({'error': 'Part number already exists'}), 409
                part.part_number = new_part_number

        if 'description' in data:
            description = data['description'].strip()
            if not description:
                return jsonify({'error': 'Description cannot be empty'}), 400
            part.description = description

        if 'category' in data:
            part.category = data['category'].strip()
        
        if 'supplier' in data:
            part.supplier = data['supplier'].strip()
        
        if 'supplier_part_number' in data:
            part.supplier_part_number = data['supplier_part_number'].strip()
        
        if 'cost_price' in data:
            part.cost_price = float(data['cost_price'])
        
        if 'sell_price' in data:
            part.sell_price = float(data['sell_price'])
        
        if 'stock_quantity' in data:
            part.stock_quantity = int(data['stock_quantity'])
        
        if 'minimum_stock' in data:
            part.minimum_stock = int(data['minimum_stock'])
        
        if 'warranty_months' in data:
            part.warranty_months = int(data['warranty_months'])
        
        if 'warranty_mileage' in data:
            part.warranty_mileage = int(data['warranty_mileage']) if data['warranty_mileage'] else None
        
        if 'location' in data:
            part.location = data['location'].strip()
        
        if 'barcode' in data:
            part.barcode = data['barcode'].strip()
        
        if 'weight' in data:
            part.weight = float(data['weight']) if data['weight'] else None
        
        if 'dimensions' in data:
            part.dimensions = data['dimensions'].strip()
        
        if 'is_active' in data:
            part.is_active = bool(data['is_active'])
        
        if 'notes' in data:
            part.notes = data['notes'].strip()

        db.session.commit()
        
        logger.info(f"Updated part: {part.part_number}")
        return jsonify(part.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating part: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete a part
@parts_bp.route('/<int:id>', methods=['DELETE'])
def delete_part(id):
    """Delete a part (soft delete by setting inactive)"""
    try:
        part = Part.query.get_or_404(id)
        
        # Check if part has been used in any services
        usage_count = PartUsage.query.filter_by(part_id=id).count()
        
        if usage_count > 0:
            # Soft delete - just mark as inactive
            part.is_active = False
            db.session.commit()
            logger.info(f"Soft deleted part: {part.part_number} (has usage history)")
            return jsonify({'message': 'Part marked as inactive (has usage history)'})
        else:
            # Hard delete if no usage history
            db.session.delete(part)
            db.session.commit()
            logger.info(f"Hard deleted part: {part.part_number}")
            return jsonify({'message': 'Part deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting part: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get parts categories
@parts_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique part categories"""
    try:
        categories = db.session.query(Part.category).filter(
            Part.category.isnot(None),
            Part.category != '',
            Part.is_active == True
        ).distinct().all()
        
        return jsonify([cat[0] for cat in categories if cat[0]])
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get parts suppliers
@parts_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all unique part suppliers"""
    try:
        suppliers = db.session.query(Part.supplier).filter(
            Part.supplier.isnot(None),
            Part.supplier != '',
            Part.is_active == True
        ).distinct().all()
        
        return jsonify([sup[0] for sup in suppliers if sup[0]])
        
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Get low stock parts
@parts_bp.route('/low-stock', methods=['GET'])
def get_low_stock_parts():
    """Get all parts that are below minimum stock level"""
    try:
        parts = Part.query.filter(Part.is_active == True).all()
        low_stock_parts = [part for part in parts if part.is_low_stock()]
        
        return jsonify([part.get_summary() for part in low_stock_parts])
        
    except Exception as e:
        logger.error(f"Error fetching low stock parts: {e}")
        return jsonify({'error': 'Internal server error'}), 500
