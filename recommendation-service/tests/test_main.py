import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_recommendations():
    user_id = "test123"
    response = client.get(f"/recommendations/{user_id}")
    assert response.status_code == 200
    
    recommendations = response.json()
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    # Check recommendation structure
    recommendation = recommendations[0]
    assert "reward_id" in recommendation
    assert "reward_name" in recommendation
    assert "points_required" in recommendation
    assert "confidence_score" in recommendation
    assert "description" in recommendation
    
    # Check confidence scores are sorted
    confidence_scores = [r["confidence_score"] for r in recommendations]
    assert confidence_scores == sorted(confidence_scores, reverse=True)

def test_get_recommendations_invalid_user():
    response = client.get("/recommendations/invalid")
    assert response.status_code == 200  # Should still return recommendations with mock data 