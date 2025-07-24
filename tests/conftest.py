import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.postgres import get_db
from app.db.models import Base

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", "")


@pytest.fixture(scope="function")
def mock_dynamodb(aws_credentials):
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="snapshort-links",
            AttributeDefinitions=[
                {"AttributeName": "short_code", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
            ],
            KeySchema=[{"AttributeName": "short_code", "KeyType": "HASH"}],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user_id-index",
                    "KeySchema": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


@pytest.fixture(scope="function")
def client(mock_dynamodb):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    # So redirect background tasks use test DB instead of default engine
    import app.db.postgres as postgres_module
    orig_session = postgres_module.SessionLocal
    postgres_module.SessionLocal = TestingSessionLocal
    try:
        with TestClient(app) as c:
            yield c
    finally:
        postgres_module.SessionLocal = orig_session
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
