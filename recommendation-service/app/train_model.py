import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def generate_sample_data(n_samples=1000):
    """
    Generate sample training data for the recommendation model.
    """
    np.random.seed(42)
    
    # Generate random transaction data
    total_spent = np.random.uniform(500, 5000, n_samples)
    transaction_count = np.random.randint(5, 50, n_samples)
    avg_transaction = total_spent / transaction_count
    
    # Generate category distributions
    categories = ["groceries", "dining", "shopping", "entertainment"]
    category_distributions = np.random.dirichlet(np.ones(4), n_samples)
    
    # Generate features
    X = np.column_stack([
        total_spent,
        transaction_count,
        avg_transaction,
        category_distributions
    ])
    
    # Generate labels (which reward would be most suitable)
    # In a real scenario, this would be based on actual user behavior
    y = np.random.randint(0, 4, n_samples)
    
    return X, y

def train_model():
    """
    Train a simple recommendation model using Random Forest.
    """
    # Generate sample data
    X, y = generate_sample_data()
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save model
    model_path = 'models/reward_model.joblib'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model() 