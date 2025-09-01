#!/usr/bin/env python
import requests
import json

def test_route_endpoint():
    """Test the main route endpoint with a simple request"""
    base_url = "https://truck-fuel-optimizer-7.onrender.com"
    
    print("🔍 Testing main route endpoint...")
    
    # Test with a simple route
    test_data = {
        "start_location": "Atlanta, GA",
        "end_location": "Memphis, TN"
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
            print("✅ Route endpoint working!")
            print(f"Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"Fuel stops: {len(data.get('fuel_stops', []))}")
        elif response.status_code == 500:
            print("❌ Internal Server Error")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_route_endpoint()
