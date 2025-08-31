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
from rest_framework import status
import json

def test_basic_functionality():
    """Test basic Django functionality"""
    print("Testing Django project setup...")
    
    # Test 1: Check if models work
    try:
        count = FuelStation.objects.count()
        print(f"✅ Database connection working. Stations in DB: {count}")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Test 2: Check if view can be instantiated
    try:
        view = FuelRouteView()
        print("✅ FuelRouteView can be instantiated")
    except Exception as e:
        print(f"❌ View instantiation error: {e}")
        return False
    
    # Test 3: Test geocoding (should work with fallback)
    try:
        coords = view.geocode_location("Chicago, IL")
        if coords:
            print(f"✅ Geocoding working: Chicago, IL -> {coords}")
        else:
            print("⚠️  Geocoding returned None (may use fallback)")
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return False
    
    # Test 4: Test fallback route creation
    try:
        start_coords = (41.8781, -87.6298)  # Chicago
        end_coords = (42.3314, -83.0458)    # Detroit
        route = view.create_fallback_route(start_coords, end_coords)
        print(f"✅ Fallback route working: {route['distance_miles']:.1f} miles")
    except Exception as e:
        print(f"❌ Fallback route error: {e}")
        return False
    
    return True

def test_api_request():
    """Test API request handling"""
    print("\nTesting API request handling...")
    
    factory = APIRequestFactory()
    
    # Create a test request
    data = {
        "start_location": "Chicago, IL",
        "end_location": "Detroit, MI"
    }
    
    request = factory.post('/api/route/', data, format='json')
    view = FuelRouteView()
    
    try:
        response = view.post(request)
        print(f"✅ API request processed. Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.data
            print(f"  Distance: {response_data.get('total_distance_miles', 'N/A')} miles")
            print(f"  Fuel Cost: ${response_data.get('total_fuel_cost', 'N/A')}")
            print(f"  Fuel Stops: {len(response_data.get('fuel_stops', []))}")
            return True
        else:
            print(f"  Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ API request error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("FUEL ROUTE OPTIMIZER - BASIC FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test basic functionality
    basic_ok = test_basic_functionality()
    
    if basic_ok:
        # Test API request
        api_ok = test_api_request()
        
        if api_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Django project is working correctly")
            print("✅ API can process requests")
            print("✅ Ready to start server and test with external tools")
        else:
            print("\n⚠️  Basic functionality works but API has issues")
    else:
        print("\n❌ Basic functionality tests failed")
        print("🔧 Check Django setup and dependencies")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
