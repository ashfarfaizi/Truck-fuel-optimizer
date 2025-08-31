#!/usr/bin/env python
import requests
import json

def test_api():
    """Test the fuel route API"""
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Basic route request
    print("Testing API with Chicago to Detroit route...")
    
    test_data = {
        "start_location": "Chicago, IL",
        "end_location": "Detroit, MI"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/route/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(f"  Total Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"  Total Fuel Cost: ${data.get('total_fuel_cost', 'N/A')}")
            print(f"  Fuel Needed: {data.get('total_fuel_needed_gallons', 'N/A')} gallons")
            print(f"  Fuel Stops: {len(data.get('fuel_stops', []))}")
            print(f"  API Used: {data.get('api_info', {}).get('route_source', 'N/A')}")
            
            # Show fuel stops
            for i, stop in enumerate(data.get('fuel_stops', [])[:3]):  # Show first 3
                print(f"    Stop {i+1}: {stop.get('name', 'N/A')} - ${stop.get('price', 'N/A')}/gal")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Error case
    print("\nTesting error handling with invalid location...")
    
    error_data = {
        "start_location": "Invalid City, XX",
        "end_location": "Another Invalid, YY"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/route/",
            json=error_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error handling working correctly")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()