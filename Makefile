up:
	docker compose up --build

down:
	docker compose down

migrate-api:
	docker compose run --rm api alembic upgrade head

make-migration:
	docker compose run --rm api alembic revision --autogenerate -m "$(MSG)"

test-api:
	docker compose run --rm api pytest
