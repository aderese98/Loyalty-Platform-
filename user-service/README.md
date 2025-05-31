# User Service

A microservice for managing user profiles in the Loyalty Rewards Platform.

## Features

- User profile management (CRUD operations)
- Email uniqueness validation
- PostgreSQL database integration
- RESTful API endpoints
- Docker containerization
- Unit tests

## API Endpoints

### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St"
}
```

### Get User
```http
GET /api/v1/users/{id}
```

### Update User
```http
PUT /api/v1/users/{id}
Content-Type: application/json

{
    "email": "updated@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "phone": "0987654321",
    "address": "456 Oak St"
}
```

### Delete User
```http
DELETE /api/v1/users/{id}
```

## Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Prerequisites

- Go 1.21+
- PostgreSQL 15+
- Docker and Docker Compose

## Environment Variables

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=user_service
PORT=8080
```

## Local Development

1. Install dependencies:
   ```bash
   go mod download
   ```

2. Run the service:
   ```bash
   go run main.go
   ```

3. Run tests:
   ```bash
   go test ./...
   ```

## Docker

Build and run with Docker:
```bash
docker build -t user-service .
docker run -p 8080:8080 user-service
```

## API Response Examples

### Create User Response
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St",
    "created_at": "2023-11-15T10:00:00Z",
    "updated_at": "2023-11-15T10:00:00Z"
}
```

### Error Response
```json
{
    "error": "user with this email already exists"
}
```

## Error Codes

- 400: Bad Request
- 404: User Not Found
- 409: Conflict (e.g., email already exists)
- 500: Internal Server Error 