import os

import pytest
from fastapi.testclient import TestClient

# Set required env vars before the app module is imported so that
# Settings() picks them up at class-body evaluation time.
os.environ.setdefault("CONVERT_API_KEY", "test-key")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("ALLOWED_HOSTS", "testserver")

from app.main import app  # noqa: E402 – must come after env setup


TEST_API_KEY = "test-key"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
