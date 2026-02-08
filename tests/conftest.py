import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app import create_app
from src.database.base import Base
from src.database.session import get_db


@pytest.fixture(scope="session")
def db_engine():
    url = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
