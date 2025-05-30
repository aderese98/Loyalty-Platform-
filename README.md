# Loyalty Rewards Platform

A microservices-based platform for managing customer loyalty programs and rewards.

## Architecture Overview

The platform consists of the following microservices:

- **User Service** (Go)
  - Manages user profiles, authentication, and authorization
  - Handles user preferences and settings
  - REST API with gRPC support

- **Reward Service** (Java)
  - Manages reward points, tiers, and redemption
  - Handles reward rules and eligibility
  - Spring Boot application with REST API

- **Transaction Service** (Python)
  - Processes transactions and point calculations
  - Handles purchase history and point accrual
  - FastAPI application with async support

- **Batch Analytics** (Python AWS Lambda)
  - Generates reports and analytics
  - Processes historical data
  - Runs on AWS Lambda with scheduled triggers

## Infrastructure

- Terraform configurations for AWS infrastructure
- Docker Compose for local development
- GitHub Actions for CI/CD pipelines

## Prerequisites

- Go 1.21+
- Java 17+
- Python 3.11+
- Docker and Docker Compose
- Terraform 1.5+
- AWS CLI (for deployment)

## Getting Started

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/loyalty-platform.git
   cd loyalty-platform
   ```

2. Start all services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Building Individual Services

#### User Service (Go)
```bash
cd user-service
go mod download
go build
```

#### Reward Service (Java)
```bash
cd reward-service
./mvnw clean install
```

#### Transaction Service (Python)
```bash
cd transaction-service
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

#### Batch Analytics (Python)
```bash
cd batch-analytics
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## Testing

Run the shared test suite:
```bash
cd tests
./run_tests.sh
```

## Deployment

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Deploy infrastructure:
   ```bash
   cd infra
   terraform init
   terraform apply
   ```

3. Deploy services:
   ```bash
   # Each service has its own deployment script
   ./deploy.sh
   ```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details 