#!/usr/bin/env python3
"""
Fix the MOT expiry dates to be realistic and current
"""

import sqlite3
from datetime import datetime, date, timedelta
import random

# Connect to database
conn = sqlite3.connect('instance/mot_reminder.db')
cursor = conn.cursor()

# Get today's date
today = date.today()

print(f"Today's date: {today}")
print("Current vehicles with MOT dates:")

# Show current data
cursor.execute("SELECT id, registration, make, model, mot_expiry FROM vehicles ORDER BY mot_expiry")
vehicles = cursor.fetchall()

for v in vehicles:
    print(f"ID: {v[0]}, Reg: {v[1]}, Make: {v[2]}, Model: {v[3]}, MOT: {v[4]}")

print("\nUpdating MOT expiry dates to realistic current/future dates...")

# Define realistic MOT expiry dates based on the urgency shown in the image
mot_updates = [
    # Critical - overdue (but not thousands of days)
    ("AD04XLL", today - timedelta(days=30)),   # 30 days overdue
    ("WP56XGY", today - timedelta(days=45)),   # 45 days overdue
    
    # High priority - due very soon
    ("ADZ 4639", today + timedelta(days=1)),   # Due in 1 day
    ("WP65 EYG", today + timedelta(days=1)),   # Due in 1 day  
    ("LG67 LOP", today + timedelta(days=2)),   # Due in 2 days
    ("LK18 GCY", today + timedelta(days=3)),   # Due in 3 days
    ("GL14 RVN", today + timedelta(days=3)),   # Due in 3 days
    ("WF52 RUC", today + timedelta(days=4)),   # Due in 4 days
    ("YG54YCU", today + timedelta(days=5)),   # Due in 5 days
    ("HK20 RNX", today + timedelta(days=7)),   # Due in 7 days
    ("LS58XNR", today + timedelta(days=8)),    # Due in 8 days
    
    # Medium priority - due soon
    ("RJ19 UCY", today + timedelta(days=10)),  # Due in 10 days
    ("RA18 EHU", today + timedelta(days=10)),  # Due in 10 days
    ("LN57 EZF", today + timedelta(days=12)),  # Due in 12 days
    ("DA54 NTT", today + timedelta(days=12)),  # Due in 12 days
]

# Update each vehicle
for registration, new_mot_date in mot_updates:
    cursor.execute("""
        UPDATE vehicles 
        SET mot_expiry = ?, updated_at = ?
        WHERE registration = ?
    """, (new_mot_date.isoformat(), datetime.now(), registration))
    
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        print(f"Updated {registration}: MOT expiry = {new_mot_date}")
    else:
        print(f"WARNING: Vehicle {registration} not found")

# Update any remaining vehicles with random future dates
cursor.execute("""
    SELECT id, registration FROM vehicles 
    WHERE registration NOT IN ({})
""".format(','.join(['?' for _ in mot_updates])), [reg for reg, _ in mot_updates])

remaining_vehicles = cursor.fetchall()

for vehicle_id, registration in remaining_vehicles:
    # Random date between 30 and 365 days in the future
    days_ahead = random.randint(30, 365)
    future_date = today + timedelta(days=days_ahead)
    
    cursor.execute("""
        UPDATE vehicles 
        SET mot_expiry = ?, updated_at = ?
        WHERE id = ?
    """, (future_date.isoformat(), datetime.now(), vehicle_id))
    
    print(f"Updated {registration}: MOT expiry = {future_date} ({days_ahead} days ahead)")

conn.commit()

print("\nUpdated vehicles:")
cursor.execute("SELECT registration, mot_expiry FROM vehicles ORDER BY mot_expiry")
updated_vehicles = cursor.fetchall()

for reg, mot_expiry in updated_vehicles:
    if mot_expiry:
        mot_date = datetime.strptime(mot_expiry, '%Y-%m-%d').date()
        days_diff = (mot_date - today).days
        if days_diff < 0:
            status = f"{abs(days_diff)} days OVERDUE"
        elif days_diff == 0:
            status = "Due TODAY"
        else:
            status = f"Due in {days_diff} days"
        print(f"{reg}: {mot_expiry} ({status})")

# Update reminders to reflect new dates
print("\nUpdating reminder dates...")
cursor.execute("UPDATE reminders SET reminder_date = ?, updated_at = ?", (today.isoformat(), datetime.now()))
print(f"Updated {cursor.rowcount} reminders to today's date")

conn.commit()
conn.close()
print("\nDate fixes complete!")
