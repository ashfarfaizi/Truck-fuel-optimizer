#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.views import FuelRouteView
from rest_framework.test import APIRequestFactory
import json

def main():
    print("Testing API with longer route...")
    
    # Test with a longer route that should require fuel stops
    factory = APIRequestFactory()
    test_data = {
        "start_location": "New York, NY",
        "end_location": "Chicago, IL"
    }
    
    request = factory.post(
        '/api/route/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    view = FuelRouteView()
    response = view.post(request)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print(f"✅ API working!")
        print(f"Distance: {data.get('total_distance_miles', 'N/A')} miles")
        print(f"Fuel cost: ${data.get('total_fuel_cost', 'N/A')}")
        print(f"Fuel needed: {data.get('total_fuel_needed_gallons', 'N/A')} gallons")
        print(f"Fuel stops: {len(data.get('fuel_stops', []))}")
        print(f"API used: {data.get('api_info', {}).get('route_source', 'N/A')}")
        
        # Show fuel stops
        for i, stop in enumerate(data.get('fuel_stops', [])[:5]):
            print(f"Stop {i+1}: {stop.get('name', 'N/A')} - ${stop.get('price', 'N/A')}/gal")
    else:
        print(f"❌ Error: {response.data}")

if __name__ == "__main__":
    main()
