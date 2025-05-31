FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY models/ ./models/

# Train the model if it doesn't exist
RUN python app/train_model.py

# Expose the port
EXPOSE 8083

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"] 