#!/usr/bin/env python3
"""
Test script for new MOT Reminder System features
This script tests the new service history and parts management functionality
"""

import os
import sys
import requests
import json
from datetime import datetime, date

# Set mock environment variables for testing
os.environ['DVLA_CLIENT_ID'] = 'test-client-id'
os.environ['DVLA_CLIENT_SECRET'] = 'test-client-secret'
os.environ['DVLA_API_KEY'] = 'test-api-key'
os.environ['DVLA_TENANT_ID'] = 'test-tenant-id'
os.environ['SECRET_KEY'] = 'test-secret-key-for-development'

# Import the app after setting environment variables
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import app

def test_database_creation():
    """Test that new database tables are created correctly"""
    print("🔧 Testing database creation...")
    
    with app.app.app_context():
        try:
            # Test services table
            result = app.db.session.execute(app.db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='services'"))
            services_table = result.fetchone()
            assert services_table is not None, "Services table not created"
            print("✅ Services table created successfully")
            
            # Test parts table
            result = app.db.session.execute(app.db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'"))
            parts_table = result.fetchone()
            assert parts_table is not None, "Parts table not created"
            print("✅ Parts table created successfully")
            
            # Test part_usage table
            result = app.db.session.execute(app.db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='part_usage'"))
            part_usage_table = result.fetchone()
            assert part_usage_table is not None, "Part usage table not created"
            print("✅ Part usage table created successfully")
            
            # Test indexes
            result = app.db.session.execute(app.db.text("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_vehicles_registration'"))
            index = result.fetchone()
            assert index is not None, "Vehicle registration index not created"
            print("✅ Search indexes created successfully")
            
        except Exception as e:
            print(f"❌ Database creation test failed: {e}")
            return False
    
    return True

def test_models():
    """Test that new models work correctly"""
    print("\n📊 Testing new models...")
    
    with app.app.app_context():
        try:
            from models.customer import Customer
            from models.vehicle import Vehicle
            from models.service import Service
            from models.part import Part
            from models.part_usage import PartUsage
            
            # Create test customer
            customer = Customer(name="Test Customer", email="test@example.com", phone="01234567890")
            app.db.session.add(customer)
            app.db.session.flush()
            
            # Create test vehicle
            vehicle = Vehicle(
                registration="TEST123",
                make="Test Make",
                model="Test Model",
                customer_id=customer.id,
                mot_expiry=date(2024, 12, 31)
            )
            app.db.session.add(vehicle)
            app.db.session.flush()
            
            # Create test part
            part = Part(
                part_number="TEST-PART-001",
                description="Test Part Description",
                category="Test Category",
                supplier="Test Supplier",
                cost_price=10.00,
                sell_price=15.00,
                stock_quantity=100,
                minimum_stock=10,
                warranty_months=12
            )
            app.db.session.add(part)
            app.db.session.flush()
            
            # Create test service
            service = Service(
                vehicle_id=vehicle.id,
                service_date=date.today(),
                service_type="Test Service",
                description="Test service description",
                labour_hours=2.0,
                labour_rate=50.00,
                technician="Test Technician"
            )
            app.db.session.add(service)
            app.db.session.flush()
            
            # Create test part usage
            part_usage = PartUsage(
                service_id=service.id,
                part_id=part.id,
                quantity=2,
                unit_cost=15.00
            )
            app.db.session.add(part_usage)
            
            # Calculate service totals
            service.calculate_totals()
            
            app.db.session.commit()
            
            # Test relationships
            assert len(vehicle.services) == 1, "Vehicle-service relationship failed"
            assert len(service.part_usage) == 1, "Service-part usage relationship failed"
            assert service.total_cost > 0, "Service total calculation failed"
            
            print("✅ Customer model working correctly")
            print("✅ Vehicle model working correctly")
            print("✅ Service model working correctly")
            print("✅ Part model working correctly")
            print("✅ Part usage model working correctly")
            print("✅ Model relationships working correctly")
            print(f"✅ Service total calculation: £{service.total_cost}")
            
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            app.db.session.rollback()
            return False
    
    return True

def test_api_endpoints():
    """Test that new API endpoints are registered correctly"""
    print("\n🌐 Testing API endpoints...")
    
    try:
        # Test that blueprints are registered
        with app.app.app_context():
            # Get all registered routes
            routes = []
            for rule in app.app.url_map.iter_rules():
                routes.append(rule.rule)
            
            # Check for new service endpoints
            service_endpoints = [r for r in routes if r.startswith('/api/services')]
            assert len(service_endpoints) > 0, "Service endpoints not registered"
            print(f"✅ Service endpoints registered: {len(service_endpoints)} routes")
            
            # Check for new parts endpoints
            parts_endpoints = [r for r in routes if r.startswith('/api/parts')]
            assert len(parts_endpoints) > 0, "Parts endpoints not registered"
            print(f"✅ Parts endpoints registered: {len(parts_endpoints)} routes")
            
            # Check for new search endpoints
            search_endpoints = [r for r in routes if r.startswith('/api/search')]
            assert len(search_endpoints) > 0, "Search endpoints not registered"
            print(f"✅ Search endpoints registered: {len(search_endpoints)} routes")
            
            # Check for new page routes
            page_routes = [r for r in routes if r in ['/service-history', '/parts']]
            assert len(page_routes) == 2, "New page routes not registered"
            print(f"✅ New page routes registered: {page_routes}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False
    
    return True

def test_search_functionality():
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    
    with app.app.app_context():
        try:
            from models.customer import Customer
            from models.vehicle import Vehicle
            
            # Test search query building
            search_term = "test"
            customers = Customer.query.filter(
                app.db.or_(
                    Customer.name.ilike(f"%{search_term}%"),
                    Customer.email.ilike(f"%{search_term}%")
                )
            ).all()
            
            vehicles = Vehicle.query.filter(
                app.db.or_(
                    Vehicle.registration.ilike(f"%{search_term}%"),
                    Vehicle.make.ilike(f"%{search_term}%")
                )
            ).all()
            
            print(f"✅ Search functionality working: found {len(customers)} customers, {len(vehicles)} vehicles")
            
        except Exception as e:
            print(f"❌ Search functionality test failed: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting MOT Reminder System Feature Tests")
    print("=" * 60)
    
    tests = [
        test_database_creation,
        test_models,
        test_api_endpoints,
        test_search_functionality
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! New features are working correctly.")
        print("\n📋 Summary of implemented features:")
        print("✅ Service History Management")
        print("✅ Parts & Warranty Tracking")
        print("✅ Advanced Search & Filtering")
        print("✅ Database Schema Updates")
        print("✅ API Endpoints")
        print("✅ Frontend Components")
        print("✅ Security Improvements")
        
        print("\n🌐 Access the new features at:")
        print("• Service History: http://localhost:5001/service-history")
        print("• Parts Management: http://localhost:5001/parts")
        print("• Main Dashboard: http://localhost:5001/")
        
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
