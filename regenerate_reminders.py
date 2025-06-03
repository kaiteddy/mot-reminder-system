#!/usr/bin/env python3
"""
Regenerate reminders for all vehicles with proper dates
"""

import sqlite3
from datetime import datetime, date, timedelta

# Connect to database
conn = sqlite3.connect('instance/mot_reminder.db')
cursor = conn.cursor()

today = date.today()
print(f"Today's date: {today}")

# Get all vehicles with MOT expiry dates
cursor.execute("""
    SELECT id, registration, make, model, mot_expiry, customer_id 
    FROM vehicles 
    WHERE mot_expiry IS NOT NULL
    ORDER BY mot_expiry
""")

vehicles = cursor.fetchall()
print(f"Found {len(vehicles)} vehicles with MOT expiry dates")

reminders_created = 0

for vehicle_id, registration, make, model, mot_expiry_str, customer_id in vehicles:
    try:
        # Parse MOT expiry date
        mot_expiry = datetime.strptime(mot_expiry_str, '%Y-%m-%d').date()
        days_until_expiry = (mot_expiry - today).days
        
        # Determine if reminder is needed (within 30 days or overdue)
        if days_until_expiry <= 30:
            # Create reminder
            cursor.execute("""
                INSERT INTO reminders (vehicle_id, reminder_date, status, created_at, updated_at)
                VALUES (?, ?, 'scheduled', ?, ?)
            """, (vehicle_id, today.isoformat(), datetime.now(), datetime.now()))
            
            reminders_created += 1
            
            if days_until_expiry < 0:
                status = f"{abs(days_until_expiry)} days OVERDUE"
            elif days_until_expiry == 0:
                status = "Due TODAY"
            else:
                status = f"Due in {days_until_expiry} days"
                
            print(f"Created reminder for {registration} ({make} {model or ''}): {status}")
        else:
            print(f"Skipped {registration}: Due in {days_until_expiry} days (not urgent)")
            
    except Exception as e:
        print(f"Error processing vehicle {registration}: {e}")

conn.commit()
conn.close()

print(f"\nCompleted! Created {reminders_created} reminders for vehicles needing attention.")
