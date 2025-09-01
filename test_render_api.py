#!/usr/bin/env python
import requests
import json

def test_render_api():
    """Test the fuel route API on Render"""
    # Replace with your actual Render URL
    base_url = "https://truck-fuel-optimizer-7.onrender.com"  # Update this with your actual URL
    
    print("Testing Render API...")
    print(f"Base URL: {base_url}")
    
    # Test 1: Check if server is running
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running and responding")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return
    
    # Test 2: Test route optimization with working route
    print("\n2. Testing route optimization...")
    
    test_data = {
        "start_location": "New York, NY",
        "end_location": "Chicago, IL"
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
            print("✅ Route optimization successful!")
            print(f"  Total Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"  Total Fuel Cost: ${data.get('total_fuel_cost', 'N/A')}")
            print(f"  Fuel Needed: {data.get('total_fuel_needed_gallons', 'N/A')} gallons")
            print(f"  Fuel Stops: {len(data.get('fuel_stops', []))}")
            print(f"  API Used: {data.get('api_info', {}).get('route_source', 'N/A')}")
            
            # Show fuel stops
            for i, stop in enumerate(data.get('fuel_stops', [])[:3]):  # Show first 3
                print(f"    Stop {i+1}: {stop.get('name', 'N/A')} - ${stop.get('price', 'N/A')}/gal")
                
        elif response.status_code == 400:
            error_data = response.json()
            print(f"❌ Bad Request: {error_data}")
        elif response.status_code == 500:
            print("❌ Internal Server Error - Check server logs")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("No error details available")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Check if the URL is correct.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Server might be slow to respond.")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test with shorter route
    print("\n3. Testing with shorter route...")
    
    test_data_2 = {
        "start_location": "Philadelphia, PA",
        "end_location": "Pittsburgh, PA"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/route/",
            json=test_data_2,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Second test successful!")
            print(f"  Distance: {data.get('total_distance_miles', 'N/A')} miles")
            print(f"  Fuel Cost: ${data.get('total_fuel_cost', 'N/A')}")
            print(f"  Fuel Stops: {len(data.get('fuel_stops', []))}")
        else:
            print(f"❌ Second test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in second test: {e}")

if __name__ == "__main__":
    test_render_api()
