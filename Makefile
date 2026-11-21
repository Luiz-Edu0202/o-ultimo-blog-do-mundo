# =============================================================================
# O Último Blog do Mundo — Makefile
# =============================================================================
# Convenience targets for local development with and without Docker.
#
# Without Docker:
#   make run          — start dev server (SQLite)
#   make test         — run pytest locally
#   make lint         — ruff check + format check
#
# With Docker:
#   make up           — start all containers (web + db + redis)
#   make down         — stop containers and remove volumes
#   make migrate      — run Django migrations inside the web container
#   make test-docker  — run pytest inside the web container
#   make logs         — tail logs from all containers
#   make shell        — open a Django shell inside the web container
# =============================================================================

.PHONY: help run test lint up down migrate test-docker logs shell build seed seed-docker

help:
	@echo ""
	@echo "O Último Blog do Mundo — available targets:"
	@echo ""
	@echo "  Without Docker:"
	@echo "    run          Start the Django dev server (SQLite)"
	@echo "    test         Run pytest locally"
	@echo "    lint         Ruff lint + format check"
	@echo "    seed         Populate database with demo articles and config"
	@echo ""
	@echo "  With Docker:"
	@echo "    up           Build and start all containers"
	@echo "    down         Stop containers and remove volumes"
	@echo "    migrate      Run Django migrations inside the web container"
	@echo "    seed-docker  Populate database inside the web container"
	@echo "    test-docker  Run pytest inside the web container (coverage >= 80%)"
	@echo "    logs         Tail logs from all containers"
	@echo "    shell        Open a Django shell inside the web container"
	@echo "    build        Build the Docker image only (no push)"
	@echo ""

# ---------------------------------------------------------------------------
# Local targets (no Docker)
# ---------------------------------------------------------------------------
run:
	python manage.py runserver

test:
	pytest --cov --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check .
	ruff format --check .

seed:
	python manage.py seed_demo

# ---------------------------------------------------------------------------
# Docker targets
# ---------------------------------------------------------------------------
up:
	docker compose up --build

down:
	docker compose down -v

migrate:
	docker compose exec web python manage.py migrate

seed-docker:
	docker compose exec web python manage.py seed_demo

test-docker:
	@echo "Starting db and redis..."
	docker compose up -d db redis
	@echo "Waiting for services to be healthy..."
	@until docker compose exec db pg_isready -U $${POSTGRES_USER:-blog} > /dev/null 2>&1; do sleep 1; done
	@until docker compose exec redis redis-cli ping > /dev/null 2>&1; do sleep 1; done
	@echo "Running tests inside web container..."
	docker compose run --rm \
		-e DJANGO_SETTINGS_MODULE=config.settings.local \
		-e DATABASE_URL=postgresql://$${POSTGRES_USER:-blog}:$${POSTGRES_PASSWORD:-blog}@db:5432/$${POSTGRES_DB:-blog} \
		-e REDIS_URL=redis://redis:6379/0 \
		web pytest --cov --cov-report=term-missing --cov-fail-under=80
	@echo "Stopping db and redis..."
	docker compose down -v

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

build:
	docker build -t o-ultimo-blog-do-mundo:local .
