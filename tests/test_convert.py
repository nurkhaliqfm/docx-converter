import io
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.conftest import TEST_API_KEY

HEADERS = {"x-api-key": TEST_API_KEY}
DOCX_BYTES = b"PK\x03\x04"  # minimal ZIP magic (all .docx files start with this)


def _fake_docx_upload(filename: str = "test.docx", content: bytes = DOCX_BYTES):
    return {"file": (filename, io.BytesIO(content), "application/octet-stream")}


@pytest.fixture
def mock_conversion(tmp_path):
    """Patch convert_docx_to_pdf so no LibreOffice is needed."""
    pdf_file = tmp_path / "output.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    with patch(
        "app.routers.convert.convert_docx_to_pdf",
        return_value=(pdf_file, tmp_path),
    ):
        yield pdf_file


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_convert_returns_pdf(client, mock_conversion):
    response = client.post("/convert", headers=HEADERS, files=_fake_docx_upload())
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_convert_pdf_filename_matches_upload(client, mock_conversion):
    response = client.post(
        "/convert", headers=HEADERS, files=_fake_docx_upload("report.docx")
    )
    assert response.status_code == 200
    content_disposition = response.headers.get("content-disposition", "")
    assert "report.pdf" in content_disposition


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


def test_convert_rejects_non_docx(client):
    response = client.post(
        "/convert", headers=HEADERS, files=_fake_docx_upload("image.png")
    )
    assert response.status_code == 400


def test_convert_rejects_oversized_file(client):
    from app.config import settings

    big = b"A" * (settings.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    response = client.post(
        "/convert", headers=HEADERS, files=_fake_docx_upload("big.docx", big)
    )
    assert response.status_code == 413


# ---------------------------------------------------------------------------
# Authentication / authorisation
# ---------------------------------------------------------------------------


def test_convert_rejects_missing_api_key(client, mock_conversion):
    response = client.post("/convert", files=_fake_docx_upload())
    assert response.status_code == 401


def test_convert_rejects_wrong_api_key(client, mock_conversion):
    response = client.post(
        "/convert",
        headers={"x-api-key": "wrong-key"},
        files=_fake_docx_upload(),
    )
    assert response.status_code == 401


def test_convert_rejects_disallowed_host(client, mock_conversion):
    from app.config import settings

    original = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ["allowed.example.com"]
    try:
        # TestClient sends Host: testserver by default
        response = client.post("/convert", headers=HEADERS, files=_fake_docx_upload())
        assert response.status_code == 403
    finally:
        settings.ALLOWED_HOSTS = original
