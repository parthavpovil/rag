.PHONY: help build up down restart logs clean test health

# Variables
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = rag-service
CONTAINER_NAME = rag-service

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)RAG Service - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build the Docker image
	@echo "$(GREEN)Building RAG service Docker image...$(NC)"
	docker compose build $(SERVICE_NAME)
	@echo "$(GREEN)✓ Build complete$(NC)"

up: ## Start the service
	@echo "$(GREEN)Starting RAG service...$(NC)"
	docker compose up -d $(SERVICE_NAME)
	@echo "$(GREEN)✓ Service started$(NC)"
	@echo "$(YELLOW)Run 'make logs' to see logs$(NC)"
	@echo "$(YELLOW)Run 'make health' to check health$(NC)"

down: ## Stop the service
	@echo "$(YELLOW)Stopping RAG service...$(NC)"
	docker compose down
	@echo "$(GREEN)✓ Service stopped$(NC)"

restart: down up ## Restart the service

logs: ## Show service logs
	docker compose logs -f $(SERVICE_NAME)

logs-tail: ## Show last 100 lines of logs
	docker compose logs --tail=100 $(SERVICE_NAME)

ps: ## Show running containers
	docker compose ps

health: ## Check service health
	@echo "$(GREEN)Checking RAG service health...$(NC)"
	@curl -s http://localhost:8000/health | jq . || echo "$(RED)✗ Service not responding$(NC)"

test-query: ## Test query endpoint
	@echo "$(GREEN)Testing query endpoint...$(NC)"
	@curl -s -X POST http://localhost:8000/query \
		-H "Content-Type: application/json" \
		-d '{"tenant_id":"test","query":"test"}' | jq .

shell: ## Open shell in container
	docker exec -it $(CONTAINER_NAME) /bin/bash

clean: down ## Stop service and remove volumes
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker compose down -v
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean ## Remove all images and containers
	@echo "$(RED)Removing all Docker images...$(NC)"
	docker rmi $$(docker images -q $(SERVICE_NAME)) 2>/dev/null || true
	@echo "$(GREEN)✓ All cleaned$(NC)"

rebuild: clean build up ## Clean, rebuild, and start

# Development commands
dev-install: ## Install dependencies locally (for development)
	cd knowledge_svc && pip install -r requirements.txt

dev-run: ## Run service locally (without Docker)
	cd knowledge_svc && uvicorn main:app --reload --port 8000

# Testing commands
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	python tests/test_e2e_rag.py
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-s3: ## Run S3 integration test
	@echo "$(GREEN)Running S3 integration test...$(NC)"
	python tests/test_s3_upload_and_query.py

test-migration: ## Run migration test
	python tests/test_migration.py

# Monitoring
stats: ## Show container resource usage
	docker stats $(CONTAINER_NAME) --no-stream

inspect: ## Inspect container configuration
	docker inspect $(CONTAINER_NAME) | jq .

# Quick commands
quick-start: build up health ## Build, start, and check health
deploy: rebuild health ## Full deployment (rebuild and verify)

.DEFAULT_GOAL := help
