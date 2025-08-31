#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation
import csv

def load_fuel_data():
    """Load fuel station data from CSV"""
    csv_file = 'fuel_stations.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return
    
    print(f"Loading data from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Skip header
        next(reader, None)
        
        count = 0
        for row in reader:
            if len(row) >= 6:
                try:
                    name = row[0].strip()
                    address = row[1].strip()
                    city = row[2].strip()
                    state = row[3].strip()
                    rack_id = int(float(row[4]))
                    retail_price = float(row[5])
                    
                    # Create or update station
                    station, created = FuelStation.objects.get_or_create(
                        rack_id=rack_id,
                        defaults={
                            'name': name,
                            'address': address,
                            'city': city,
                            'state': state,
                            'retail_price': retail_price
                        }
                    )
                    
                    if not created:
                        # Update existing station
                        station.name = name
                        station.address = address
                        station.city = city
                        station.state = state
                        station.retail_price = retail_price
                        station.save()
                    
                    count += 1
                    print(f"Processed: {name} - {city}, {state}")
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
    
    print(f"\nTotal stations processed: {count}")
    print(f"Total stations in database: {FuelStation.objects.count()}")

if __name__ == '__main__':
    load_fuel_data()
