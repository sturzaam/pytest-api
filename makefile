build:
	poetry install

development:
	poetry run uvicorn test_app.main:app --reload

test:
	poetry run pytest tests

quality:
	poetry run black .
	poetry run isort . --profile black
	poetry run flake8 .

quality-check:
	poetry run black . --check
	poetry run isort . --profile black --check-only
	poetry run flake8 .

secure:
	poetry run bandit -r pytest_api
	poetry run safety check