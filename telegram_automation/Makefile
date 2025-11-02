.PHONY: install test run clean docker-build docker-run

# Install requirements
install:
	pip install -r requirements.txt

# Run tests
test:
	python simple_test.py

# Run integration tests
test-integration:
	python test_integration.py

# Run the bot
run:
	python main_bot.py

# Run API server
api:
	python api_gateway.py

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Docker build
docker-build:
	docker-compose build

# Docker run
docker-run:
	docker-compose up -d

# Docker logs
docker-logs:
	docker-compose logs -f

# Docker stop
docker-stop:
	docker-compose down

# Setup development environment
setup-dev:
	cp .env.example .env
	pip install -r requirements.txt
	python -c "from database.models import create_tables; create_tables()"

# Format code
format:
	black . --line-length 88
	isort . --profile black

# Lint code
lint:
	flake8 . --max-line-length=88 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports

# Full check
check: lint test

# Update requirements
update-reqs:
	pip-compile requirements.in
