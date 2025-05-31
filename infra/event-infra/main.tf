provider "aws" {
  region = var.aws_region
}

# SNS Topic for reward events
resource "aws_sns_topic" "reward_events" {
  name = "reward-events"
}

# SQS Queue for reward service
resource "aws_sqs_queue" "reward_service_queue" {
  name                      = "reward-service-queue"
  visibility_timeout_seconds = 300
  message_retention_seconds = 345600  # 4 days
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.reward_service_dlq.arn
    maxReceiveCount     = 3
  })
}

# Dead Letter Queue for reward service
resource "aws_sqs_queue" "reward_service_dlq" {
  name = "reward-service-dlq"
}

# SQS Queue for batch analytics
resource "aws_sqs_queue" "batch_analytics_queue" {
  name                      = "batch-analytics-queue"
  visibility_timeout_seconds = 300
  message_retention_seconds = 345600  # 4 days
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.batch_analytics_dlq.arn
    maxReceiveCount     = 3
  })
}

# Dead Letter Queue for batch analytics
resource "aws_sqs_queue" "batch_analytics_dlq" {
  name = "batch-analytics-dlq"
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "reward_events_policy" {
  arn = aws_sns_topic.reward_events.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = [
          "sqs:SendMessage"
        ]
        Resource = [
          aws_sqs_queue.reward_service_queue.arn,
          aws_sqs_queue.batch_analytics_queue.arn
        ]
        Condition = {
          ArnLike = {
            "aws:SourceArn": aws_sns_topic.reward_events.arn
          }
        }
      }
    ]
  })
}

# SNS to SQS subscriptions
resource "aws_sns_topic_subscription" "reward_service_subscription" {
  topic_arn = aws_sns_topic.reward_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.reward_service_queue.arn
}

resource "aws_sns_topic_subscription" "batch_analytics_subscription" {
  topic_arn = aws_sns_topic.reward_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.batch_analytics_queue.arn
}

# IAM policy for reward service
resource "aws_iam_policy" "reward_service_sqs_policy" {
  name        = "reward-service-sqs-policy"
  description = "Policy for reward service to consume SQS messages"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = [
          aws_sqs_queue.reward_service_queue.arn,
          aws_sqs_queue.reward_service_dlq.arn
        ]
      }
    ]
  })
}

# IAM policy for batch analytics Lambda
resource "aws_iam_policy" "batch_analytics_sqs_policy" {
  name        = "batch-analytics-sqs-policy"
  description = "Policy for batch analytics Lambda to consume SQS messages"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = [
          aws_sqs_queue.batch_analytics_queue.arn,
          aws_sqs_queue.batch_analytics_dlq.arn
        ]
      }
    ]
  })
} 