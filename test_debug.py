#!/usr/bin/env python
import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint to identify the issue"""
    base_url = "https://truck-fuel-optimizer-7.onrender.com"
    
    print("🔍 Testing debug endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/debug/", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint working!")
            print(f"Database fuel stations: {data.get('database', {}).get('fuel_stations_count', 'N/A')}")
            print(f"Database working: {data.get('database', {}).get('database_working', 'N/A')}")
            print(f"Views imported: {data.get('views', {}).get('FuelRouteView_imported', 'N/A')}")
            print(f"View created: {data.get('views', {}).get('view_created', 'N/A')}")
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing debug endpoint: {e}")

def test_simple_endpoints():
    """Test simple endpoints to see what's working"""
    base_url = "https://truck-fuel-optimizer-7.onrender.com"
    
    print("\n🔍 Testing simple endpoints...")
    
    # Test 1: API info
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"API Info: {response.status_code}")
    except Exception as e:
        print(f"API Info error: {e}")
    
    # Test 2: Test endpoint
    try:
        response = requests.get(f"{base_url}/api/test/", timeout=10)
        print(f"Test endpoint: {response.status_code}")
    except Exception as e:
        print(f"Test endpoint error: {e}")
    
    # Test 3: Simple route endpoint
    try:
        response = requests.get(f"{base_url}/api/simple-route/", timeout=10)
        print(f"Simple route: {response.status_code}")
    except Exception as e:
        print(f"Simple route error: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
    test_simple_endpoints()
