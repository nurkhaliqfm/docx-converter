import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/documents", tags=["documents"])

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


@router.get("/", summary="List available .docx files")
def list_documents():
    files = [f.name for f in ASSETS_DIR.glob("*.docx") if f.is_file()]
    return {"files": files}


@router.get("/{filename}", summary="Download a .docx file from assets")
def get_document(filename: str):
    if not filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    safe_name = Path(filename).name
    file_path = ASSETS_DIR / safe_name

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=safe_name,
    )
