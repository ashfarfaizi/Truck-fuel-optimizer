#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.views import FuelRouteView
from rest_framework.test import APIRequestFactory
import json

def test_api():
    print("🧪 Final API Test")
    print("=" * 40)
    
    # Test 1: Short route (should work but no fuel stops needed)
    print("1. Testing short route (Philadelphia to Pittsburgh)...")
    test_short_route("Philadelphia, PA", "Pittsburgh, PA")
    
    # Test 2: Long route (should find fuel stops)
    print("\n2. Testing long route (New York to Chicago)...")
    test_long_route("New York, NY", "Chicago, IL")
    
    # Test 3: Error handling
    print("\n3. Testing error handling...")
    test_error_handling("Invalid City, XX", "Another Invalid, YY")

def test_short_route(start, end):
    factory = APIRequestFactory()
    test_data = {"start_location": start, "end_location": end}
    
    request = factory.post('/api/route/', data=json.dumps(test_data), content_type='application/json')
    view = FuelRouteView()
    response = view.post(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"   ✅ Success: {data.get('total_distance_miles', 'N/A')} miles, {len(data.get('fuel_stops', []))} fuel stops")
    else:
        print(f"   ❌ Failed: {response.status_code}")

def test_long_route(start, end):
    factory = APIRequestFactory()
    test_data = {"start_location": start, "end_location": end}
    
    request = factory.post('/api/route/', data=json.dumps(test_data), content_type='application/json')
    view = FuelRouteView()
    response = view.post(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"   ✅ Success: {data.get('total_distance_miles', 'N/A')} miles, {len(data.get('fuel_stops', []))} fuel stops")
        print(f"   💰 Total cost: ${data.get('total_fuel_cost', 'N/A')}")
    else:
        print(f"   ❌ Failed: {response.status_code}")

def test_error_handling(start, end):
    factory = APIRequestFactory()
    test_data = {"start_location": start, "end_location": end}
    
    request = factory.post('/api/route/', data=json.dumps(test_data), content_type='application/json')
    view = FuelRouteView()
    response = view.post(request)
    
    if response.status_code == 400:
        print(f"   ✅ Error handling works: {response.status_code}")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    test_api()
