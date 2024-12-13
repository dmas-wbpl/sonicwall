# SonicWall API Authentication Service

This service implements secure authentication for the SonicWall API using RFC-7616 HTTP Digest Access Authentication.

## Features

- RFC-7616 HTTP Digest Access Authentication
- Single administrator session management
- Session tracking and expiration
- Secure password handling
- PostgreSQL database backend

## Security Features

- SHA-256 support for enhanced security
- Protection against replay attacks
- Session management
- HTTPS requirement
- Single administrator restriction

## Prerequisites

- Python 3.11+
- PostgreSQL
- Poetry (optional, for dependency management)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=sonicwall
SECRET_KEY=your_secret_key
SQL_DEBUG=false
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication Endpoints

### Login
```
POST /api/sonicos/auth
```

### Logout
```
DELETE /api/sonicos/auth
```

## Security Notes

- Only one administrator can be logged in at a time
- Only users with full admin privileges are allowed
- All connections must be made over HTTPS
- Sessions expire after 1 hour of inactivity 