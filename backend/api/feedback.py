"""Feedback endpoints for model improvement."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import User, Job
from api.dependencies import get_current_user
from api.schemas import ChatMessageRequest
from services.active_learning_service import ActiveLearningService
from services.job_service import JobService
from utils.logger import logger
from pydantic import BaseModel
from typing import Optional, Dict, Any


router = APIRouter(prefix="/feedback", tags=["feedback"])


class EntityCorrection(BaseModel):
    """Entity correction feedback."""
    original: Dict[str, Any]
    corrected: Dict[str, Any]


class SummaryFeedback(BaseModel):
    """Summary feedback."""
    job_id: str
    summary_rating: Optional[int] = None  # 1-5
    is_correct: Optional[bool] = None
    corrected_summary: Optional[str] = None


class QAFeedback(BaseModel):
    """QA feedback."""
    message_id: int
    answer_rating: Optional[int] = None  # 1-5
    is_correct: Optional[bool] = None
    corrected_answer: Optional[str] = None


@router.post("/entities/{job_id}")
async def correct_entities(
    job_id: str,
    corrections: list[EntityCorrection],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit entity corrections for training."""
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update job with corrected entities
    corrected_entities = [corr.corrected for corr in corrections]
    job.entities = {"entities": corrected_entities}
    db.commit()
    
    # Collect for training
    active_learning = ActiveLearningService()
    active_learning.collect_training_data_from_job(db, job_id)
    
    logger.info(f"Entity corrections received for job {job_id}")
    return {"message": "Feedback received, will be used for model improvement"}


@router.post("/summary")
async def submit_summary_feedback(
    feedback: SummaryFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit summary feedback."""
    job = JobService.get_job(db, feedback.job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update job with corrected summary if provided
    if feedback.corrected_summary:
        job.summary = feedback.corrected_summary
        db.commit()
        
        # Collect for training
        active_learning = ActiveLearningService()
        active_learning.collect_training_data_from_job(db, feedback.job_id)
    
    logger.info(f"Summary feedback received for job {feedback.job_id}")
    return {"message": "Feedback received"}


@router.post("/qa")
async def submit_qa_feedback(
    feedback: QAFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit QA feedback."""
    from database.models import ChatMessage
    
    message = db.query(ChatMessage).filter(
        ChatMessage.id == feedback.message_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Update message with corrected answer if provided
    if feedback.corrected_answer:
        message.assistant_message = feedback.corrected_answer
        db.commit()
        
        # Collect for training
        active_learning = ActiveLearningService()
        active_learning.collect_training_data_from_chat(db, message.job_id)
    
    logger.info(f"QA feedback received for message {feedback.message_id}")
    return {"message": "Feedback received"}

