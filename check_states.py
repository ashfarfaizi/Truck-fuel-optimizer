#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation
from django.db.models import Count

def main():
    print("Checking fuel stations by state...")
    
    # Get states with fuel stations
    states = FuelStation.objects.values('state').annotate(count=Count('state')).order_by('-count')
    
    print("States with fuel stations:")
    for state in states[:15]:
        print(f"- {state['state']}: {state['count']} stations")
    
    # Show some sample stations
    print("\nSample stations:")
    sample_stations = FuelStation.objects.all()[:10]
    for station in sample_stations:
        print(f"- {station.name}: {station.city}, {station.state} ({station.latitude}, {station.longitude})")

if __name__ == "__main__":
    main()
