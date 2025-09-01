#!/usr/bin/env python
"""
Simple script to add fuel station data
Run this manually in Render shell after deployment
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation

def add_sample_fuel_stations():
    """Add sample fuel stations to the database"""
    
    # Sample fuel station data
    sample_stations = [
        {
            'name': 'PILOT TRAVEL CENTER I-80 EXIT 23',
            'address': '1234 Highway 80',
            'city': 'Rock Springs',
            'state': 'WY',
            'rack_id': 1001,
            'retail_price': 3.45,
            'latitude': 41.5868,
            'longitude': -109.2026
        },
        {
            'name': "LOVE'S TRAVEL STOP I-40 EXIT 89",
            'address': '5678 Route 40',
            'city': 'Flagstaff',
            'state': 'AZ',
            'rack_id': 1002,
            'retail_price': 3.67,
            'latitude': 35.1988,
            'longitude': -111.6518
        },
        {
            'name': 'TA TRAVEL CENTER I-10 EXIT 156',
            'address': '9012 Interstate 10',
            'city': 'El Paso',
            'state': 'TX',
            'rack_id': 1003,
            'retail_price': 3.23,
            'latitude': 31.7619,
            'longitude': -106.4850
        },
        {
            'name': 'FLYING J I-5 EXIT 234',
            'address': '3456 Pacific Highway',
            'city': 'Medford',
            'state': 'OR',
            'rack_id': 1004,
            'retail_price': 3.89,
            'latitude': 42.3265,
            'longitude': -122.8756
        },
        {
            'name': 'PILOT I-90 EXIT 67',
            'address': '7890 Mountain Pass',
            'city': 'Spokane',
            'state': 'WA',
            'rack_id': 1005,
            'retail_price': 3.56,
            'latitude': 47.6588,
            'longitude': -117.4260
        },
        {
            'name': "LOVE'S I-70 EXIT 123",
            'address': '2345 Desert Road',
            'city': 'Grand Junction',
            'state': 'CO',
            'rack_id': 1006,
            'retail_price': 3.34,
            'latitude': 39.0673,
            'longitude': -108.5645
        },
        {
            'name': 'TA I-95 EXIT 89',
            'address': '4567 Coastal Highway',
            'city': 'Jacksonville',
            'state': 'FL',
            'rack_id': 1007,
            'retail_price': 3.12,
            'latitude': 30.3322,
            'longitude': -81.6557
        },
        {
            'name': 'FLYING J I-35 EXIT 156',
            'address': '6789 Central Expressway',
            'city': 'Austin',
            'state': 'TX',
            'rack_id': 1008,
            'retail_price': 3.45,
            'latitude': 30.2672,
            'longitude': -97.7431
        },
        {
            'name': 'PILOT I-75 EXIT 234',
            'address': '8901 Dixie Highway',
            'city': 'Atlanta',
            'state': 'GA',
            'rack_id': 1009,
            'retail_price': 3.23,
            'latitude': 33.7490,
            'longitude': -84.3880
        },
        {
            'name': "LOVE'S I-55 EXIT 67",
            'address': '1234 Mississippi River Road',
            'city': 'Memphis',
            'state': 'TN',
            'rack_id': 1010,
            'retail_price': 3.34,
            'latitude': 35.1495,
            'longitude': -90.0490
        }
    ]
    
    # Create stations
    created_count = 0
    for station_data in sample_stations:
        try:
            station, created = FuelStation.objects.get_or_create(
                rack_id=station_data['rack_id'],
                defaults=station_data
            )
            if created:
                created_count += 1
                print(f"Created: {station.name}")
        except Exception as e:
            print(f"Error creating station {station_data['name']}: {e}")
    
    return created_count

if __name__ == "__main__":
    print("Adding sample fuel stations...")
    created = add_sample_fuel_stations()
    total = FuelStation.objects.count()
    print(f"Created {created} new stations. Total stations: {total}")
