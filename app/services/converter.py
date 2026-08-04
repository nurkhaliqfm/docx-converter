import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import HTTPException

from app.config import settings


def convert_docx_to_pdf(contents: bytes) -> tuple[Path, Path]:
    """Runs LibreOffice conversion. Returns (pdf_path, tmp_dir) — caller must clean up tmp_dir."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="docx2pdf_"))
    job_id = uuid.uuid4().hex[:8]
    docx_path = tmp_dir / f"{job_id}.docx"
    docx_path.write_bytes(contents)

    try:
        result = subprocess.run(
            [
                settings.SOFFICE_PATH,
                "--headless",
                "--norestore",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_dir),
                str(docx_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(504, "Conversion timed out.")

    pdf_path = tmp_dir / f"{job_id}.pdf"
    if result.returncode != 0 or not pdf_path.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(500, f"Conversion failed: {result.stderr or result.stdout}")

    return pdf_path, tmp_dir
