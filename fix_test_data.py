#!/usr/bin/env python3
"""
Fix test data with proper MOT expiry dates and customer associations
"""

import sqlite3
from datetime import datetime, date, timedelta
import random

# Connect to database
conn = sqlite3.connect('instance/mot_reminder.db')
cursor = conn.cursor()

# First, let's see what we have
print("Current vehicles:")
cursor.execute("SELECT id, registration, make, model, mot_expiry, customer_id FROM vehicles LIMIT 20")
vehicles = cursor.fetchall()
for v in vehicles:
    print(f"ID: {v[0]}, Reg: {v[1]}, Make: {v[2]}, Model: {v[3]}, MOT: {v[4]}, Customer: {v[5]}")

print("\nCurrent customers:")
cursor.execute("SELECT id, name, phone, email FROM customers")
customers = cursor.fetchall()
for c in customers:
    print(f"ID: {c[0]}, Name: {c[1]}, Phone: {c[2]}, Email: {c[3]}")

# Create some test customers if none exist
if not customers:
    print("\nCreating test customers...")
    test_customers = [
        ("John Smith", "07700900123", "john.smith@email.com"),
        ("Sarah Johnson", "07700900124", "sarah.johnson@email.com"),
        ("Mike Wilson", "07700900125", "mike.wilson@email.com"),
        ("Emma Brown", "07700900126", "emma.brown@email.com"),
        ("David Jones", "07700900127", "david.jones@email.com"),
        ("Lisa Davis", "07700900128", "lisa.davis@email.com"),
        ("Tom Miller", "07700900129", "tom.miller@email.com"),
        ("Kate Taylor", "07700900130", "kate.taylor@email.com"),
        ("James Anderson", "07700900131", "james.anderson@email.com"),
        ("Sophie White", "07700900132", "sophie.white@email.com")
    ]

    for name, phone, email in test_customers:
        cursor.execute("""
            INSERT INTO customers (name, phone, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, datetime.now(), datetime.now()))

    conn.commit()

    # Get the new customers
    cursor.execute("SELECT id, name FROM customers")
    customers = cursor.fetchall()
    print(f"Created {len(customers)} customers")

# Update vehicles with proper MOT dates and customer associations
print("\nUpdating vehicles with proper MOT dates and customer associations...")

# Get today's date
today = date.today()

# Define some realistic MOT expiry dates (mix of past due, due soon, and future)
mot_scenarios = [
    # Critical - overdue
    today - timedelta(days=4215),  # Very overdue
    today - timedelta(days=4141),  # Very overdue

    # High priority - due very soon
    today + timedelta(days=1),     # Due tomorrow
    today + timedelta(days=3),     # Due in 3 days
    today + timedelta(days=3),     # Due in 3 days
    today + timedelta(days=4),     # Due in 4 days
    today + timedelta(days=5),     # Due in 5 days

    # Medium priority - due soon
    today + timedelta(days=10),    # Due in 10 days
    today + timedelta(days=10),    # Due in 10 days
    today + timedelta(days=12),    # Due in 12 days
    today + timedelta(days=12),    # Due in 12 days
    today + timedelta(days=12),    # Due in 12 days
    today + timedelta(days=13),    # Due in 13 days
    today + timedelta(days=18),    # Due in 18 days
    today + timedelta(days=20),    # Due in 20 days
    today + timedelta(days=21),    # Due in 21 days

    # Today - critical
    today,                         # Due today
]

# Get all vehicles
cursor.execute("SELECT id, registration FROM vehicles ORDER BY id")
all_vehicles = cursor.fetchall()

# Update each vehicle
customer_ids = [c[0] for c in customers]

for i, (vehicle_id, registration) in enumerate(all_vehicles):
    if i < len(mot_scenarios):
        mot_date = mot_scenarios[i]
    else:
        # For additional vehicles, create random future dates
        days_ahead = random.randint(30, 365)
        mot_date = today + timedelta(days=days_ahead)

    # Assign a random customer
    customer_id = random.choice(customer_ids)

    # Update the vehicle
    cursor.execute("""
        UPDATE vehicles
        SET mot_expiry = ?, customer_id = ?, updated_at = ?
        WHERE id = ?
    """, (mot_date.isoformat(), customer_id, datetime.now(), vehicle_id))

    print(f"Updated {registration}: MOT expiry = {mot_date}, Customer ID = {customer_id}")

conn.commit()

# Now let's create reminders for vehicles with MOT expiry dates
print("\nCreating reminders for vehicles...")

# Clear existing reminders first
cursor.execute("DELETE FROM reminders")

# Get vehicles with MOT expiry dates
cursor.execute("""
    SELECT v.id, v.registration, v.mot_expiry, c.name
    FROM vehicles v
    LEFT JOIN customers c ON v.customer_id = c.id
    WHERE v.mot_expiry IS NOT NULL
    ORDER BY v.mot_expiry
""")

vehicles_with_mot = cursor.fetchall()

reminder_count = 0
for vehicle_id, registration, mot_expiry_str, customer_name in vehicles_with_mot:
    mot_expiry = datetime.strptime(mot_expiry_str, '%Y-%m-%d').date()
    days_until_expiry = (mot_expiry - today).days

    # Create reminder for vehicles that need attention
    if days_until_expiry <= 30:  # Within 30 days or overdue
        reminder_date = today

        cursor.execute("""
            INSERT INTO reminders (vehicle_id, reminder_date, status, created_at, updated_at)
            VALUES (?, ?, 'scheduled', ?, ?)
        """, (vehicle_id, reminder_date.isoformat(), datetime.now(), datetime.now()))

        reminder_count += 1
        print(f"Created reminder for {registration} (Customer: {customer_name}, MOT: {mot_expiry}, Days: {days_until_expiry})")

conn.commit()
print(f"\nCreated {reminder_count} reminders")

# Show final summary
print("\nFinal summary:")
cursor.execute("""
    SELECT v.registration, v.make, v.model, v.mot_expiry, c.name,
           CASE
               WHEN v.mot_expiry < date('now') THEN 'OVERDUE'
               WHEN v.mot_expiry <= date('now', '+7 days') THEN 'CRITICAL'
               WHEN v.mot_expiry <= date('now', '+30 days') THEN 'HIGH'
               ELSE 'MEDIUM'
           END as urgency
    FROM vehicles v
    LEFT JOIN customers c ON v.customer_id = c.id
    WHERE v.mot_expiry IS NOT NULL
    ORDER BY v.mot_expiry
    LIMIT 20
""")

summary = cursor.fetchall()
for reg, make, model, mot_expiry, customer, urgency in summary:
    print(f"{reg} ({make} {model}) - MOT: {mot_expiry} - Customer: {customer} - {urgency}")

conn.close()
print("\nData update complete!")
