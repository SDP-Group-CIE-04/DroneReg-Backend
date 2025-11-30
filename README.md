## Drone Registry Backend

A Django REST API backend for managing drone/UAS (Unmanned Aircraft Systems) registrations, operators, pilots, and Remote ID (RID) modules. This system provides a comprehensive registry for tracking aircraft, operators, and their associated metadata.

### Features

- **Operator Management**: Register and manage drone operators with company details, addresses, and authorizations
- **Aircraft Registration**: Track registered aircraft with ESN, MACI numbers, and type certificates
- **Pilot Management**: Manage remote pilots with competency tests and validity tracking
- **Remote ID Module Support**: Track and manage RID modules with activation status and lifecycle management
- **RESTful API**: Full REST API with browsable interface
- **Authentication & Authorization**: JWT-based authentication with privileged access controls
- **Reference Data**: Manufacturer and activity type management

### API Endpoints

The API provides endpoints for:
- Operators (`/api/v1/operators`)
- Aircraft (`/api/v1/aircraft`)
- Pilots (`/api/v1/pilots`)
- Contacts (`/api/v1/contacts`)
- RID Modules (`/api/v1/rid-modules`)
- Manufacturers (`/api/v1/manufacturers`)

See the API documentation at `/api/v1/` when running the server.

## Technical Details / Installation

This is a Django project using Django REST Framework for building the API. 

### Prerequisites

- Python 3.7+
- pip
- (Optional) PostgreSQL for production use
- (Optional) Docker and Docker Compose for containerized deployment

### Local Development Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Create Initial Database

Run migrations to create the database schema. By default, it uses SQLite:

```bash
python manage.py migrate
```

#### 3. Populate Initial Data (Optional)

Load sample data for testing:

```bash
python manage.py loaddata registry/defaultregistrydata.json
```

#### 4. Create Superuser (Optional)

Create an admin user to access the Django admin interface:

```bash
python manage.py createsuperuser
```

#### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at:
- API Explorer: http://localhost:8000/api/v1/
- Django Admin: http://localhost:8000/admin/

### Docker Deployment

For production deployment using Docker:

1. Create a `.env` file with your configuration (see `docker-compose.yml` for required variables)
2. Build and run with Docker Compose:

```bash
docker-compose up -d
```

The API will be available at http://localhost:8001/

### Environment Variables

Key environment variables you can configure:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `BYPASS_AUTHENTICATION`: Set to `True` to disable authentication (testing only)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

### Project Structure

- `registry/`: Main application containing models, views, serializers
- `ohio/`: Django project settings and URL configuration
- `documents/`: API documentation and white papers
- `tools/`: Utility scripts
- `migrations/`: Database migration files
