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
    print("🔍 Simple Debug Test")
    print("=" * 30)
    
    # Test 1: Check database
    print("1. Checking database...")
    try:
        count = FuelStation.objects.count()
        print(f"   Fuel stations in database: {count}")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Test 2: Check if we can create the view
    print("\n2. Testing view creation...")
    try:
        view = FuelRouteView()
        print("   ✅ View created successfully")
    except Exception as e:
        print(f"   ❌ View creation failed: {e}")
        return
    
    # Test 3: Test geocoding
    print("\n3. Testing geocoding...")
    try:
        coords = view.geocode_location("Miami, FL")
        if coords:
            print(f"   ✅ Geocoding works: {coords}")
        else:
            print("   ❌ Geocoding failed")
    except Exception as e:
        print(f"   ❌ Geocoding error: {e}")
    
    # Test 4: Test route calculation
    print("\n4. Testing route calculation...")
    try:
        start_coords = (25.7617, -80.1918)  # Miami
        end_coords = (28.5383, -81.3792)    # Orlando
        route_data = view.create_fallback_route(start_coords, end_coords)
        print(f"   ✅ Route calculation works: {route_data['distance_miles']:.2f} miles")
    except Exception as e:
        print(f"   ❌ Route calculation error: {e}")
    
    # Test 5: Test API request
    print("\n5. Testing API request...")
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
        
        response = view.post(request)
        print(f"   ✅ API request successful: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"   Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"   Fuel stops: {len(data.get('fuel_stops', []))}")
        else:
            print(f"   Response: {response.data}")
            
    except Exception as e:
        print(f"   ❌ API request error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
