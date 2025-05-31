# Transaction Service

A FastAPI microservice for processing purchase transactions and publishing reward events.

## Features

- Process purchase transactions
- Store transactions in DynamoDB
- Publish reward events to SNS
- RESTful API endpoints
- Docker containerization
- Unit tests with mocked AWS services

## API Endpoints

### Create Transaction
```http
POST /transactions
Content-Type: application/json

{
    "user_id": "user123",
    "amount": 100.50,
    "merchant": "Store Name",
    "description": "Purchase description",
    "category": "Retail"
}
```

### Health Check
```http
GET /health
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS Account with appropriate permissions
- AWS CLI configured locally

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Service Configuration
DYNAMODB_TABLE=transactions
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:reward-events
```

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Docker

Build and run with Docker:
```bash
docker build -t transaction-service .
docker run -p 8000:8000 --env-file .env transaction-service
```

## AWS Setup

1. Create DynamoDB Table:
   ```bash
   aws dynamodb create-table \
       --table-name transactions \
       --attribute-definitions AttributeName=transaction_id,AttributeType=S \
       --key-schema AttributeName=transaction_id,KeyType=HASH \
       --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
   ```

2. Create SNS Topic:
   ```bash
   aws sns create-topic --name reward-events
   ```

## API Response Examples

### Successful Transaction
```json
{
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "success",
    "timestamp": "2023-11-15T10:00:00Z"
}
```

### Error Response
```json
{
    "detail": "Error message"
}
```

## Error Codes

- 400: Bad Request
- 422: Validation Error
- 500: Internal Server Error

## Testing

The service includes unit tests that mock AWS services using the `moto` library. To run the tests:

```bash
pytest
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request 