.PHONY: help deps install test run docker-up lint format

help:
	@echo "Make targets: deps, install, test, run, docker-up, lint, format"

deps:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install:
	python -m pip install -r requirements-dev.txt

test:
	PYTHONPATH=. pytest -q

run:
	./start.sh

docker-up:
	cd docker && docker compose -f docker-compose.no-gpu.yml up --build

lint:
	black . && isort . && flake8

format:
	black . && isort .
