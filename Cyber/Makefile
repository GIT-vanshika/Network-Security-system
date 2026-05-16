.PHONY: help install install-dev test lint format clean build run docker-build docker-run docker-compose-up docker-compose-down

help:
	@echo "Network Security ML - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install           - Install production dependencies"
	@echo "  make install-dev       - Install development dependencies"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test              - Run tests with coverage"
	@echo "  make lint              - Run linting checks"
	@echo "  make format            - Format code"
	@echo ""
	@echo "Building & Running:"
	@echo "  make build             - Build the project"
	@echo "  make run               - Run the FastAPI app locally"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker image"
	@echo "  make docker-run        - Run Docker container"
	@echo "  make docker-compose-up - Start Docker Compose services"
	@echo "  make docker-compose-down - Stop Docker Compose services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean             - Clean build artifacts and cache"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio flake8 black isort mypy

test:
	pytest --cov=networksecurity --cov-report=html --cov-report=term-missing -v

lint:
	flake8 networksecurity --max-line-length=127 --count --statistics
	mypy networksecurity --ignore-missing-imports || true

format:
	black networksecurity --line-length=127
	isort networksecurity

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf dist build *.egg-info

build: clean
	python setup.py build

run:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -f Dockerfile -t network-security-app:latest .

docker-run:
	docker run -p 8000:8000 \
		-e MONGO_DB_URL=mongodb://localhost:27017 \
		network-security-app:latest

docker-compose-up:
	docker-compose up -d
	@echo "Services started:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Swagger UI: http://localhost:8000/docs"
	@echo "  - MongoDB Express: http://localhost:8081"

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f app

ci-local: install-dev lint test
	@echo "✅ All CI checks passed locally"
