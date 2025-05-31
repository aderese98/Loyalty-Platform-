# Loyalty Platform

A microservices-based loyalty platform that enables businesses to manage customer loyalty programs, track transactions, and provide personalized rewards.

## Architecture

The platform consists of the following microservices:

- **User Service** (Go): Manages user profiles and authentication
- **Transaction Service** (Python): Processes transactions and calculates loyalty points
- **Reward Service** (Java): Manages rewards and redemption
- **Recommendation Service** (Python): Provides AI-powered reward recommendations

### Tech Stack

- **Languages**: Go, Python, Java
- **Databases**: PostgreSQL, DynamoDB
- **Message Queue**: AWS SQS
- **Event Bus**: AWS SNS
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Go 1.21+
- Python 3.9+
- Java 17+
- Maven

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/loyalty-platform.git
cd loyalty-platform
```

2. Start the services:
```bash
docker-compose up -d
```

3. Verify the services are running:
```bash
docker-compose ps
```

## Usage Flow

### 1. User Registration and Profile Management

```bash
# Create a new user
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }'

# Get user profile
curl http://localhost:8080/api/v1/users/123

# Update user profile
curl -X PUT http://localhost:8080/api/v1/users/123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "phone": "+1987654321"
  }'
```

### 2. Transaction Processing

```bash
# Record a transaction
curl -X POST http://localhost:8082/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "123",
    "amount": 100.50,
    "merchantId": "M456",
    "category": "RETAIL"
  }'
```

### 3. Reward Management

```bash
# Get available rewards
curl http://localhost:8081/api/v1/rewards

# Redeem a reward
curl -X POST http://localhost:8081/api/v1/rewards/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "123",
    "rewardId": "R789",
    "points": 1000
  }'
```

### 4. Get Personalized Recommendations

```bash
# Get reward recommendations
curl http://localhost:8083/api/v1/recommendations/123
```

## Test Cases

### User Service Tests

```bash
# Run User Service tests
cd user-service
go test ./...

# Test user creation
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com"
  }'

# Test user retrieval
curl http://localhost:8080/api/v1/users/1

# Test user update
curl -X PUT http://localhost:8080/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated User"
  }'

# Test user deletion
curl -X DELETE http://localhost:8080/api/v1/users/1
```

### Transaction Service Tests

```bash
# Run Transaction Service tests
cd transaction-service
pytest

# Test transaction creation
curl -X POST http://localhost:8082/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "1",
    "amount": 50.00,
    "merchantId": "M1",
    "category": "RETAIL"
  }'

# Test transaction retrieval
curl http://localhost:8082/api/v1/transactions/1
```

### Reward Service Tests

```bash
# Run Reward Service tests
cd reward-service
mvn test

# Test reward creation
curl -X POST http://localhost:8081/api/v1/rewards \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Free Coffee",
    "points": 100,
    "description": "Get a free coffee"
  }'

# Test reward redemption
curl -X POST http://localhost:8081/api/v1/rewards/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "1",
    "rewardId": "1",
    "points": 100
  }'
```

## Monitoring

### Prometheus

Access Prometheus metrics at http://localhost:9090

Key metrics:
- HTTP request duration
- Request count by endpoint
- Error rates
- Transaction volume
- Reward redemption rate

### Grafana

Access Grafana dashboards at http://localhost:3000 (admin/admin)

Available dashboards:
- Service Overview
- Transaction Analytics
- User Activity
- Reward Performance

## Development

### Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/new-feature
```

2. Make your changes
3. Run tests:
```bash
./tests/run_tests.sh
```

4. Submit a pull request

### Code Style

- Go: Follow [Effective Go](https://golang.org/doc/effective_go)
- Python: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Java: Follow [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 