import json
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Constants
REWARDS_TABLE = 'rewards'
METRICS_NAMESPACE = 'LoyaltyPlatform/Rewards'

def process_transaction(transaction: Dict[str, Any]) -> None:
    """Process a single transaction and update analytics."""
    try:
        # Extract transaction details
        user_id = transaction['user_id']
        amount = float(transaction['amount'])
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate reward points (example: 1 point per $1)
        points = int(amount)
        
        # Store reward record
        table = dynamodb.Table(REWARDS_TABLE)
        table.put_item(
            Item={
                'user_id': user_id,
                'points': points,
                'status': 'ISSUED',
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'timestamp': timestamp,
                'transaction_id': transaction.get('transaction_id', ''),
                'merchant': transaction.get('merchant', ''),
                'category': transaction.get('category', '')
            }
        )
        
        # Put metric for real-time tracking
        cloudwatch.put_metric_data(
            Namespace=METRICS_NAMESPACE,
            MetricData=[
                {
                    'MetricName': 'RewardPointsIssued',
                    'Value': points,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'UserId', 'Value': user_id},
                        {'Name': 'Merchant', 'Value': transaction.get('merchant', 'Unknown')}
                    ]
                }
            ]
        )
        
        logger.info(f"Processed transaction for user {user_id}: {points} points issued")
        
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler function."""
    try:
        # Process each record from SQS
        for record in event['Records']:
            # Parse SNS message
            sns_message = json.loads(record['body'])
            transaction = json.loads(sns_message['Message'])
            
            # Process the transaction
            process_transaction(transaction)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(event["Records"])} transactions'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing SQS messages: {str(e)}")
        raise 