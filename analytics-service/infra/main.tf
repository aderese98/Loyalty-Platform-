provider "aws" {
  region = var.aws_region
}

# S3 bucket for analytics data
resource "aws_s3_bucket" "analytics" {
  bucket = "loyalty-platform-analytics"
}

resource "aws_s3_bucket_versioning" "analytics" {
  bucket = aws_s3_bucket.analytics.id
  versioning_configuration {
    status = "Enabled"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "analytics_lambda_role" {
  name = "analytics_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda
resource "aws_iam_policy" "analytics_lambda_policy" {
  name        = "analytics_lambda_policy"
  description = "Policy for analytics Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/rewards",
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/rewards/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.analytics.arn,
          "${aws_s3_bucket.analytics.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "analytics_lambda_policy_attachment" {
  role       = aws_iam_role.analytics_lambda_role.name
  policy_arn = aws_iam_policy.analytics_lambda_policy.arn
}

# Lambda function
resource "aws_lambda_function" "analytics" {
  filename         = "../lambda/reward_analytics.zip"
  function_name    = "reward-analytics"
  role            = aws_iam_role.analytics_lambda_role.arn
  handler         = "reward_analytics.lambda_handler"
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      REWARDS_TABLE = "rewards"
      S3_BUCKET     = aws_s3_bucket.analytics.id
      S3_PREFIX     = "daily-rewards"
    }
  }
}

# CloudWatch Event Rule
resource "aws_cloudwatch_event_rule" "daily_analytics" {
  name                = "daily-reward-analytics"
  description         = "Trigger reward analytics Lambda daily"
  schedule_expression = "cron(0 0 * * ? *)"  # Run at midnight UTC daily
}

# CloudWatch Event Target
resource "aws_cloudwatch_event_target" "analytics_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_analytics.name
  target_id = "AnalyticsLambda"
  arn       = aws_lambda_function.analytics.arn
}

# Lambda permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_analytics.arn
}

# SQS trigger for batch analytics Lambda
resource "aws_lambda_event_source_mapping" "batch_analytics_sqs_trigger" {
  event_source_arn = aws_sqs_queue.batch_analytics_queue.arn
  function_name    = aws_lambda_function.analytics.arn
  batch_size       = 10
  enabled          = true
}

# Update Lambda IAM role to include SQS permissions
resource "aws_iam_role_policy_attachment" "batch_analytics_sqs_policy_attachment" {
  role       = aws_iam_role.analytics_lambda_role.name
  policy_arn = aws_iam_policy.batch_analytics_sqs_policy.arn
}

# Get current AWS account ID
data "aws_caller_identity" "current" {} 