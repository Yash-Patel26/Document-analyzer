"""Service for document analysis processing."""
from sqlalchemy.orm import Session
from services.model_service import ModelService
from services.job_service import JobService
from services.active_learning_service import ActiveLearningService
from database.models import JobStatus
from typing import Optional
from utils.logger import logger
import asyncio


class AnalysisService:
    """Service for processing document analysis jobs."""
    
    def __init__(self):
        self.model_service = ModelService()
        self.active_learning = ActiveLearningService()
    
    async def process_job(self, db: Session, job_id: str):
        """Process a document analysis job."""
        job = JobService.get_job(db, job_id)
        
        if not job:
            logger.error(f"Job not found: {job_id}")
            return
        
        try:
            # Update status to processing
            JobService.update_job_status(
                db, job_id, JobStatus.PROCESSING.value,
                progress=0.0, current_step="Starting analysis"
            )
            
            # Step 1: Process document (OCR, entities, summary, embeddings)
            logger.info(f"Processing document for job {job_id}")
            JobService.update_job_status(
                db, job_id, JobStatus.PROCESSING.value,
                progress=10.0, current_step="Extracting text from document"
            )
            
            results = self.model_service.process_document(job.file_path)
            
            # Step 2: Save results
            JobService.update_job_status(
                db, job_id, JobStatus.PROCESSING.value,
                progress=90.0, current_step="Saving results"
            )
            
            JobService.save_job_results(
                db, job_id,
                ocr_text=results.get("ocr", {}).get("text"),
                summary=results.get("summary", {}).get("summary"),
                entities=results.get("entities"),
                embeddings=results.get("embeddings")
            )
            
            # Step 3: Mark as completed
            JobService.update_job_status(
                db, job_id, JobStatus.COMPLETED.value,
                progress=100.0, current_step="Analysis completed"
            )
            
            # Step 4: Collect training data for active learning
            try:
                self.active_learning.collect_training_data_from_job(db, job_id)
                # Check if we have enough data for incremental training
                self.active_learning.trigger_incremental_training(
                    db, model_type="all", min_samples=10
                )
            except Exception as e:
                logger.error(f"Error in active learning collection: {e}")
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            JobService.update_job_status(
                db, job_id, JobStatus.FAILED.value,
                error_message=str(e)
            )
    
    def process_job_async(self, db: Session, job_id: str):
        """Process job asynchronously (for background tasks)."""
        asyncio.create_task(self.process_job(db, job_id))

