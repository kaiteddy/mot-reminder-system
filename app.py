import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from database import db

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mot_reminder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize database with app
db.init_app(app)

# Import models after db initialization to avoid circular imports
from models.vehicle import Vehicle
from models.customer import Customer
from models.reminder import Reminder
from models.job_sheet import JobSheet
from models.service import Service
from models.part import Part
from models.part_usage import PartUsage

# Import routes
from routes.vehicle import vehicle_bp
from routes.customer import customer_bp
from routes.reminder import reminder_bp
from routes.user import user_bp
from routes.job_sheet import job_sheet_bp
from routes.service import service_bp
from routes.parts import parts_bp
from routes.search import search_bp

# Register blueprints
app.register_blueprint(vehicle_bp, url_prefix='/api/vehicles')
app.register_blueprint(customer_bp, url_prefix='/api/customers')
app.register_blueprint(reminder_bp, url_prefix='/api/reminders')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(job_sheet_bp, url_prefix='/api/job-sheets')
app.register_blueprint(service_bp, url_prefix='/api/services')
app.register_blueprint(parts_bp, url_prefix='/api/parts')
app.register_blueprint(search_bp, url_prefix='/api/search')

# AI Insights endpoint
@app.route('/api/insights')
def get_ai_insights():
    from services.ai_insights_service import AIInsightsService

    insights_service = AIInsightsService()
    insights = insights_service.generate_insights()
    stats = insights_service.get_quick_stats()

    return jsonify({
        'insights': insights,
        'stats': stats
    })

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/batch-verification')
def batch_verification():
    return send_from_directory('templates', 'batch_verification.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# API status endpoint
@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'database': 'connected'
    })

# Create database tables
@app.route('/init-db')
def init_db():
    db.create_all()
    return jsonify({"message": "Database initialized"})

# Create database tables on startup and handle migrations
with app.app_context():
    db.create_all()

    # Check if we need to add new columns to existing tables
    try:
        # Try to query the new columns to see if they exist
        db.session.execute(db.text("SELECT archived_at FROM reminders LIMIT 1"))
        logger.info("Reminders table schema is up to date")
    except Exception as e:
        # Columns don't exist, add them
        logger.info("Adding new columns to reminders table...")
        try:
            db.session.execute(db.text("ALTER TABLE reminders ADD COLUMN archived_at DATETIME"))
            db.session.execute(db.text("ALTER TABLE reminders ADD COLUMN review_batch_id VARCHAR(50)"))
            db.session.commit()
            logger.info("Successfully added new columns to reminders table")
        except Exception as migration_error:
            logger.error(f"Error adding columns to reminders table: {migration_error}")
            db.session.rollback()
            # Don't raise here as the app can still function without these columns

    # Check if we need to add dvla_verified_at column to vehicles table
    try:
        db.session.execute(db.text("SELECT dvla_verified_at FROM vehicles LIMIT 1"))
        logger.info("Vehicles table schema is up to date")
    except Exception as e:
        logger.info("Adding dvla_verified_at column to vehicles table...")
        try:
            db.session.execute(db.text("ALTER TABLE vehicles ADD COLUMN dvla_verified_at DATETIME"))
            db.session.commit()
            logger.info("Successfully added dvla_verified_at column to vehicles table")
        except Exception as migration_error:
            logger.error(f"Error adding dvla_verified_at column: {migration_error}")
            db.session.rollback()
            # Don't raise here as the app can still function without this column

    # Create new tables for service history and parts management
    try:
        # Check if services table exists
        db.session.execute(db.text("SELECT 1 FROM services LIMIT 1"))
        logger.info("Services table already exists")
    except Exception:
        logger.info("Creating services table...")
        try:
            db.session.execute(db.text("""
                CREATE TABLE services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    service_date DATE NOT NULL,
                    service_type VARCHAR(100) NOT NULL,
                    description TEXT,
                    labour_hours REAL DEFAULT 0.0,
                    labour_rate DECIMAL(10,2) DEFAULT 0.0,
                    labour_cost DECIMAL(10,2) DEFAULT 0.0,
                    parts_cost DECIMAL(10,2) DEFAULT 0.0,
                    total_cost DECIMAL(10,2) DEFAULT 0.0,
                    vat_amount DECIMAL(10,2) DEFAULT 0.0,
                    technician VARCHAR(100),
                    advisories TEXT,
                    status VARCHAR(20) DEFAULT 'completed',
                    mileage INTEGER,
                    next_service_due DATE,
                    next_service_mileage INTEGER,
                    invoice_number VARCHAR(50),
                    payment_status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                )
            """))
            db.session.commit()
            logger.info("Successfully created services table")
        except Exception as migration_error:
            logger.error(f"Error creating services table: {migration_error}")
            db.session.rollback()

    # Create parts table
    try:
        db.session.execute(db.text("SELECT 1 FROM parts LIMIT 1"))
        logger.info("Parts table already exists")
    except Exception:
        logger.info("Creating parts table...")
        try:
            db.session.execute(db.text("""
                CREATE TABLE parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_number VARCHAR(100) NOT NULL UNIQUE,
                    description VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    supplier VARCHAR(100),
                    supplier_part_number VARCHAR(100),
                    cost_price DECIMAL(10,2) DEFAULT 0.0,
                    sell_price DECIMAL(10,2) DEFAULT 0.0,
                    stock_quantity INTEGER DEFAULT 0,
                    minimum_stock INTEGER DEFAULT 0,
                    warranty_months INTEGER DEFAULT 12,
                    warranty_mileage INTEGER,
                    location VARCHAR(100),
                    barcode VARCHAR(100),
                    weight REAL,
                    dimensions VARCHAR(100),
                    is_active BOOLEAN DEFAULT 1,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            logger.info("Successfully created parts table")
        except Exception as migration_error:
            logger.error(f"Error creating parts table: {migration_error}")
            db.session.rollback()

    # Create part_usage table
    try:
        db.session.execute(db.text("SELECT 1 FROM part_usage LIMIT 1"))
        logger.info("Part usage table already exists")
    except Exception:
        logger.info("Creating part_usage table...")
        try:
            db.session.execute(db.text("""
                CREATE TABLE part_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id INTEGER NOT NULL,
                    part_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    unit_cost DECIMAL(10,2) NOT NULL,
                    total_cost DECIMAL(10,2),
                    warranty_start DATE,
                    warranty_end DATE,
                    warranty_mileage_start INTEGER,
                    warranty_mileage_end INTEGER,
                    installation_notes TEXT,
                    is_warranty_claim BOOLEAN DEFAULT 0,
                    warranty_claim_reference VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_id) REFERENCES services (id),
                    FOREIGN KEY (part_id) REFERENCES parts (id)
                )
            """))
            db.session.commit()
            logger.info("Successfully created part_usage table")
        except Exception as migration_error:
            logger.error(f"Error creating part_usage table: {migration_error}")
            db.session.rollback()

    # Create indexes for better search performance
    try:
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_vehicles_registration ON vehicles(registration)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_services_vehicle_date ON services(vehicle_id, service_date)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_services_date ON services(service_date)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_part_usage_service ON part_usage(service_id)"))
        db.session.commit()
        logger.info("Successfully created search indexes")
    except Exception as migration_error:
        logger.error(f"Error creating indexes: {migration_error}")
        db.session.rollback()

    logger.info("Database initialization completed")

# Serve the main dashboard
@app.route('/')
def dashboard():
    return send_from_directory('static', 'index.html')

# Serve service history page
@app.route('/service-history')
def service_history():
    return send_from_directory('templates', 'service_history.html')

# Serve parts management page
@app.route('/parts')
def parts_management():
    return send_from_directory('templates', 'parts.html')

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('templates', filename)

if __name__ == '__main__':
    # Run the app on all interfaces port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)
