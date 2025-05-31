from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
import logging
from typing import List, Dict
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="Reward Recommendation Service")

# Load the pre-trained model
MODEL_PATH = os.getenv('MODEL_PATH', 'models/reward_model.joblib')
try:
    model = joblib.load(MODEL_PATH)
    logger.info("model_loaded", model_path=MODEL_PATH)
except Exception as e:
    logger.error("model_load_failed", error=str(e))
    model = None

class TransactionHistory(BaseModel):
    total_spent: float
    transaction_count: int
    avg_transaction: float
    category_distribution: Dict[str, float]

class RewardRecommendation(BaseModel):
    reward_id: str
    reward_name: str
    points_required: int
    confidence_score: float
    description: str

def get_user_transaction_history(user_id: str) -> TransactionHistory:
    """
    Mock function to get user transaction history.
    In a real implementation, this would fetch data from the transaction service.
    """
    # Example data
    return TransactionHistory(
        total_spent=1500.0,
        transaction_count=15,
        avg_transaction=100.0,
        category_distribution={
            "groceries": 0.4,
            "dining": 0.3,
            "shopping": 0.2,
            "entertainment": 0.1
        }
    )

def generate_recommendations(transaction_history: TransactionHistory) -> List[RewardRecommendation]:
    """
    Generate reward recommendations based on transaction history.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Prepare features for the model
    features = np.array([
        transaction_history.total_spent,
        transaction_history.transaction_count,
        transaction_history.avg_transaction,
        transaction_history.category_distribution.get("groceries", 0),
        transaction_history.category_distribution.get("dining", 0),
        transaction_history.category_distribution.get("shopping", 0),
        transaction_history.category_distribution.get("entertainment", 0)
    ]).reshape(1, -1)

    # Get predictions from the model
    predictions = model.predict_proba(features)[0]

    # Example reward catalog
    rewards = [
        {"id": "R1", "name": "Grocery Store Gift Card", "points": 1000, "description": "$50 gift card for grocery shopping"},
        {"id": "R2", "name": "Restaurant Voucher", "points": 1500, "description": "$75 dining voucher"},
        {"id": "R3", "name": "Shopping Mall Gift Card", "points": 2000, "description": "$100 shopping mall gift card"},
        {"id": "R4", "name": "Movie Tickets", "points": 500, "description": "2 movie tickets with popcorn"},
    ]

    # Generate recommendations based on predictions
    recommendations = []
    for reward, confidence in zip(rewards, predictions):
        recommendations.append(RewardRecommendation(
            reward_id=reward["id"],
            reward_name=reward["name"],
            points_required=reward["points"],
            confidence_score=float(confidence),
            description=reward["description"]
        ))

    return sorted(recommendations, key=lambda x: x.confidence_score, reverse=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/recommendations/{user_id}", response_model=List[RewardRecommendation])
async def get_recommendations(user_id: str):
    try:
        # Get user's transaction history
        transaction_history = get_user_transaction_history(user_id)
        
        # Generate recommendations
        recommendations = generate_recommendations(transaction_history)
        
        logger.info(
            "recommendations_generated",
            user_id=user_id,
            recommendation_count=len(recommendations)
        )
        
        return recommendations
    except Exception as e:
        logger.error(
            "recommendation_failed",
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 