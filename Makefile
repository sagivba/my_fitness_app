.PHONY: install test test-full lint format clean run docker-dev docker-qa

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	scripts/test.sh quick

test-full:
	scripts/test.sh full

lint:
	scripts/lint.sh

format:
	python -m ruff format src tests
	python -m ruff check --fix src tests

clean:
	scripts/clean.sh

run:
	PYTHONPATH=src flask --app my_fitness_app.app:create_app run --debug

docker-dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

docker-qa:
	docker compose -f docker-compose.yml -f docker-compose.qa.yml up -d --build
