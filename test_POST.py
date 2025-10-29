import requests
import uuid
import json

BASE_URL = "http://localhost:8000/api/v1"

# Prebuilt JWT that the backend accepts (no verification performed server-side)
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzY29wZSI6InJlYWQ6cHJpdmlsZWdlZCJ9.KOegGEpI-PyT9K91sEfrd-eqQ0L_xcXQjk_LG1jNHwk"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MOCK_TOKEN}",
}

def get_or_create_operator_id():
    # Try to use an existing operator first
    try:
        resp = requests.get(f"{BASE_URL}/operators")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get("id")
    except Exception:
        pass

    # Create a minimal operator if none exists
    data = {
        "company_name": "Temp Operator",
        "website": "https://temp.example.com",
        "email": "temp@example.com",
        "phone_number": "+10000000000",
        "operator_type": 1,
        "vat_number": "GB000000000",
        "insurance_number": "INS-TEMP",
        "company_number": "COMP-TEMP",
        "country": "GB",
        "address": {
            "address_line_1": "1 Temp Street",
            "address_line_2": "",
            "address_line_3": "",
            "postcode": "T1 1TT",
            "city": "London",
            "country": "GB"
        }
    }
    r = requests.post(f"{BASE_URL}/operators", json=data, headers=HEADERS)
    print("Temp operator status:", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    return (r.json() or {}).get("id") if r.status_code == 201 else None

def post_pilot(operator_id):
    data = {
        "operator": operator_id,
        "is_active": True,
        "person": {
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-05-20"
        },
        "address": {
            "address_line_1": "456 Pilot Avenue",
            "address_line_2": "-",
            "address_line_3": "-",
            "postcode": "PI12 3LT",
            "city": "Manchester",
            "country": "GB"
        }
    }
    r = requests.post(f"{BASE_URL}/pilots", json=data, headers=HEADERS)
    print("Pilot status:", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)

if __name__ == "__main__":
    operator_id = get_or_create_operator_id()
    if operator_id:
        post_pilot(operator_id)
    else:
        print("No operator available; cannot create pilot.")