import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb, mock_sns
import boto3
import os
import json
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def dynamodb(aws_credentials):
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb')
        # Create the DynamoDB table
        table = dynamodb.create_table(
            TableName='transactions',
            KeySchema=[
                {'AttributeName': 'transaction_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'transaction_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        yield dynamodb

@pytest.fixture
def sns(aws_credentials):
    with mock_sns():
        sns = boto3.client('sns')
        # Create the SNS topic
        topic = sns.create_topic(Name='reward-events')
        os.environ['SNS_TOPIC_ARN'] = topic['TopicArn']
        yield sns

def test_create_transaction(client, dynamodb, sns):
    transaction_data = {
        "user_id": "user123",
        "amount": 100.50,
        "merchant": "Test Store",
        "description": "Test purchase",
        "category": "Retail"
    }

    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "transaction_id" in data
    assert "status" in data
    assert data["status"] == "success"
    assert "timestamp" in data

def test_create_transaction_invalid_amount(client):
    transaction_data = {
        "user_id": "user123",
        "amount": -50.00,  # Invalid negative amount
        "merchant": "Test Store"
    }

    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == 422  # Validation error

def test_create_transaction_missing_required_fields(client):
    transaction_data = {
        "user_id": "user123"
        # Missing required fields: amount and merchant
    }

    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == 422  # Validation error

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 