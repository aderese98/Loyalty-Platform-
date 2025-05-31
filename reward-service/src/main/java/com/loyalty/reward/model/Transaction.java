package com.loyalty.reward.model;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class Transaction {
    private UUID transactionId;
    private UUID userId;
    private BigDecimal amount;
    private String merchantId;
    private String category;
    private LocalDateTime timestamp;
    private String status;
}