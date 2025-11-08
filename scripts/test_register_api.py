#!/usr/bin/env python
"""
Test script to directly call the external registration API.
"""

import requests
import json

# API Configuration
API_URL = "https://govcarpeta-apis-4905ff3c005b.herokuapp.com"
ENDPOINT = "/apis/registerCitizen"

# Test data
test_citizen = {
    "id": 435243201,
    "name": "Juan Pérez Test",
    "address": "Cra 44 # 45 - 67",
    "email": "juan.perez@test.com",
    "operatorId": "65ca0a00d833e984e26087569",
    "operatorName": "Operador Ciudadano CCP"
}

print("=" * 70)
print("🧪 TESTING EXTERNAL REGISTRATION API")
print("=" * 70)
print(f"URL: {API_URL}{ENDPOINT}")
print(f"Method: POST")
print()
print("Payload:")
print(json.dumps(test_citizen, indent=2))
print("=" * 70)
print()

# Test 1: POST with JSON
print("Test 1: POST with Content-Type: application/json")
print("-" * 70)
try:
    response = requests.post(
        f"{API_URL}{ENDPOINT}",
        json=test_citizen,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500] if response.text else 'Empty'}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("=" * 70)
print()

# Test 2: POST with form data
print("Test 2: POST with Content-Type: application/x-www-form-urlencoded")
print("-" * 70)
try:
    response = requests.post(
        f"{API_URL}{ENDPOINT}",
        data=test_citizen,
        headers={
            'Accept': 'application/json'
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500] if response.text else 'Empty'}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("=" * 70)
print()

# Test 3: Check if endpoint exists with OPTIONS
print("Test 3: OPTIONS request to check endpoint")
print("-" * 70)
try:
    response = requests.options(
        f"{API_URL}{ENDPOINT}",
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Allowed Methods: {response.headers.get('Allow', 'Not specified')}")
    print(f"Headers: {dict(response.headers)}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("=" * 70)
print("✅ TESTS COMPLETED")
print("=" * 70)
