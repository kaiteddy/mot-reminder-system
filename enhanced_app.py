#!/usr/bin/env python3
"""
Enhanced MOT Reminder System Flask Application
Improved API connectivity and data handling
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import db
import os
from datetime import datetime, date, timedelta
import logging

# Im# Import enhanced routes
from routes.enhanced_vehicle import vehicle_bp
from routes.enhanced_customer import customer_bp
from routes.enhanced_reminder import reminder_bp
from routes.data_import import data_import_bp
from routes.data_management import data_mgmt_bp

# Import models for database initialization
from models.customer import Customer
from models.vehicle import Vehicle
from models.reminder import Reminder

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mot_reminder.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    
    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Initialize database
    db.init_app(app)
    
    return app

# Create Flask application
app = create_app()

# Register enhanced blueprints
app.register_blueprint(vehicle_bp, url_prefix='/api/vehicles')
app.register_blueprint(customer_bp, url_prefix='/api/customers')
app.register_blueprint(reminder_bp, url_prefix='/api/reminders')
app.register_blueprint(data_import_bp, url_prefix='/api/import')
app.register_blueprint(data_mgmt_bp, url_prefix='/api/data')

# Root route - serve enhanced HTML
@app.route('/')
def index():
    """Serve the enhanced main page"""
    return send_from_directory(app.static_folder, 'enhanced-index.html')

# API status endpoint
@app.route('/api/status')
def api_status():
    """Enhanced API status with system information"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        
        # Get counts
        vehicle_count = Vehicle.query.count()
        customer_count = Customer.query.count()
        reminder_count = Reminder.query.count()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0-enhanced',
            'counts': {
                'vehicles': vehicle_count,
                'customers': customer_count,
                'reminders': reminder_count
            }
        })
    except Exception as e:
        app.logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'error',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Enhanced insights endpoint
@app.route('/api/insights')
def get_insights():
    """Generate AI-style insights from data"""
    try:
        # Get current data
        vehicles = Vehicle.query.all()
        customers = Customer.query.all()
        reminders = Reminder.query.all()
        
        # Calculate insights
        total_vehicles = len(vehicles)
        total_customers = len(customers)
        
        # MOT status analysis
        expired_count = 0
        expires_soon_count = 0
        current_count = 0
        
        for vehicle in vehicles:
            if vehicle.mot_expiry:
                status = vehicle.mot_status()
                if status == 'expired':
                    expired_count += 1
                elif status in ['expires_today', 'expires_soon']:
                    expires_soon_count += 1
                else:
                    current_count += 1
        
        # Reminder analysis
        today = date.today()
        overdue_reminders = [r for r in reminders if r.reminder_date <= today and r.status == 'scheduled']
        upcoming_reminders = [r for r in reminders if r.reminder_date > today and r.status == 'scheduled']
        
        # Revenue potential calculation (estimated)
        revenue_potential = (expired_count * 150) + (expires_soon_count * 120)
        
        # Generate recommendations
        recommendations = []
        if expired_count > 0:
            recommendations.append(f"Contact {expired_count} customers with expired MOTs immediately")
        if expires_soon_count > 0:
            recommendations.append(f"Schedule reminders for {expires_soon_count} vehicles expiring soon")
        if len(overdue_reminders) > 0:
            recommendations.append(f"Process {len(overdue_reminders)} overdue reminders")
        if revenue_potential > 0:
            recommendations.append(f"Potential revenue of £{revenue_potential} from MOT bookings")
        
        if not recommendations:
            recommendations.append("All MOTs are current and reminders are up to date")
        
        return jsonify({
            'success': True,
            'insights': {
                'total_revenue_potential': revenue_potential,
                'overdue_count': expired_count,
                'upcoming_count': expires_soon_count,
                'reminder_backlog': len(overdue_reminders),
                'recommendations': recommendations,
                'summary': {
                    'vehicles': total_vehicles,
                    'customers': total_customers,
                    'expired_mots': expired_count,
                    'current_mots': current_count
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Error generating insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate insights',
            'message': str(e)
        }), 500

# Dashboard data endpoint
@app.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data in one request"""
    try:
        # Get all data
        vehicles = Vehicle.query.all()
        customers = Customer.query.all()
        reminders = Reminder.query.all()
        
        # Calculate dashboard metrics
        today = date.today()
        due_reminders = [r for r in reminders if r.reminder_date <= today and r.status == 'scheduled']
        
        # MOT status breakdown
        mot_status_counts = {
            'expired': 0,
            'expires_today': 0,
            'expires_soon': 0,
            'due_soon': 0,
            'current': 0
        }
        
        for vehicle in vehicles:
            if vehicle.mot_expiry:
                status = vehicle.mot_status()
                status_key = status['status']  # Extract the status string from the dict
                if status_key in mot_status_counts:
                    mot_status_counts[status_key] += 1
        
        return jsonify({
            'success': True,
            'dashboard': {
                'counts': {
                    'vehicles': len(vehicles),
                    'customers': len(customers),
                    'reminders_due': len(due_reminders)
                },
                'mot_status': mot_status_counts,
                'due_reminders': [r.to_dict() for r in due_reminders[:5]]  # Latest 5
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get dashboard data',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': 'The request was invalid'
    }), 400

# Database initialization and migration
def init_database():
    """Initialize database with tables and migrations"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Add any missing columns (migrations)
            try:
                # Check and add dvla_verified_at column to vehicles
                db.session.execute("SELECT dvla_verified_at FROM vehicles LIMIT 1")
            except Exception:
                try:
                    db.session.execute("ALTER TABLE vehicles ADD COLUMN dvla_verified_at DATETIME")
                    db.session.commit()
                    app.logger.info("Added dvla_verified_at column to vehicles table")
                except Exception as e:
                    app.logger.warning(f"Could not add dvla_verified_at column: {e}")
                    db.session.rollback()
            
            # Check and add archived_at column to reminders
            try:
                db.session.execute("SELECT archived_at FROM reminders LIMIT 1")
            except Exception:
                try:
                    db.session.execute("ALTER TABLE reminders ADD COLUMN archived_at DATETIME")
                    db.session.commit()
                    app.logger.info("Added archived_at column to reminders table")
                except Exception as e:
                    app.logger.warning(f"Could not add archived_at column: {e}")
                    db.session.rollback()
            
            # Check and add review_batch_id column to reminders
            try:
                db.session.execute("SELECT review_batch_id FROM reminders LIMIT 1")
            except Exception:
                try:
                    db.session.execute("ALTER TABLE reminders ADD COLUMN review_batch_id VARCHAR(50)")
                    db.session.commit()
                    app.logger.info("Added review_batch_id column to reminders table")
                except Exception as e:
                    app.logger.warning(f"Could not add review_batch_id column: {e}")
                    db.session.rollback()
                    
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the enhanced app
    app.logger.info("Starting Enhanced MOT Reminder System")
    app.run(host='0.0.0.0', port=5001, debug=False)

