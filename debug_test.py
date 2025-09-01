#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation
from fuel_route.views import FuelRouteView
from rest_framework.test import APIRequestFactory
import json

def test_database():
    """Test if database has fuel station data"""
    print("Testing database...")
    
    total_stations = FuelStation.objects.count()
    print(f"Total fuel stations in database: {total_stations}")
    
    stations_with_coords = FuelStation.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).count()
    print(f"Stations with coordinates: {stations_with_coords}")
    
    if total_stations == 0:
        print("❌ No fuel stations in database!")
        print("Run: python manage.py load_fuel_data fuel_stations.csv --skip-geocoding")
        return False
    
    return True

def test_geocoding():
    """Test geocoding functionality"""
    print("\nTesting geocoding...")
    
    view = FuelRouteView()
    
    # Test with a simple location
    coords = view.geocode_location("Miami, FL")
    if coords:
        print(f"✅ Geocoding works: Miami, FL -> {coords}")
        return True
    else:
        print("❌ Geocoding failed for Miami, FL")
        return False

def test_route_calculation():
    """Test route calculation without external API"""
    print("\nTesting route calculation...")
    
    view = FuelRouteView()
    
    # Test fallback route
    start_coords = (25.7617, -80.1918)  # Miami
    end_coords = (28.5383, -81.3792)    # Orlando
    
    route_data = view.create_fallback_route(start_coords, end_coords)
    
    if route_data:
        print(f"✅ Fallback route works: {route_data['distance_miles']:.2f} miles")
        print(f"   API used: {route_data['api_used']}")
        return True
    else:
        print("❌ Fallback route failed")
        return False

def test_fuel_station_search():
    """Test fuel station search"""
    print("\nTesting fuel station search...")
    
    view = FuelRouteView()
    
    # Create a simple route
    route_coords = [
        [25.7617, -80.1918],  # Miami
        [26.1224, -80.1373],  # Fort Lauderdale
        [26.7153, -80.0534],  # West Palm Beach
        [27.6648, -81.5158],  # Sebring
        [28.5383, -81.3792]   # Orlando
    ]
    
    try:
        nearby_stations = view.get_nearby_fuel_stations(route_coords)
        print(f"✅ Found {len(nearby_stations)} nearby stations")
        return True
    except Exception as e:
        print(f"❌ Fuel station search failed: {e}")
        return False

def test_api_request():
    """Test the actual API request"""
    print("\nTesting API request...")
    
    factory = APIRequestFactory()
    
    # Create test data
    test_data = {
        "start_location": "Miami, FL",
        "end_location": "Orlando, FL"
    }
    
    # Create request
    request = factory.post(
        '/api/route/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Test the view
    view = FuelRouteView()
    
    try:
        response = view.post(request)
        print(f"✅ API request successful: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print(f"   Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"   Fuel stops: {len(data.get('fuel_stops', []))}")
        return True
    except Exception as e:
        print(f"❌ API request failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Debugging Fuel Route API")
    print("=" * 50)
    
    # Test database
    db_ok = test_database()
    
    # Test geocoding
    geocoding_ok = test_geocoding()
    
    # Test route calculation
    route_ok = test_route_calculation()
    
    # Test fuel station search
    stations_ok = test_fuel_station_search()
    
    # Test API request
    api_ok = test_api_request()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"Geocoding: {'✅' if geocoding_ok else '❌'}")
    print(f"Route calculation: {'✅' if route_ok else '❌'}")
    print(f"Fuel stations: {'✅' if stations_ok else '❌'}")
    print(f"API request: {'✅' if api_ok else '❌'}")
    
    if not db_ok:
        print("\n🔧 FIX: Load fuel station data:")
        print("python manage.py load_fuel_data fuel_stations.csv --skip-geocoding")
    
    if not geocoding_ok:
        print("\n🔧 FIX: Check internet connection and Nominatim service")
    
    if not api_ok:
        print("\n🔧 FIX: Check the specific error above")

if __name__ == "__main__":
    main()
