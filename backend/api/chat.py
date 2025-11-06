"""Chat/QA endpoints with streaming support."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import User, ChatMessage
from api.dependencies import get_current_user
from api.schemas import ChatMessageRequest, ChatMessageResponse
from services.job_service import JobService
from services.model_service import ModelService
from utils.logger import logger
import json
import asyncio

router = APIRouter(prefix="/jobs", tags=["chat"])


@router.post("/{job_id}/chat")
async def chat_with_document(
    job_id: str,
    message: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    stream: bool = False
):
    """Ask a question about a document."""
    # Get job
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job not completed yet"
        )
    
    # Get context from OCR text
    context = job.ocr_text or ""
    
    if not context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text extracted from document"
        )
    
    # Get answer using model service
    model_service = ModelService()
    answer_result = model_service.answer_question(
        question=message.message,
        context=context,
        job_id=job.id
    )
    
    # Save chat message
    chat_message = ChatMessage(
        job_id=job.id,
        user_message=message.message,
        assistant_message=answer_result.get("answer", "")
    )
    db.add(chat_message)
    db.commit()
    
    # Collect training data for active learning
    try:
        from services.active_learning_service import ActiveLearningService
        active_learning = ActiveLearningService()
        active_learning.collect_training_data_from_chat(db, job_id)
    except Exception as e:
        logger.error(f"Error collecting chat training data: {e}")
    
    if stream:
        # Stream response
        async def generate():
            answer = answer_result.get("answer", "")
            # Simulate streaming by chunking
            words = answer.split()
            for i, word in enumerate(words):
                chunk = {
                    "chunk": word + " ",
                    "done": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    else:
        # Return complete response
        return ChatMessageResponse(
            message=message.message,
            answer=answer_result.get("answer", ""),
            confidence=answer_result.get("confidence", 0.0),
            created_at=chat_message.created_at
        )


@router.get("/{job_id}/chat/history")
async def get_chat_history(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a job."""
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get chat messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.job_id == job.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        ChatMessageResponse(
            message=msg.user_message,
            answer=msg.assistant_message,
            created_at=msg.created_at
        )
        for msg in messages
    ]

