import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.config import settings
from app.dependencies import verify_api_key, verify_host

# ---------------------------------------------------------------------------
# verify_api_key
# ---------------------------------------------------------------------------


def test_verify_api_key_accepts_correct_key():
    # Should not raise
    verify_api_key(x_api_key=settings.API_KEY)


def test_verify_api_key_rejects_wrong_key():
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(x_api_key="wrong-key")
    assert exc_info.value.status_code == 401


def test_verify_api_key_rejects_none():
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(x_api_key=None)
    assert exc_info.value.status_code == 401


def test_verify_api_key_raises_500_when_server_has_no_key():
    original = settings.API_KEY
    settings.API_KEY = None
    try:
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(x_api_key="any-key")
        assert exc_info.value.status_code == 500
    finally:
        settings.API_KEY = original


# ---------------------------------------------------------------------------
# verify_host
# ---------------------------------------------------------------------------


def _make_request(host: str) -> MagicMock:
    request = MagicMock()
    request.headers = {"host": host}
    return request


def test_verify_host_accepts_allowed_host():
    original = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ["example.com"]
    try:
        verify_host(_make_request("example.com"))  # should not raise
    finally:
        settings.ALLOWED_HOSTS = original


def test_verify_host_rejects_disallowed_host():
    original = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ["example.com"]
    try:
        with pytest.raises(HTTPException) as exc_info:
            verify_host(_make_request("evil.com"))
        assert exc_info.value.status_code == 403
    finally:
        settings.ALLOWED_HOSTS = original


def test_verify_host_allows_all_when_list_empty():
    original = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = []
    try:
        verify_host(_make_request("any.host"))  # should not raise
    finally:
        settings.ALLOWED_HOSTS = original


def test_verify_host_strips_port_from_host_header():
    original = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ["example.com"]
    try:
        verify_host(_make_request("example.com:8080"))  # should not raise
    finally:
        settings.ALLOWED_HOSTS = original
