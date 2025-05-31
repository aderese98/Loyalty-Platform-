package com.loyalty.reward.consumer;

import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.loyalty.reward.model.Transaction;
import com.loyalty.reward.service.RewardService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Component
public class TransactionConsumer {
    private static final Logger logger = LoggerFactory.getLogger(TransactionConsumer.class);
    private static final int MAX_NUMBER_OF_MESSAGES = 10;
    private static final int WAIT_TIME_SECONDS = 20;
    private static final int VISIBILITY_TIMEOUT = 300;

    @Value("${aws.sqs.queue.url}")
    private String queueUrl;

    private final AmazonSQS sqsClient;
    private final RewardService rewardService;
    private final ObjectMapper objectMapper;
    private final ExecutorService executorService;

    @Autowired
    public TransactionConsumer(RewardService rewardService) {
        this.sqsClient = AmazonSQSClientBuilder.defaultClient();
        this.rewardService = rewardService;
        this.objectMapper = new ObjectMapper();
        this.executorService = Executors.newFixedThreadPool(5);
    }

    @Scheduled(fixedDelay = 1000)
    public void pollMessages() {
        try {
            ReceiveMessageRequest receiveRequest = new ReceiveMessageRequest()
                .withQueueUrl(queueUrl)
                .withMaxNumberOfMessages(MAX_NUMBER_OF_MESSAGES)
                .withWaitTimeSeconds(WAIT_TIME_SECONDS)
                .withVisibilityTimeout(VISIBILITY_TIMEOUT);

            ReceiveMessageResult receiveResult = sqsClient.receiveMessage(receiveRequest);
            List<Message> messages = receiveResult.getMessages();

            if (!messages.isEmpty()) {
                logger.info("Received {} messages from SQS", messages.size());
                processMessages(messages);
            }
        } catch (Exception e) {
            logger.error("Error polling messages from SQS", e);
        }
    }

    private void processMessages(List<Message> messages) {
        for (Message message : messages) {
            executorService.submit(() -> processMessage(message));
        }
    }

    private void processMessage(Message message) {
        try {
            // Parse SNS message
            String snsMessage = message.getBody();
            String transactionJson = extractTransactionJson(snsMessage);
            
            // Parse transaction
            Transaction transaction = objectMapper.readValue(transactionJson, Transaction.class);
            
            // Process transaction and update rewards
            rewardService.processTransaction(transaction);
            
            // Delete message from queue
            deleteMessage(message);
            
            logger.info("Successfully processed transaction: {}", transaction.getTransactionId());
        } catch (Exception e) {
            logger.error("Error processing message: {}", message.getMessageId(), e);
            // Message will return to queue after visibility timeout
        }
    }

    private String extractTransactionJson(String snsMessage) throws Exception {
        // Parse SNS message to get the actual transaction JSON
        return objectMapper.readTree(snsMessage)
            .get("Message")
            .asText();
    }

    private void deleteMessage(Message message) {
        try {
            DeleteMessageRequest deleteRequest = new DeleteMessageRequest()
                .withQueueUrl(queueUrl)
                .withReceiptHandle(message.getReceiptHandle());
            
            sqsClient.deleteMessage(deleteRequest);
        } catch (Exception e) {
            logger.error("Error deleting message from SQS", e);
        }
    }
} 