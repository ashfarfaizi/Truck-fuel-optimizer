#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation
from fuel_route.views import FuelRouteView
from rest_framework.test import APIRequestFactory
import json

def main():
    print("🔍 Detailed Debug Test")
    print("=" * 40)
    
    # Test 1: Check fuel stations with coordinates
    print("1. Checking fuel stations with coordinates...")
    try:
        stations_with_coords = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        print(f"   Stations with coordinates: {stations_with_coords}")
        
        # Show a few sample stations
        sample_stations = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )[:3]
        
        for station in sample_stations:
            print(f"   - {station.name}: ({station.latitude}, {station.longitude})")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Test fuel station search
    print("\n2. Testing fuel station search...")
    try:
        view = FuelRouteView()
        
        # Create a route from Miami to Orlando
        route_coords = [
            [25.7617, -80.1918],  # Miami
            [26.1224, -80.1373],  # Fort Lauderdale
            [26.7153, -80.0534],  # West Palm Beach
            [27.6648, -81.5158],  # Sebring
            [28.5383, -81.3792]   # Orlando
        ]
        
        nearby_stations = view.get_nearby_fuel_stations(route_coords)
        print(f"   Found {len(nearby_stations)} nearby stations")
        
        if nearby_stations:
            for i, station in enumerate(nearby_stations[:3]):
                print(f"   - {station['name']}: ${station['retail_price']}/gal, {station['distance_from_route']} miles from route")
        else:
            print("   No nearby stations found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test route calculation with fuel stops
    print("\n3. Testing route calculation with fuel stops...")
    try:
        view = FuelRouteView()
        
        # Create a simple route
        route_coords = [
            [25.7617, -80.1918],  # Miami
            [26.1224, -80.1373],  # Fort Lauderdale
            [26.7153, -80.0534],  # West Palm Beach
            [27.6648, -81.5158],  # Sebring
            [28.5383, -81.3792]   # Orlando
        ]
        
        nearby_stations = view.get_nearby_fuel_stations(route_coords)
        fuel_stops, total_distance = view.find_optimal_fuel_stops(route_coords, nearby_stations)
        
        print(f"   Total distance: {total_distance:.2f} miles")
        print(f"   Fuel stops found: {len(fuel_stops)}")
        
        for i, stop in enumerate(fuel_stops[:3]):
            print(f"   - Stop {i+1}: {stop['name']} - ${stop['price']}/gal")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test full API request
    print("\n4. Testing full API request...")
    try:
        factory = APIRequestFactory()
        test_data = {
            "start_location": "Miami, FL",
            "end_location": "Orlando, FL"
        }
        
        request = factory.post(
            '/api/route/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        view = FuelRouteView()
        response = view.post(request)
        
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"   Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"   Fuel cost: ${data.get('total_fuel_cost', 'N/A')}")
            print(f"   Fuel needed: {data.get('total_fuel_needed_gallons', 'N/A')} gallons")
            print(f"   Fuel stops: {len(data.get('fuel_stops', []))}")
            print(f"   API used: {data.get('api_info', {}).get('route_source', 'N/A')}")
            
            # Show fuel stops
            for i, stop in enumerate(data.get('fuel_stops', [])[:3]):
                print(f"   - Stop {i+1}: {stop.get('name', 'N/A')} - ${stop.get('price', 'N/A')}/gal")
        else:
            print(f"   Error response: {response.data}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
