.PHONY: install test clean help pipeline watch match queue-test worker docker-build docker-up docker-down docker-restart docker-scale

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make pipeline       - Run pipeline once (fast mode)"
	@echo "  make pipeline-full  - Run pipeline with full LLM evaluation"
	@echo "  make watch          - Watch for new HTML files"
	@echo "  make queue-test     - Test RabbitMQ and Supabase connection"
	@echo "  make worker         - Start profile processing worker (local)"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Build and start containers"
	@echo "  make docker-down    - Stop and remove containers"
	@echo "  make docker-restart - Restart containers"
	@echo "  make docker-logs    - View worker logs"
	@echo "  make docker-scale   - Scale workers (e.g., make docker-scale N=5)"
	@echo "  make clean          - Clean cache and temp files"

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest tests/ -v

pipeline:
	python run.py pipeline

pipeline-full:
	python run.py pipeline --mode full

watch:
	python run.py watch

queue-test:
	python scripts/test_queue.py

worker:
	python scripts/start_worker.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-restart:
	docker-compose restart

docker-logs:
	docker-compose logs -f worker

docker-scale:
	docker-compose up -d --scale worker=$(N)

docker-ps:
	docker-compose ps

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf cache/*
	rm -rf logs/*.log
