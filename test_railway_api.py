#!/usr/bin/env python3
"""
Test script for Railway API deployment
"""

import requests
import json

# Railway deployment URL
BASE_URL = "https://web-production-623ca.up.railway.app"

def test_api_info():
    """Test the API info endpoint"""
    print("Testing API Info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Info endpoint working correctly!")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Endpoints: {data.get('endpoints')}")
        else:
            print("❌ API Info endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing API Info: {e}")

def test_route_endpoint():
    """Test the route optimization endpoint"""
    print("\nTesting Route Optimization endpoint...")
    
    # Sample test data
    test_data = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "fuel_capacity": 100,
        "current_fuel": 50,
        "fuel_efficiency": 25
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/route/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Route endpoint working correctly!")
        else:
            print("❌ Route endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing Route endpoint: {e}")

def test_invalid_route():
    """Test the route endpoint with invalid data"""
    print("\nTesting Route endpoint with invalid data...")
    
    invalid_data = {
        "invalid_field": "test"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/route/",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            print("✅ Route endpoint correctly handling invalid data!")
        else:
            print("⚠️  Route endpoint response unexpected for invalid data")
            
    except Exception as e:
        print(f"❌ Error testing invalid route: {e}")

if __name__ == "__main__":
    print("🚀 Testing Railway API Deployment")
    print("=" * 50)
    
    test_api_info()
    test_route_endpoint()
    test_invalid_route()
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
