import os
import sys
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from flask_cors import CORS
from database import db

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure SQLite database - using a local file for easy setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mot_reminder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Import models after db initialization to avoid circular imports
from models.vehicle import Vehicle
from models.customer import Customer
from models.reminder import Reminder
from models.job_sheet import JobSheet

# Import routes
from routes.vehicle import vehicle_bp
from routes.customer import customer_bp
from routes.reminder import reminder_bp
from routes.user import user_bp
from routes.job_sheet import job_sheet_bp

# Register blueprints
app.register_blueprint(vehicle_bp, url_prefix='/api/vehicles')
app.register_blueprint(customer_bp, url_prefix='/api/customers')
app.register_blueprint(reminder_bp, url_prefix='/api/reminders')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(job_sheet_bp, url_prefix='/api/job-sheets')

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

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
        print("Database schema is up to date")
    except Exception:
        # Columns don't exist, add them
        print("Adding new columns to reminders table...")
        try:
            db.session.execute(db.text("ALTER TABLE reminders ADD COLUMN archived_at DATETIME"))
            db.session.execute(db.text("ALTER TABLE reminders ADD COLUMN review_batch_id VARCHAR(50)"))
            db.session.commit()
            print("Successfully added new columns to reminders table")
        except Exception as e:
            print(f"Error adding columns: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Run the app on localhost port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
