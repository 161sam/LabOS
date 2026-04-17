up:
	docker compose up --build

down:
	docker compose down

test-api:
	docker compose run --rm api pytest
