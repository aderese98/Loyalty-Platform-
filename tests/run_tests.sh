#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Running tests for all services..."

# Run Go tests
echo -e "\n${GREEN}Running User Service tests...${NC}"
cd ../user-service
go test ./... -v

# Run Java tests
echo -e "\n${GREEN}Running Reward Service tests...${NC}"
cd ../reward-service
./mvnw test

# Run Python tests
echo -e "\n${GREEN}Running Transaction Service tests...${NC}"
cd ../transaction-service
python -m pytest -v

echo -e "\n${GREEN}Running Batch Analytics tests...${NC}"
cd ../batch-analytics
python -m pytest -v

echo -e "\n${GREEN}All tests completed successfully!${NC}" 