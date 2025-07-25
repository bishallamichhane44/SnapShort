.PHONY: install dev test lint migrate create-dynamo-local build deploy-aws

install:
	pip install -r requirements.txt -r requirements-dev.txt

dev:
	docker-compose up -d
	uvicorn app.main:app --reload --port 8080

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/
	ruff format app/ tests/

migrate:
	alembic upgrade head

create-dynamo-local:
	aws dynamodb create-table \
		--table-name snapshort-links \
		--attribute-definitions \
			AttributeName=short_code,AttributeType=S \
			AttributeName=user_id,AttributeType=S \
			AttributeName=created_at,AttributeType=S \
		--key-schema AttributeName=short_code,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--global-secondary-indexes \
			"[{\"IndexName\":\"user_id-index\",\"KeySchema\":[{\"AttributeName\":\"user_id\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]" \
		--endpoint-url http://localhost:8000

build:
	sam build --use-container

deploy-aws:
	sam deploy --guided
