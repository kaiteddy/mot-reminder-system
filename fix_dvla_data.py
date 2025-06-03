#!/usr/bin/env python3
"""
Fix vehicle data by fetching real DVLA data for all vehicles
"""

import sqlite3
import requests
import json
import time
from datetime import datetime

# DVLA API configuration
DVLA_API_URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
DVLA_API_KEY = "your_api_key_here"  # Replace with actual API key

def get_dvla_data(registration):
    """Fetch vehicle data from DVLA API"""
    try:
        headers = {
            'x-api-key': DVLA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = {
            'registrationNumber': registration.replace(' ', '').upper()
        }
        
        response = requests.post(DVLA_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"DVLA API error for {registration}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching DVLA data for {registration}: {e}")
        return None

def update_vehicle_with_dvla_data(cursor, vehicle_id, registration, dvla_data):
    """Update vehicle record with DVLA data"""
    try:
        # Extract relevant fields from DVLA data
        make = dvla_data.get('make', '')
        model = dvla_data.get('model', '')
        color = dvla_data.get('primaryColour', '')
        year = dvla_data.get('yearOfManufacture')
        mot_expiry = dvla_data.get('motExpiryDate')
        fuel_type = dvla_data.get('fuelType', '')
        engine_capacity = dvla_data.get('engineCapacity')
        
        # Convert year to integer if it exists
        if year:
            try:
                year = int(year)
            except:
                year = None
        
        # Update the vehicle record
        cursor.execute("""
            UPDATE vehicles 
            SET make = ?, model = ?, color = ?, year = ?, mot_expiry = ?, 
                fuel_type = ?, engine_capacity = ?
            WHERE id = ?
        """, (make, model, color, year, mot_expiry, fuel_type, engine_capacity, vehicle_id))
        
        print(f"✅ Updated {registration}: {make} {model}, MOT: {mot_expiry}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {registration}: {e}")
        return False

def main():
    """Main function to fix all vehicle data"""
    print("🔄 Starting DVLA data synchronization...")
    
    # Connect to database
    conn = sqlite3.connect('instance/mot_reminder.db')
    cursor = conn.cursor()
    
    try:
        # Get all vehicles
        cursor.execute("SELECT id, registration FROM vehicles")
        vehicles = cursor.fetchall()
        
        print(f"📊 Found {len(vehicles)} vehicles to check")
        
        updated_count = 0
        error_count = 0
        
        for vehicle_id, registration in vehicles:
            print(f"\n🔍 Checking {registration}...")
            
            # Fetch DVLA data
            dvla_data = get_dvla_data(registration)
            
            if dvla_data:
                if update_vehicle_with_dvla_data(cursor, vehicle_id, registration, dvla_data):
                    updated_count += 1
                else:
                    error_count += 1
            else:
                print(f"⚠️  No DVLA data found for {registration}")
                error_count += 1
            
            # Rate limiting - be nice to the API
            time.sleep(0.5)
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Synchronization complete!")
        print(f"📈 Updated: {updated_count} vehicles")
        print(f"❌ Errors: {error_count} vehicles")
        
        # Show some updated vehicles
        print(f"\n📋 Sample of updated vehicles:")
        cursor.execute("""
            SELECT registration, make, model, mot_expiry 
            FROM vehicles 
            ORDER BY registration 
            LIMIT 10
        """)
        
        for reg, make, model, mot_expiry in cursor.fetchall():
            print(f"   {reg}: {make} {model} - MOT: {mot_expiry}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
