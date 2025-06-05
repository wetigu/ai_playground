#!/usr/bin/env python3
"""
Test script for registration endpoint
"""
import requests
import json

# Test data
test_data = {
    "email": "test@wetigu.com",
    "password": "Test125443!",
    "full_name": "Test User",
    "phone": "4168981156",
    "company_name": "Test Company",
    "company_type": "buyer",
    "business_license": "license123",
    "tax_number": "77698989"
}

# Test local endpoint
def test_local():
    url = "http://localhost:8000/api/v1/auth/register"
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Local test failed: {e}")

# Test production endpoint
def test_production():
    url = "https://api.wetigu.com/api/v1/auth/register"
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Production test failed: {e}")

if __name__ == "__main__":
    print("Testing registration endpoint...")
    print("\n--- Local Test ---")
    test_local()
    print("\n--- Production Test ---")
    test_production() 