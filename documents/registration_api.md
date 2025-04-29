# Aircraft Registry Registration API

This document outlines how to use the Aircraft Registry Registration API to register new Operators, Pilots, Aircraft, and Contacts.

## Authentication

All registration endpoints require authentication using Auth0 JWT tokens. Tokens should be included in the Authorization header of each request as follows:

```
Authorization: Bearer YOUR_AUTH0_TOKEN
```

Privileged endpoints require additional scopes in the JWT token. Specifically, endpoints with `/privileged` in the URL require the `read:privileged` scope.

## API Endpoints

### Operators

#### List all operators
```
GET /api/v1/operators
```

#### Create a new operator
```
POST /api/v1/operators
```

Example request body:
```json
{
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
```

#### Get operator details
```
GET /api/v1/operators/{operator_id}
```

#### Get privileged operator details
```
GET /api/v1/operators/{operator_id}/privilaged
```
Note: Requires `read:privileged` scope in JWT token.

#### Update operator
```
PUT /api/v1/operators/{operator_id}
```

#### Delete operator
```
DELETE /api/v1/operators/{operator_id}
```

#### Get all aircraft for an operator
```
GET /api/v1/operators/{operator_id}/aircraft
```

### Aircraft

#### List all aircraft
```
GET /api/v1/aircraft
```

#### Create a new aircraft
```
POST /api/v1/aircraft
```

Example request body:
```json
{
  "operator": "operator-uuid-here",
  "mass": 5,
  "manufacturer": "manufacturer-uuid-here",
  "model": "Phantom 4 Pro",
  "esn": "ESN123456789",
  "maci_number": "MACI123456",
  "registration_mark": "G-DRON",
  "aircraft_category": 2,
  "sub_category": 4,
  "is_airworthy": true,
  "icao_aircraft_type_designator": "UAV",
  "max_certified_takeoff_weight": 1.380,
  "year_of_manufacture": 2023,
  "status": 1
}
```

#### Get aircraft details
```
GET /api/v1/aircraft/{aircraft_id}
```

#### Get aircraft by ESN
```
GET /api/v1/aircraft/esn/{esn}
```

#### Update aircraft
```
PUT /api/v1/aircraft/{aircraft_id}
```

#### Delete aircraft
```
DELETE /api/v1/aircraft/{aircraft_id}
```

### Pilots

#### List all pilots
```
GET /api/v1/pilots
```

#### Create a new pilot
```
POST /api/v1/pilots
```

Example request body:
```json
{
  "operator": "operator-uuid-here",
  "is_active": true,
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
```

#### Get pilot details
```
GET /api/v1/pilots/{pilot_id}
```

#### Get privileged pilot details
```
GET /api/v1/pilots/{pilot_id}/privilaged
```
Note: Requires `read:privileged` scope in JWT token.

#### Update pilot
```
PUT /api/v1/pilots/{pilot_id}
```

#### Delete pilot
```
DELETE /api/v1/pilots/{pilot_id}
```

### Contacts

#### List all contacts
```
GET /api/v1/contacts
```

#### Create a new contact
```
POST /api/v1/contacts
```

Example request body:
```json
{
  "operator": "operator-uuid-here",
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
```

#### Get contact details
```
GET /api/v1/contacts/{contact_id}
```

#### Get privileged contact details
```
GET /api/v1/contacts/{contact_id}/privilaged
```
Note: Requires `read:privileged` scope in JWT token.

#### Update contact
```
PUT /api/v1/contacts/{contact_id}
```

#### Delete contact
```
DELETE /api/v1/contacts/{contact_id}
```

### Manufacturers

#### List all manufacturers
```
GET /api/v1/manufacturers
```

## Response Codes

- 200 OK: Request successful
- 201 Created: Resource created successfully
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Missing or invalid authentication token
- 403 Forbidden: Token does not have the required scope
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

## Data Validation

The API performs validation on all submitted data, including:
- Required fields must be filled
- Email fields must contain valid email format
- URLs must be in valid format
- Phone numbers must be in a valid format
- Entity IDs for relationships must reference existing entities

## Relationship Requirements

- Aircraft must be associated with an Operator (mandatory relationship)
- Pilots can be optionally associated with an Operator
- Contacts must be associated with an entity (in this case, an Operator) 