"""
Cross-Checking Service for MOT Reminder System

This service compares vehicle data from the garage system with DVLA records.
For local development, it uses mock data to simulate discrepancies.
"""

from services.dvla_api_service import DVLAApiService

class CrossCheckService:
    def __init__(self):
        self.dvla_api = DVLAApiService()
    
    def check_vehicle(self, vehicle):
        """
        Check a vehicle against DVLA records and identify discrepancies.
        For local development, this simulates discrepancies.
        """
        # Get vehicle details from DVLA API
        dvla_data = self.dvla_api.get_vehicle_details(vehicle.registration)
        
        # Compare and identify discrepancies
        discrepancies = []
        
        # Check make
        if vehicle.make and dvla_data.get('make') and vehicle.make.lower() != dvla_data['make'].lower():
            discrepancies.append({
                'field': 'make',
                'garage_value': vehicle.make,
                'dvla_value': dvla_data['make']
            })
        
        # Check model
        if vehicle.model and dvla_data.get('model') and vehicle.model.lower() != dvla_data['model'].lower():
            discrepancies.append({
                'field': 'model',
                'garage_value': vehicle.model,
                'dvla_value': dvla_data['model']
            })
        
        # Check color
        if vehicle.color and dvla_data.get('primaryColour') and vehicle.color.lower() != dvla_data['primaryColour'].lower():
            discrepancies.append({
                'field': 'color',
                'garage_value': vehicle.color,
                'dvla_value': dvla_data['primaryColour']
            })
        
        # Check year
        if vehicle.year and dvla_data.get('yearOfManufacture') and vehicle.year != dvla_data['yearOfManufacture']:
            discrepancies.append({
                'field': 'year',
                'garage_value': str(vehicle.year),
                'dvla_value': str(dvla_data['yearOfManufacture'])
            })
        
        return {
            'has_discrepancies': len(discrepancies) > 0,
            'discrepancies': discrepancies,
            'dvla_data': dvla_data
        }
    
    def update_vehicle_from_dvla(self, vehicle):
        """
        Update vehicle data from DVLA records.
        """
        # Get vehicle details from DVLA API
        dvla_data = self.dvla_api.get_vehicle_details(vehicle.registration)
        
        # Update vehicle data
        if dvla_data.get('make'):
            vehicle.make = dvla_data['make']
        
        if dvla_data.get('model'):
            vehicle.model = dvla_data['model']
        
        if dvla_data.get('primaryColour'):
            vehicle.color = dvla_data['primaryColour']
        
        if dvla_data.get('yearOfManufacture'):
            vehicle.year = dvla_data['yearOfManufacture']
        
        # Return updated vehicle
        return vehicle
