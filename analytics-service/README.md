# Reward Analytics Service

A daily batch analytics service for the Loyalty Rewards Platform that aggregates reward data and publishes metrics.

## Features

- Daily aggregation of rewards data
- DynamoDB integration for data querying
- S3 storage for analytics results
- CloudWatch metrics and logging
- Automated daily execution via CloudWatch Events

## Architecture

The service consists of:
1. AWS Lambda function for data processing
2. DynamoDB table for rewards data
3. S3 bucket for storing analytics results
4. CloudWatch Events for scheduling
5. CloudWatch Metrics for monitoring

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed
- Python 3.11+
- Access to AWS services (Lambda, DynamoDB, S3, CloudWatch)

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install boto3
   ```

3. Package the Lambda function:
   ```bash
   cd lambda
   zip -r reward_analytics.zip reward_analytics.py
   ```

## Deployment

1. Initialize Terraform:
   ```bash
   cd infra
   terraform init
   ```

2. Review the planned changes:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

## Infrastructure

The Terraform configuration creates:
- S3 bucket for analytics data
- IAM role and policy for Lambda
- Lambda function
- CloudWatch Event rule for daily execution
- Required permissions and attachments

## Monitoring

The service publishes the following metrics to CloudWatch:
- TotalIssuedRewards
- TotalRedeemedRewards
- NetRewards

Metrics are available in the CloudWatch console under the "LoyaltyPlatform/Rewards" namespace.

## Analytics Data

Daily analytics results are stored in S3 with the following structure:
```
s3://loyalty-platform-analytics/daily-rewards/YYYY-MM-DD.json
```

Example analytics data:
```json
{
  "date": "2023-11-15",
  "total_issued": 1500.0,
  "total_redeemed": 750.0,
  "net_rewards": 750.0,
  "issued_count": 15,
  "redeemed_count": 8
}
```

## Cleanup

To remove all created resources:
```bash
cd infra
terraform destroy
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request 