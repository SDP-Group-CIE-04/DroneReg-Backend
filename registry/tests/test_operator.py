import requests
import json
import jwt
from datetime import datetime, timedelta

def generate_test_token():
    # Create a simple test token that will be accepted by the backend
    payload = {
        'email': 'test@example.com',
        'exp': int((datetime.utcnow() + timedelta(days=1)).timestamp())
    }
    # Using a simple token format for PyJWT 1.7.1
    token = jwt.encode(payload, 'test-secret', algorithm='HS256')
    # In PyJWT 1.7.1, encode returns bytes, so we need to decode to str
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def test_create_operator():
    # API endpoint
    url = 'http://localhost:8000/api/v1/operators'
    
    # Test data for a new operator
    operator_data = {
        "company_name": "Test Drone Company",
        "website": "https://testdronecompany.com",
        "email": "contact@testdronecompany.com",
        "phone_number": "1234567890",
        "operator_type": 2,  # 2 = Non-LUC
        "vat_number": "VAT123456",
        "insurance_number": "INS123456",
        "company_number": "COMP123456",
        "country": "AE",
        "address": {
            "address_line_1": "123 Drone Street",
            "address_line_2": "Innovation District",
            "address_line_3": "-",
            "postcode": "12345",
            "city": "Abu Dhabi",
            "country": "UAE"  # Backend will convert to AE
        }
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {generate_test_token()}'
    }
    
    try:
        # Make the POST request
        response = requests.post(url, json=operator_data, headers=headers)
        
        # Print the response status and content
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

if __name__ == "__main__":
    test_create_operator()
