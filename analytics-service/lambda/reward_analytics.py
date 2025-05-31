import json
import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

# Constants
REWARDS_TABLE = 'rewards'
S3_BUCKET = 'loyalty-platform-analytics'
S3_PREFIX = 'daily-rewards'

def get_yesterday_date() -> str:
    """Get yesterday's date in YYYY-MM-DD format."""
    yesterday = datetime.utcnow() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')

def aggregate_rewards(date: str) -> Dict[str, Any]:
    """Aggregate rewards data for the given date."""
    table = dynamodb.Table(REWARDS_TABLE)
    
    # Query for issued rewards
    issued_rewards = table.query(
        IndexName='status-date-index',
        KeyConditionExpression='#status = :status AND #date = :date',
        ExpressionAttributeNames={
            '#status': 'status',
            '#date': 'date'
        },
        ExpressionAttributeValues={
            ':status': 'ISSUED',
            ':date': date
        }
    )
    
    # Query for redeemed rewards
    redeemed_rewards = table.query(
        IndexName='status-date-index',
        KeyConditionExpression='#status = :status AND #date = :date',
        ExpressionAttributeNames={
            '#status': 'status',
            '#date': 'date'
        },
        ExpressionAttributeValues={
            ':status': 'REDEEMED',
            ':date': date
        }
    )
    
    # Calculate totals
    total_issued = sum(float(item['points']) for item in issued_rewards.get('Items', []))
    total_redeemed = sum(float(item['points']) for item in redeemed_rewards.get('Items', []))
    
    return {
        'date': date,
        'total_issued': total_issued,
        'total_redeemed': total_redeemed,
        'net_rewards': total_issued - total_redeemed,
        'issued_count': len(issued_rewards.get('Items', [])),
        'redeemed_count': len(redeemed_rewards.get('Items', []))
    }

def write_to_s3(data: Dict[str, Any], date: str) -> None:
    """Write analytics data to S3."""
    key = f"{S3_PREFIX}/{date}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType='application/json'
    )
    logger.info(f"Successfully wrote analytics data to s3://{S3_BUCKET}/{key}")

def put_metrics(data: Dict[str, Any]) -> None:
    """Put metrics to CloudWatch."""
    cloudwatch.put_metric_data(
        Namespace='LoyaltyPlatform/Rewards',
        MetricData=[
            {
                'MetricName': 'TotalIssuedRewards',
                'Value': data['total_issued'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Date', 'Value': data['date']}
                ]
            },
            {
                'MetricName': 'TotalRedeemedRewards',
                'Value': data['total_redeemed'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Date', 'Value': data['date']}
                ]
            },
            {
                'MetricName': 'NetRewards',
                'Value': data['net_rewards'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Date', 'Value': data['date']}
                ]
            }
        ]
    )
    logger.info("Successfully published metrics to CloudWatch")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler function."""
    try:
        # Get yesterday's date
        date = get_yesterday_date()
        logger.info(f"Processing analytics for date: {date}")
        
        # Aggregate rewards data
        analytics_data = aggregate_rewards(date)
        logger.info(f"Aggregated data: {json.dumps(analytics_data)}")
        
        # Write to S3
        write_to_s3(analytics_data, date)
        
        # Put metrics to CloudWatch
        put_metrics(analytics_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analytics processing completed successfully',
                'data': analytics_data
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing analytics: {str(e)}")
        raise 