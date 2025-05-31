from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import json
import boto3
import os
import uuid
from datetime import datetime, UTC
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(title="Transaction Service")

# Initialize AWS clients with environment-aware configuration
dynamodb = boto3.resource('dynamodb',
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT', None),  # None will use default AWS endpoint
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
)

sns = boto3.client('sns',
    endpoint_url=os.getenv('SNS_ENDPOINT', None),  # None will use default AWS endpoint
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
)

# Initialize Prometheus metrics
transaction_counter = Counter(
    'transaction_total',
    'Total number of transactions processed',
    ['status']
)

transaction_amount = Histogram(
    'transaction_amount',
    'Transaction amount distribution',
    buckets=[10, 50, 100, 500, 1000, 5000]
)

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

class Transaction(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)  # Amount must be positive
    merchant: str
    description: str = None
    category: str = None

    model_config = ConfigDict(
        json_encoders={
            float: lambda v: Decimal(str(v))
        }
    )

@app.post("/transactions")
async def create_transaction(transaction: Transaction):
    try:
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()
        
        # Create transaction record with Decimal amount
        transaction_record = {
            'transaction_id': transaction_id,
            'user_id': transaction.user_id,
            'amount': Decimal(str(transaction.amount)),  # Convert to Decimal
            'merchant': transaction.merchant,
            'description': transaction.description,
            'category': transaction.category,
            'timestamp': timestamp
        }
        
        # Store in DynamoDB
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'transactions'))
        table.put_item(Item=transaction_record)
        
        # Publish to SNS
        sns.publish(
            TopicArn=os.getenv('SNS_TOPIC_ARN'),
            Message=json.dumps(transaction_record, default=str)  # Handle Decimal serialization
        )
        
        # Record metrics
        transaction_counter.labels(status='success').inc()
        transaction_amount.observe(float(transaction.amount))  # Convert back to float for metrics
        
        # Log success
        logger.info(
            "transaction_processed",
            transaction_id=transaction_id,
            user_id=transaction.user_id,
            amount=float(transaction.amount),  # Convert back to float for logging
            merchant=transaction.merchant
        )
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "timestamp": timestamp
        }
        
    except Exception as e:
        # Record failure
        transaction_counter.labels(status='error').inc()
        
        # Log error
        logger.error(
            "transaction_failed",
            error=str(e),
            user_id=transaction.user_id,
            amount=float(transaction.amount)  # Convert back to float for logging
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return generate_latest() 