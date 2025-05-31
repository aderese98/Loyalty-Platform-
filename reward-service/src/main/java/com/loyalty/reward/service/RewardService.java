package com.loyalty.reward.service;

import com.loyalty.reward.model.Transaction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class RewardService {
    private static final Logger logger = LoggerFactory.getLogger(RewardService.class);

    public void processTransaction(Transaction transaction) {
        logger.info("Processing transaction: {}", transaction.getTransactionId());
        // TODO: Implement reward calculation logic
        // For now, just log the transaction
    }
}