"""Service for managing document analysis jobs."""
from sqlalchemy.orm import Session
from database.models import Job, JobStatus
from typing import Optional, Dict, Any
import uuid
import os
from config import settings
from utils.logger import logger


class JobService:
    """Service for job management."""
    
    @staticmethod
    def create_job(
        db: Session,
        user_id: int,
        filename: str,
        file_path: str,
        file_type: str,
        file_size: int
    ) -> Job:
        """Create a new analysis job."""
        job_id = str(uuid.uuid4())
        
        job = Job(
            user_id=user_id,
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status=JobStatus.PENDING.value
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Created job: {job_id} for user {user_id}")
        return job
    
    @staticmethod
    def update_job_status(
        db: Session,
        job_id: str,
        status: str,
        progress: float = 0.0,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Job]:
        """Update job status."""
        job = db.query(Job).filter(Job.job_id == job_id).first()
        
        if not job:
            return None
        
        job.status = status
        job.progress = progress
        job.current_step = current_step
        job.error_message = error_message
        
        if status == JobStatus.COMPLETED.value:
            from datetime import datetime
            job.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        logger.info(f"Updated job {job_id}: {status} - {progress}%")
        return job
    
    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return db.query(Job).filter(Job.job_id == job_id).first()
    
    @staticmethod
    def save_job_results(
        db: Session,
        job_id: str,
        ocr_text: Optional[str] = None,
        summary: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        embeddings: Optional[Dict[str, Any]] = None
    ) -> Optional[Job]:
        """Save analysis results to job."""
        job = db.query(Job).filter(Job.job_id == job_id).first()
        
        if not job:
            return None
        
        if ocr_text:
            job.ocr_text = ocr_text
        if summary:
            job.summary = summary
        if entities:
            job.entities = entities
        if embeddings:
            job.embeddings = embeddings
        
        db.commit()
        db.refresh(job)
        
        return job

