#!/usr/bin/env python
"""
Test script for the Aircraft Registry API

This script demonstrates how to interact with the Registry API
using Python's requests library. It includes examples for 
creating, reading, updating, and deleting records for all entity types.

Usage:
    python test_api.py

Requirements:
    - requests library (pip install requests)
"""

import requests
import json
import uuid

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Simulated Auth0 JWT token (replace with a real token in production)
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzY29wZSI6InJlYWQ6cHJpdmlsZWdlZCJ9.KOegGEpI-PyT9K91sEfrd-eqQ0L_xcXQjk_LG1jNHwk"

# Headers for the request, including Auth0 token
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MOCK_TOKEN}"
}

def handle_response(response):
    """Handle API response, print status and data"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except json.JSONDecodeError:
        print(response.text)
        return None

def test_operators():
    """Test operator endpoints"""
    print("\n=== TESTING OPERATOR ENDPOINTS ===")
    
    # Create a new operator
    print("\n--- Creating a new operator ---")
    operator_data = {
        "company_name": "Drone Operations Ltd",
        "website": "https://droneoperations.com",
        "email": "info@droneoperations.com",
        "phone_number": "+1234567890",
        "operator_type": 1,
        "vat_number": "GB123456789",
        "insurance_number": "INS-12345",
        "company_number": "COMP-12345",
        "country": "GB",
        "address": {
            "address_line_1": "123 Drone Street",
            "address_line_2": "Aviation District",
            "address_line_3": "",
            "postcode": "AB12 3CD",
            "city": "London",
            "country": "GB"
        }
    }
    
    print(f"Sending request to {BASE_URL}/operators")
    print(f"Request data: {json.dumps(operator_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/operators", json=operator_data, headers=HEADERS)
    operator = handle_response(response)
    if not operator or response.status_code != 201:
        print("Failed to create operator, skipping related tests")
        return None
    
    operator_id = operator.get("id")
    
    # Get operator details
    print("\n--- Getting operator details ---")
    response = requests.get(f"{BASE_URL}/operators/{operator_id}")
    handle_response(response)
    
    # Get privileged operator details
    print("\n--- Getting privileged operator details ---")
    response = requests.get(f"{BASE_URL}/operators/{operator_id}/privilaged", headers=HEADERS)
    handle_response(response)
    
    return operator_id

def test_aircraft(operator_id):
    """Test aircraft endpoints"""
    if not operator_id:
        print("No operator_id provided, skipping aircraft tests")
        return None
        
    print("\n=== TESTING AIRCRAFT ENDPOINTS ===")
    
    # Create a new aircraft
    print("\n--- Creating a new aircraft ---")
    # First, get a manufacturer ID
    response = requests.get(f"{BASE_URL}/manufacturers")
    manufacturers = handle_response(response)
    manufacturer_id = ""
    if manufacturers and len(manufacturers) > 0:
        manufacturer_id = manufacturers[0].get("id", "")
    
    aircraft_data = {
        "operator": operator_id,
        "mass": 5,
        "manufacturer": manufacturer_id,
        "model": "Phantom 4 Pro",
        "esn": f"ESN{uuid.uuid4().hex[:10].upper()}",
        "maci_number": f"MACI{uuid.uuid4().hex[:8].upper()}",
        "registration_mark": "G-DRON",
        "category": 2,
        "sub_category": 4,
        "is_airworthy": True,
        "icao_aircraft_type_designator": "UAV",
        "max_certified_takeoff_weight": 1.380,
        "status": 1
    }
    
    print(f"Sending request to {BASE_URL}/aircraft")
    print(f"Request data: {json.dumps(aircraft_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/aircraft", json=aircraft_data, headers=HEADERS)
    aircraft = handle_response(response)
    if not aircraft or response.status_code != 201:
        print("Failed to create aircraft, skipping related tests")
        return None
    
    aircraft_id = aircraft.get("id")
    aircraft_esn = aircraft.get("esn")
    
    # Get aircraft details
    print("\n--- Getting aircraft details ---")
    response = requests.get(f"{BASE_URL}/aircraft/{aircraft_id}")
    handle_response(response)
    
    # Get aircraft by ESN
    print("\n--- Getting aircraft by ESN ---")
    response = requests.get(f"{BASE_URL}/aircraft/esn/{aircraft_esn}")
    handle_response(response)
    
    # Get all aircraft for an operator
    print("\n--- Getting all aircraft for an operator ---")
    response = requests.get(f"{BASE_URL}/operators/{operator_id}/aircraft")
    handle_response(response)
    
    return aircraft_id

def test_pilots(operator_id):
    """Test pilot endpoints"""
    if not operator_id:
        print("No operator_id provided, skipping pilot tests")
        return None
        
    print("\n=== TESTING PILOT ENDPOINTS ===")
    
    # Create a new pilot
    print("\n--- Creating a new pilot ---")
    pilot_data = {
        "operator": operator_id,
        "is_active": True,
        "person": {
            "first_name": "John",
            "middle_name": "",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "phone_number": "+1234567890",
            "date_of_birth": "1985-01-15"
        },
        "address": {
            "address_line_1": "456 Pilot Avenue",
            "address_line_2": "Flying District",
            "address_line_3": "",
            "postcode": "PI12 3LT",
            "city": "Manchester",
            "country": "GB"
        }
    }
    
    print(f"Sending request to {BASE_URL}/pilots")
    print(f"Request data: {json.dumps(pilot_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/pilots", json=pilot_data, headers=HEADERS)
    pilot = handle_response(response)
    if not pilot or response.status_code != 201:
        print("Failed to create pilot, skipping related tests")
        return None
    
    pilot_id = pilot.get("id")
    
    # Get pilot details
    print("\n--- Getting pilot details ---")
    response = requests.get(f"{BASE_URL}/pilots/{pilot_id}")
    handle_response(response)
    
    # Get privileged pilot details
    print("\n--- Getting privileged pilot details ---")
    response = requests.get(f"{BASE_URL}/pilots/{pilot_id}/privilaged", headers=HEADERS)
    handle_response(response)
    
    return pilot_id

def test_contacts(operator_id):
    """Test contact endpoints"""
    if not operator_id:
        print("No operator_id provided, skipping contact tests")
        return None
        
    print("\n=== TESTING CONTACT ENDPOINTS ===")
    
    # Create a new contact
    print("\n--- Creating a new contact ---")
    contact_data = {
        "operator": operator_id,
        "role_type": 1,
        "person": {
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-05-20"
        },
        "address": {
            "address_line_1": "789 Contact Road",
            "address_line_2": "Support Area",
            "address_line_3": "",
            "postcode": "CO45 6NT",
            "city": "Birmingham",
            "country": "GB"
        }
    }
    
    print(f"Sending request to {BASE_URL}/contacts")
    print(f"Request data: {json.dumps(contact_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/contacts", json=contact_data, headers=HEADERS)
    contact = handle_response(response)
    if not contact or response.status_code != 201:
        print("Failed to create contact, skipping related tests")
        return None
    
    contact_id = contact.get("id")
    
    # Get contact details
    print("\n--- Getting contact details ---")
    response = requests.get(f"{BASE_URL}/contacts/{contact_id}")
    handle_response(response)
    
    # Get privileged contact details
    print("\n--- Getting privileged contact details ---")
    response = requests.get(f"{BASE_URL}/contacts/{contact_id}/privilaged", headers=HEADERS)
    handle_response(response)
    
    return contact_id

def test_manufacturers():
    """Test manufacturer endpoints"""
    print("\n=== TESTING MANUFACTURER ENDPOINTS ===")
    
    # List all manufacturers
    print("\n--- Listing all manufacturers ---")
    response = requests.get(f"{BASE_URL}/manufacturers")
    handle_response(response)
    return response.json() if response.status_code == 200 else []

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    # Test manufacturers first to get manufacturer data if needed
    manufacturers = test_manufacturers()
    
    # Test operators first to get an operator_id for other tests
    operator_id = test_operators()
    
    # Test other endpoints using the operator_id
    aircraft_id = test_aircraft(operator_id)
    pilot_id = test_pilots(operator_id)
    contact_id = test_contacts(operator_id)
    
    print("\nAPI tests completed!")

if __name__ == "__main__":
    main() 