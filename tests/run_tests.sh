#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Running tests for all services..."

# Run Go tests
echo -e "\n${GREEN}Running User Service tests...${NC}"
cd "$PROJECT_ROOT/user-service"
go test ./... -v

# Run Java tests
echo -e "\n${GREEN}Running Reward Service tests...${NC}"
cd "$PROJECT_ROOT/reward-service"
mvn test

# Run Python tests
echo -e "\n${GREEN}Running Transaction Service tests...${NC}"
cd "$PROJECT_ROOT/transaction-service"
python3 -m pytest -v

echo -e "\n${GREEN}Running Batch Analytics tests...${NC}"
cd "$PROJECT_ROOT/batch-analytics"
python3 -m pytest -v

echo -e "\n${GREEN}All tests completed successfully!${NC}" 