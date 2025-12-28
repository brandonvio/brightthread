.PHONY: help test lint format install dev integration-tests integration-tests-verbose clean generate-api-docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# API endpoint for integration tests
API_ENDPOINT = https://api.brightthread.design/

help: ## Show this help message
	@echo "$(BLUE)BrightThread Backend Targets$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev                   Run development server (http://127.0.0.1:8000)"
	@echo "  make install               Install dependencies (uv sync)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test                  Run unit tests (pytest)"
	@echo "  make lint                  Run code linting (ruff)"
	@echo "  make integration-tests     Run integration tests against deployed API"
	@echo "  make integration-tests-v   Run integration tests with verbose output"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make format                Format code with ruff"
	@echo "  make clean                 Remove build artifacts"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make generate-api-docs     Generate API docs (requires local server running)"
	@echo ""
	@echo "$(GREEN)Configuration:$(NC)"
	@echo "  API_ENDPOINT               API endpoint for integration tests"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make test"
	@echo "  make lint && make format"
	@echo "  API_ENDPOINT=https://...prod/ make integration-tests"

install: ## Install dependencies with uv
	@echo "$(BLUE)==> Installing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev: ## Run development server
	@echo "$(BLUE)==> Starting development server...$(NC)"
	cd src && uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload

test: ## Run unit tests
	@echo "$(BLUE)==> Running unit tests...$(NC)"
	uv run pytest tests/ -v --tb=short
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

lint: ## Run code linting
	@echo "$(BLUE)==> Linting code...$(NC)"
	uv run ruff check src/ tests/
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with ruff
	@echo "$(BLUE)==> Formatting code...$(NC)"
	uv run ruff format src/ tests/ tests_integration/
	@echo "$(GREEN)✓ Code formatted$(NC)"

integration-tests: ## Run integration tests against deployed API
	@echo "$(BLUE)==> Running integration tests...$(NC)"
	@echo "$(BLUE)API Endpoint: $(API_ENDPOINT)$(NC)"
	API_ENDPOINT=$(API_ENDPOINT) uv run pytest tests_integration/ -v --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

integration-tests-verbose: ## Run integration tests with verbose output
	@echo "$(BLUE)==> Running integration tests (verbose)...$(NC)"
	@echo "$(BLUE)API Endpoint: $(API_ENDPOINT)$(NC)"
	API_ENDPOINT=$(API_ENDPOINT) uv run pytest tests_integration/ -vv -s --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

integration-tests-local: ## Run integration tests with verbose output
	@echo "$(BLUE)==> Running integration tests (local)...$(NC)"
	@echo "$(BLUE)API Endpoint: $(API_ENDPOINT)$(NC)"
	API_ENDPOINT=http://127.0.0.1:8000 uv run pytest tests_integration/ -vv -s --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

clean: ## Remove build artifacts
	@echo "$(BLUE)==> Cleaning build artifacts...$(NC)"
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

generate-api-docs: ## Generate API documentation (requires local server at localhost:8000)
	@echo "$(BLUE)==> Generating API documentation...$(NC)"
	@echo "$(YELLOW)Note: Ensure dev server is running (make dev)$(NC)"
	@mkdir -p ../docs/api
	@curl -s http://127.0.0.1:8000/openapi.json -o ../docs/api/openapi.json
	@echo '<!DOCTYPE html>' > ../docs/api/index.html
	@echo '<html>' >> ../docs/api/index.html
	@echo '<head>' >> ../docs/api/index.html
	@echo '  <title>BrightThread API Documentation</title>' >> ../docs/api/index.html
	@echo '  <meta charset="utf-8"/>' >> ../docs/api/index.html
	@echo '  <meta name="viewport" content="width=device-width, initial-scale=1">' >> ../docs/api/index.html
	@echo '  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">' >> ../docs/api/index.html
	@echo '  <style>body { margin: 0; padding: 0; }</style>' >> ../docs/api/index.html
	@echo '</head>' >> ../docs/api/index.html
	@echo '<body>' >> ../docs/api/index.html
	@echo '  <redoc spec-url="openapi.json"></redoc>' >> ../docs/api/index.html
	@echo '  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>' >> ../docs/api/index.html
	@echo '</body>' >> ../docs/api/index.html
	@echo '</html>' >> ../docs/api/index.html
	@echo "$(GREEN)✓ API docs generated at ../docs/api/$(NC)"

migrate-head:
	@echo "$(BLUE)==> Migrating database to latest version...$(NC)"
	PYTHONPATH=. uv run alembic upgrade head
	@echo "$(GREEN)✓ Database migrated to latest version$(NC)"

migrate-down:
	@echo "$(BLUE)==> Migrating database down...$(NC)"
	PYTHONPATH=. uv run alembic downgrade -1
	@echo "$(GREEN)✓ Database migrated down$(NC)"

migrate-base:
	@echo "$(BLUE)==> Migrating database to base version...$(NC)"
	PYTHONPATH=. uv run alembic downgrade base
	@echo "$(GREEN)✓ Database migrated to base version$(NC)"