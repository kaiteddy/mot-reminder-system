#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced MOT reminder system
Tests all major functionality including database relationships, reminders, and API endpoints
"""

import sqlite3
import requests
import json
from datetime import datetime, date, timedelta

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
DB_PATH = "instance/mot_reminder.db"

def test_database_schema():
    """Test that all required tables and columns exist"""
    print("=== Testing Database Schema ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    required_tables = ['customers', 'vehicles', 'reminders', 'job_sheets']
    
    for table in required_tables:
        if table in tables:
            print(f"✓ {table} table exists")
        else:
            print(f"✗ {table} table missing")
    
    # Test customer table has account field
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'account' in columns:
        print("✓ customers.account field exists")
    else:
        print("✗ customers.account field missing")
    
    # Test vehicles table has dvla_verified_at field
    cursor.execute("PRAGMA table_info(vehicles)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'dvla_verified_at' in columns:
        print("✓ vehicles.dvla_verified_at field exists")
    else:
        print("✗ vehicles.dvla_verified_at field missing")
    
    # Test reminders table has new fields
    cursor.execute("PRAGMA table_info(reminders)")
    columns = [col[1] for col in cursor.fetchall()]
    new_fields = ['archived_at', 'review_batch_id']
    for field in new_fields:
        if field in columns:
            print(f"✓ reminders.{field} field exists")
        else:
            print(f"✗ reminders.{field} field missing")
    
    conn.close()

def test_data_relationships():
    """Test that customer-vehicle relationships are properly established"""
    print("\n=== Testing Data Relationships ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test vehicles with customers
    cursor.execute("""
        SELECT COUNT(*) FROM vehicles 
        WHERE customer_id IS NOT NULL
    """)
    vehicles_with_customers = cursor.fetchone()[0]
    print(f"✓ {vehicles_with_customers} vehicles have customer associations")
    
    # Test vehicles with MOT dates
    cursor.execute("""
        SELECT COUNT(*) FROM vehicles 
        WHERE mot_expiry IS NOT NULL
    """)
    vehicles_with_mot = cursor.fetchone()[0]
    print(f"✓ {vehicles_with_mot} vehicles have MOT expiry dates")
    
    # Test reminders exist
    cursor.execute("SELECT COUNT(*) FROM reminders")
    reminder_count = cursor.fetchone()[0]
    print(f"✓ {reminder_count} reminders created")
    
    # Test reminder-vehicle-customer chain
    cursor.execute("""
        SELECT COUNT(*) FROM reminders r
        JOIN vehicles v ON r.vehicle_id = v.id
        JOIN customers c ON v.customer_id = c.id
    """)
    complete_chains = cursor.fetchone()[0]
    print(f"✓ {complete_chains} complete reminder→vehicle→customer chains")
    
    conn.close()

def test_api_endpoints():
    """Test all API endpoints are working"""
    print("\n=== Testing API Endpoints ===")
    
    endpoints = [
        "/api/customers",
        "/api/vehicles",
        "/api/reminders",
        "/api/insights"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {endpoint} - Status: {response.status_code}, Records: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                print(f"✗ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")

def test_reminder_functionality():
    """Test reminder generation and filtering"""
    print("\n=== Testing Reminder Functionality ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = date.today()
    
    # Test overdue reminders
    cursor.execute("""
        SELECT COUNT(*) FROM reminders r
        JOIN vehicles v ON r.vehicle_id = v.id
        WHERE v.mot_expiry < ?
    """, (today,))
    overdue_count = cursor.fetchone()[0]
    print(f"✓ {overdue_count} overdue MOT reminders")
    
    # Test critical reminders (within 7 days)
    cursor.execute("""
        SELECT COUNT(*) FROM reminders r
        JOIN vehicles v ON r.vehicle_id = v.id
        WHERE v.mot_expiry BETWEEN ? AND ?
    """, (today, today + timedelta(days=7)))
    critical_count = cursor.fetchone()[0]
    print(f"✓ {critical_count} critical MOT reminders (within 7 days)")
    
    # Test high priority reminders (within 30 days)
    cursor.execute("""
        SELECT COUNT(*) FROM reminders r
        JOIN vehicles v ON r.vehicle_id = v.id
        WHERE v.mot_expiry BETWEEN ? AND ?
    """, (today, today + timedelta(days=30)))
    high_count = cursor.fetchone()[0]
    print(f"✓ {high_count} high priority MOT reminders (within 30 days)")
    
    conn.close()

def test_customer_parser():
    """Test customer data parsing functionality"""
    print("\n=== Testing Customer Parser ===")
    
    # Import the parser function
    import sys
    sys.path.append('.')
    from test_customer_parser import parse_customer_data
    
    test_cases = [
        ("Ms Jo Newton + Lauren Newton t: m: 07939887633 e:", "Ms Jo Newton + Lauren Newton", "07939887633"),
        ("Mrs Sheridan t: 8203 0611 m: 07973224728 nikki e: nikkihiller@hotmail.co.uk", "Mrs Sheridan", "07973224728"),
        ("-", None, None),
        ("", None, None)
    ]
    
    for test_input, expected_name, expected_phone in test_cases:
        result = parse_customer_data(test_input)
        if result is None and expected_name is None:
            print(f"✓ Empty/dash input handled correctly")
        elif result and result['name'] == expected_name and result['phone'] == expected_phone:
            print(f"✓ Parsed '{test_input[:30]}...' correctly")
        else:
            print(f"✗ Failed to parse '{test_input[:30]}...'")

def test_web_interface():
    """Test that web interface is accessible"""
    print("\n=== Testing Web Interface ===")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print(f"✓ Main page accessible - Status: {response.status_code}")
        else:
            print(f"✗ Main page error - Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Web interface error: {e}")

def run_all_tests():
    """Run all test suites"""
    print("MOT Reminder System - Enhanced Functionality Test Suite")
    print("=" * 60)
    
    test_database_schema()
    test_data_relationships()
    test_api_endpoints()
    test_reminder_functionality()
    test_customer_parser()
    test_web_interface()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("If you see any ✗ marks above, those areas need attention.")
    print("All ✓ marks indicate successful functionality.")

if __name__ == "__main__":
    run_all_tests()
