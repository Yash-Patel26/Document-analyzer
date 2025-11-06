"""Active learning service for continuous model improvement."""
from sqlalchemy.orm import Session
from database.models import Job, ChatMessage
from services.model_service import ModelService
from services.job_service import JobService
from typing import Dict, Any, List
from utils.logger import logger
import json
from pathlib import Path
from config import settings
from datetime import datetime


class ActiveLearningService:
    """Service for continuous model training from user interactions."""
    
    def __init__(self):
        self.model_service = ModelService()
        self.training_data_dir = Path(settings.MODEL_STORAGE_PATH) / "training_data"
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_training_data_from_job(self, db: Session, job_id: str):
        """Collect training data from a completed job."""
        job = JobService.get_job(db, job_id)
        
        if not job or job.status != "completed":
            return
        
        training_data = {
            "job_id": job.job_id,
            "filename": job.filename,
            "created_at": job.created_at.isoformat(),
            "ocr_text": job.ocr_text,
            "summary": job.summary,
            "entities": job.entities,
        }
        
        # Save for summarization training
        if job.ocr_text and job.summary:
            self._save_summarization_data(job.ocr_text, job.summary)
        
        # Save for NER training (if entities are manually corrected)
        if job.entities:
            self._save_ner_data(job.ocr_text, job.entities)
        
        logger.info(f"Collected training data from job {job_id}")
    
    def collect_training_data_from_chat(self, db: Session, job_id: str):
        """Collect QA training data from chat interactions."""
        job = JobService.get_job(db, job_id)
        
        if not job or not job.ocr_text:
            return
        
        chat_messages = db.query(ChatMessage).filter(
            ChatMessage.job_id == job.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        for message in chat_messages:
            if message.user_message and message.assistant_message:
                # Extract answer span from context
                context = job.ocr_text
                answer_text = message.assistant_message
                
                # Find answer in context
                start = context.find(answer_text)
                if start != -1:
                    end = start + len(answer_text)
                    self._save_qa_data(
                        question=message.user_message,
                        context=context,
                        answer=answer_text,
                        start=start,
                        end=end
                    )
        
        logger.info(f"Collected QA training data from job {job_id}")
    
    def _save_summarization_data(self, text: str, summary: str):
        """Save summarization training data."""
        data_file = self.training_data_dir / "summarization" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "text": text,
            "summary": summary
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_ner_data(self, text: str, entities: Dict[str, Any]):
        """Save NER training data."""
        data_file = self.training_data_dir / "ner" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "text": text,
            "entities": entities.get("entities", [])
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_qa_data(self, question: str, context: str, answer: str, start: int, end: int):
        """Save QA training data."""
        data_file = self.training_data_dir / "qa" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data or create new
        existing_data = {"context": context, "qa_pairs": []}
        
        # Add new QA pair
        existing_data["qa_pairs"].append({
            "question": question,
            "answer": answer,
            "start": start,
            "end": end
        })
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    def trigger_incremental_training(self, db: Session, model_type: str = "all", min_samples: int = 10):
        """Trigger incremental training when enough new data is collected."""
        # The background trainer will handle actual training
        # This just logs that we have enough data
        if model_type in ["summarization", "all"]:
            summarization_files = list((self.training_data_dir / "summarization").glob("*.json"))
            if len(summarization_files) >= min_samples:
                logger.info(f"Enough data for summarization training: {len(summarization_files)} samples")
        
        if model_type in ["ner", "all"]:
            ner_files = list((self.training_data_dir / "ner").glob("*.json"))
            if len(ner_files) >= min_samples:
                logger.info(f"Enough data for NER training: {len(ner_files)} samples")
        
        if model_type in ["qa", "all"]:
            qa_files = list((self.training_data_dir / "qa").glob("*.json"))
            if len(qa_files) >= min_samples:
                logger.info(f"Enough data for QA training: {len(qa_files)} samples")

