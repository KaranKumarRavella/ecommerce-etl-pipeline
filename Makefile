.PHONY: test run generate-data up down lint

test:
	pytest -q

run:
	python -m etl.pipeline --dry-run

generate-data:
	python scripts/generate_data.py --rows 500 --out data/generated

up:
	docker compose up -d --build

down:
	docker compose down -v

lint:
	ruff check src tests scripts
