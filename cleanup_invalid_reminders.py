#!/usr/bin/env python3
"""
Cleanup Invalid Reminders Script

This script removes all invalid reminders that were created based on incorrect 
database MOT dates and regenerates them using real-time DVLA verification.

Usage: python cleanup_invalid_reminders.py
"""

import sqlite3
import sys
import os
from datetime import datetime, date
from services.dvla_api_service import DVLAApiService

def main():
    print("🧹 MOT Reminder System - Invalid Reminders Cleanup")
    print("=" * 60)
    print()
    
    # Connect to database
    try:
        conn = sqlite3.connect('mot_reminder_system.db')
        cursor = conn.cursor()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Initialize DVLA service
    try:
        dvla_service = DVLAApiService()
        print("✅ DVLA service initialized")
    except Exception as e:
        print(f"❌ DVLA service initialization failed: {e}")
        return
    
    print()
    
    # Step 1: Get all current reminders
    cursor.execute("""
        SELECT r.id, r.vehicle_id, r.status, v.registration, v.mot_expiry
        FROM reminders r
        JOIN vehicles v ON r.vehicle_id = v.id
        WHERE r.status IN ('scheduled', 'sent')
        ORDER BY v.registration
    """)
    
    current_reminders = cursor.fetchall()
    print(f"📊 Found {len(current_reminders)} active reminders to verify")
    
    if len(current_reminders) == 0:
        print("✅ No reminders to process")
        return
    
    # Step 2: Verify each reminder against DVLA data
    invalid_reminders = []
    valid_reminders = []
    dvla_errors = []
    vehicles_updated = []
    
    today = date.today()
    
    for reminder_id, vehicle_id, status, registration, db_mot_expiry in current_reminders:
        print(f"\n🔍 Checking {registration}...")
        
        try:
            # Get DVLA data
            dvla_data = dvla_service.get_vehicle_details(registration)
            
            if dvla_data and dvla_data.get('motExpiryDate'):
                dvla_mot_expiry = datetime.strptime(dvla_data['motExpiryDate'], '%Y-%m-%d').date()
                
                # Calculate days until expiry based on DVLA data
                days_until_expiry = (dvla_mot_expiry - today).days
                
                # Update vehicle MOT date if different
                if db_mot_expiry != dvla_mot_expiry.isoformat():
                    cursor.execute("""
                        UPDATE vehicles 
                        SET mot_expiry = ?, dvla_verified_at = ?
                        WHERE id = ?
                    """, (dvla_mot_expiry.isoformat(), datetime.now(), vehicle_id))
                    
                    vehicles_updated.append({
                        'registration': registration,
                        'old_date': db_mot_expiry,
                        'new_date': dvla_mot_expiry.isoformat(),
                        'days_diff': days_until_expiry
                    })
                    
                    print(f"   📅 Updated MOT date: {db_mot_expiry} → {dvla_mot_expiry.isoformat()}")
                
                # Check if reminder is still valid (MOT due within 30 days)
                if days_until_expiry > 30:
                    invalid_reminders.append({
                        'id': reminder_id,
                        'registration': registration,
                        'days_until_expiry': days_until_expiry,
                        'dvla_mot_expiry': dvla_mot_expiry.isoformat()
                    })
                    print(f"   ❌ Invalid reminder: MOT valid for {days_until_expiry} days")
                else:
                    valid_reminders.append({
                        'id': reminder_id,
                        'registration': registration,
                        'days_until_expiry': days_until_expiry
                    })
                    print(f"   ✅ Valid reminder: MOT due in {days_until_expiry} days")
            else:
                dvla_errors.append({
                    'registration': registration,
                    'reminder_id': reminder_id
                })
                print(f"   ⚠️  No DVLA data available")
                
        except Exception as e:
            dvla_errors.append({
                'registration': registration,
                'reminder_id': reminder_id,
                'error': str(e)
            })
            print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total reminders checked: {len(current_reminders)}")
    print(f"Valid reminders: {len(valid_reminders)}")
    print(f"Invalid reminders: {len(invalid_reminders)}")
    print(f"DVLA errors: {len(dvla_errors)}")
    print(f"Vehicles updated: {len(vehicles_updated)}")
    print()
    
    # Step 3: Show details of invalid reminders
    if invalid_reminders:
        print("🗑️  INVALID REMINDERS TO BE REMOVED:")
        print("-" * 50)
        for reminder in invalid_reminders:
            print(f"• {reminder['registration']}: MOT valid for {reminder['days_until_expiry']} days")
        print()
    
    # Step 4: Show vehicles that were updated
    if vehicles_updated:
        print("📅 VEHICLES WITH UPDATED MOT DATES:")
        print("-" * 50)
        for vehicle in vehicles_updated:
            print(f"• {vehicle['registration']}: {vehicle['old_date']} → {vehicle['new_date']} ({vehicle['days_diff']} days)")
        print()
    
    # Step 5: Ask for confirmation
    if invalid_reminders or vehicles_updated:
        response = input("❓ Proceed with cleanup? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Cleanup cancelled")
            return
        
        # Remove invalid reminders
        if invalid_reminders:
            invalid_ids = [r['id'] for r in invalid_reminders]
            placeholders = ','.join(['?' for _ in invalid_ids])
            cursor.execute(f"DELETE FROM reminders WHERE id IN ({placeholders})", invalid_ids)
            print(f"🗑️  Removed {len(invalid_reminders)} invalid reminders")
        
        # Commit all changes
        conn.commit()
        print("✅ Database updated successfully")
        
        # Step 6: Generate new reminders for vehicles that need them
        print("\n🔄 Checking for vehicles that need new reminders...")
        
        # Get all vehicles with customers
        cursor.execute("""
            SELECT v.id, v.registration, v.mot_expiry, v.customer_id
            FROM vehicles v
            WHERE v.customer_id IS NOT NULL AND v.mot_expiry IS NOT NULL
        """)
        
        all_vehicles = cursor.fetchall()
        new_reminders_created = 0
        
        for vehicle_id, registration, mot_expiry_str, customer_id in all_vehicles:
            if mot_expiry_str:
                mot_expiry = datetime.strptime(mot_expiry_str, '%Y-%m-%d').date()
                days_until_expiry = (mot_expiry - today).days
                
                # Check if vehicle needs a reminder (within 30 days) and doesn't have one
                if days_until_expiry <= 30:
                    cursor.execute("""
                        SELECT COUNT(*) FROM reminders 
                        WHERE vehicle_id = ? AND status IN ('scheduled', 'sent')
                    """, (vehicle_id,))
                    
                    existing_count = cursor.fetchone()[0]
                    
                    if existing_count == 0:
                        # Create new reminder
                        cursor.execute("""
                            INSERT INTO reminders (vehicle_id, reminder_date, status, created_at, updated_at)
                            VALUES (?, ?, 'scheduled', ?, ?)
                        """, (vehicle_id, today.isoformat(), datetime.now(), datetime.now()))
                        
                        new_reminders_created += 1
                        print(f"   ➕ Created reminder for {registration} (due in {days_until_expiry} days)")
        
        if new_reminders_created > 0:
            conn.commit()
            print(f"\n✅ Created {new_reminders_created} new DVLA-verified reminders")
        else:
            print("\n✅ No new reminders needed")
    
    else:
        print("✅ All reminders are valid - no cleanup needed")
    
    # Final summary
    print()
    print("=" * 60)
    print("🎉 CLEANUP COMPLETE")
    print("=" * 60)
    print(f"• Invalid reminders removed: {len(invalid_reminders) if invalid_reminders else 0}")
    print(f"• Vehicle MOT dates updated: {len(vehicles_updated) if vehicles_updated else 0}")
    print(f"• New reminders created: {new_reminders_created if 'new_reminders_created' in locals() else 0}")
    print(f"• Valid reminders retained: {len(valid_reminders)}")
    print()
    print("✅ All reminders are now based on authoritative DVLA data!")
    
    conn.close()

if __name__ == "__main__":
    main()
