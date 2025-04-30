import requests
import json
import jwt
import uuid
from datetime import datetime, timedelta
from registry.tests.test_operator import generate_test_token, test_create_operator

def test_create_aircraft():
    # First create an operator to get the operator ID
    operator_response = test_create_operator()
    if not operator_response:
        print("Failed to create operator")
        return None
    
    print("Operator created successfully:", json.dumps(operator_response, indent=2))
    
    # Get operator UUID from the API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {generate_test_token()}'
    }
    
    # First get the operator's UUID
    operators_url = 'http://localhost:8000/api/v1/operators'
    try:
        response = requests.get(operators_url, headers=headers)
        operators = response.json() if response.status_code == 200 else []
        
        # Find our operator by company name
        operator_id = None
        for operator in operators:
            if operator.get('company_name') == "Test Drone Company":
                operator_id = operator.get('id')
                break
        
        if not operator_id:
            print("Could not find operator UUID")
            return None
            
        print(f"Found operator UUID: {operator_id}")
        
        # Now get a manufacturer ID
        manufacturers_url = 'http://localhost:8000/api/v1/manufacturers'
        response = requests.get(manufacturers_url, headers=headers)
        manufacturers = response.json() if response.status_code == 200 else []
        manufacturer_id = manufacturers[0].get("id") if manufacturers else None
        
        if not manufacturer_id:
            print("No manufacturer found, cannot create aircraft")
            return None
        
        # Test data for a new aircraft based on requirements
        aircraft_data = {
            "operator": operator_id,  # Use the operator UUID
            "mass": 25,  # Integer value in kg
            "model": "DJI Mavic 3",
            "esn": f"ESN{uuid.uuid4().hex[:10].upper()}",
            "maci_number": f"MACI{uuid.uuid4().hex[:8].upper()}",
            "registration_mark": "UAE-DR123",
            "category": 2,  # 2 = ROTORCRAFT
            "sub_category": 4,  # 4 = HELICOPTER
            "is_airworthy": True,
            "icao_type": "UAV",
            "max_takeoff_weight": 30,
            "status": 1,  # 1 = Active
            "manufacturer": manufacturer_id
        }
        
        # API endpoint for aircraft
        url = 'http://localhost:8000/api/v1/aircraft'
        
        # Make the POST request
        response = requests.post(url, json=aircraft_data, headers=headers)
        
        # Print the response status and content
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

if __name__ == "__main__":
    test_create_aircraft()
