"""Document upload endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import User
from api.dependencies import get_current_user
from services.job_service import JobService
from config import settings
from utils.logger import logger
import os
import uuid
import aiofiles
from pathlib import Path
from api.schemas import JobStatusResponse

router = APIRouter(prefix="/upload", tags=["upload"])


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE


@router.post("/", response_model=JobStatusResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for analysis."""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_size = 0
    chunk_size = 8192
    chunks = []
    
    async with aiofiles.open("/dev/null", "wb") as temp_file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
            file_size += len(chunk)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
                )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}{file_ext}"
    
    async with aiofiles.open(file_path, "wb") as f:
        for chunk in chunks:
            await f.write(chunk)
    
    # Create job
    job = JobService.create_job(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_ext,
        file_size=file_size
    )
    
    logger.info(f"File uploaded: {file.filename} -> {file_path}")
    
    # Trigger analysis (async)
    # This would typically be done via Celery or background task
    from services.analysis_service import AnalysisService
    analysis_service = AnalysisService()
    # analysis_service.process_job_async(job.job_id)
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at
    )

