import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.dependencies import verify_api_key, verify_host
from app.services.converter import convert_docx_to_pdf

router = APIRouter()


@router.post("/convert", dependencies=[Depends(verify_api_key), Depends(verify_host)])
async def convert(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Only .docx files are accepted.")

    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File too large. Max is {settings.MAX_UPLOAD_MB} MB.")

    pdf_path, tmp_dir = convert_docx_to_pdf(contents)
    original_name = Path(file.filename).stem
    background_tasks.add_task(shutil.rmtree, tmp_dir, ignore_errors=True)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{original_name}.pdf",
        background=background_tasks,
    )
