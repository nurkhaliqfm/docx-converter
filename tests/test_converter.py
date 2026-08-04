import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.converter import convert_docx_to_pdf

FAKE_DOCX = b"PK\x03\x04 fake docx content"


def _make_subprocess_mock(tmp_dir: Path, returncode: int = 0):
    """Return a side_effect function that creates the expected PDF and returns a mock result."""

    def _run(cmd, **kwargs):
        if returncode == 0:
            # LibreOffice would produce <job_id>.pdf in --outdir
            docx_path = Path(cmd[-1])
            outdir = Path(cmd[cmd.index("--outdir") + 1])
            pdf_path = outdir / docx_path.with_suffix(".pdf").name
            pdf_path.write_bytes(b"%PDF-1.4 fake")
        return MagicMock(returncode=returncode, stderr="conversion error", stdout="")

    return _run


# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------

def test_convert_docx_to_pdf_returns_pdf_path(tmp_path):
    with patch(
        "app.services.converter.subprocess.run",
        side_effect=_make_subprocess_mock(tmp_path),
    ):
        pdf_path, tmp_dir = convert_docx_to_pdf(FAKE_DOCX)

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"


def test_convert_docx_to_pdf_returns_tmp_dir(tmp_path):
    with patch(
        "app.services.converter.subprocess.run",
        side_effect=_make_subprocess_mock(tmp_path),
    ):
        pdf_path, tmp_dir = convert_docx_to_pdf(FAKE_DOCX)

    assert pdf_path.parent == tmp_dir


def test_convert_docx_to_pdf_writes_docx_input(tmp_path):
    """The service should write the raw bytes to a temp .docx before calling soffice."""
    captured_cmd = {}

    def _run(cmd, **kwargs):
        captured_cmd["cmd"] = cmd
        docx_path = Path(cmd[-1])
        outdir = Path(cmd[cmd.index("--outdir") + 1])
        (outdir / docx_path.with_suffix(".pdf").name).write_bytes(b"%PDF fake")
        return MagicMock(returncode=0, stderr="", stdout="")

    with patch("app.services.converter.subprocess.run", side_effect=_run):
        convert_docx_to_pdf(FAKE_DOCX)

    docx_path = Path(captured_cmd["cmd"][-1])
    assert docx_path.suffix == ".docx"
    assert docx_path.read_bytes() == FAKE_DOCX


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------

def test_convert_raises_504_on_timeout():
    def _timeout(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, timeout=120)

    with patch("app.services.converter.subprocess.run", side_effect=_timeout):
        with pytest.raises(HTTPException) as exc_info:
            convert_docx_to_pdf(FAKE_DOCX)

    assert exc_info.value.status_code == 504


def test_convert_raises_500_on_nonzero_returncode():
    with patch(
        "app.services.converter.subprocess.run",
        side_effect=_make_subprocess_mock(Path("/tmp"), returncode=1),
    ):
        with pytest.raises(HTTPException) as exc_info:
            convert_docx_to_pdf(FAKE_DOCX)

    assert exc_info.value.status_code == 500


def test_convert_raises_500_when_pdf_missing():
    """Non-zero is not the only failure: LibreOffice may exit 0 but produce no file."""

    def _run_no_output(cmd, **kwargs):
        return MagicMock(returncode=0, stderr="", stdout="")

    with patch("app.services.converter.subprocess.run", side_effect=_run_no_output):
        with pytest.raises(HTTPException) as exc_info:
            convert_docx_to_pdf(FAKE_DOCX)

    assert exc_info.value.status_code == 500


def test_convert_cleans_up_tmp_dir_on_timeout():
    captured_tmp = {}

    def _intercept(cmd, **kwargs):
        # Record the tmp dir before raising
        captured_tmp["dir"] = Path(cmd[-1]).parent
        raise subprocess.TimeoutExpired(cmd, timeout=120)

    with patch("app.services.converter.subprocess.run", side_effect=_intercept):
        with pytest.raises(HTTPException):
            convert_docx_to_pdf(FAKE_DOCX)

    assert not captured_tmp["dir"].exists()
