"""Service for managing and using AI models."""
from typing import Dict, Any, Optional
from models.ocr_model import OCRModel
from models.entity_extraction_model import EntityExtractionModel
from models.summarization_model import SummarizationModel
from models.qa_model import QAModel
from models.embedding_model import EmbeddingModel
from services.vector_db import VectorDB
from utils.logger import logger
import os
from config import settings


class ModelService:
    """Service for AI model inference."""
    
    def __init__(self):
        self.ocr_model = None
        self.ner_model = None
        self.summarization_model = None
        self.qa_model = None
        self.embedding_model = None
        self.vector_db = None
        self._load_models()
    
    def _load_models(self):
        """Load all AI models."""
        try:
            logger.info("Loading AI models...")
            self.ocr_model = OCRModel()
            self.ner_model = EntityExtractionModel()
            self.summarization_model = SummarizationModel()
            self.qa_model = QAModel()
            self.embedding_model = EmbeddingModel()
            self.vector_db = VectorDB(dimension=384)
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document through the full pipeline."""
        logger.info(f"Processing document: {file_path}")
        
        results = {
            "ocr": None,
            "entities": None,
            "summary": None,
            "embeddings": None
        }
        
        try:
            # Step 1: OCR
            from PIL import Image
            import pdf2image
            
            # Determine file type and extract images
            if file_path.endswith('.pdf'):
                images = pdf2image.convert_from_path(file_path)
                # Process first page for now
                image = images[0] if images else None
            else:
                image = Image.open(file_path)
            
            if image:
                ocr_result = self.ocr_model.predict({"image": image})
                results["ocr"] = ocr_result
                text = ocr_result.get("text", "")
                
                if text:
                    # Step 2: Entity Extraction
                    entities_result = self.ner_model.predict({"text": text})
                    results["entities"] = entities_result
                    
                    # Step 3: Summarization
                    summary_result = self.summarization_model.predict({"text": text})
                    results["summary"] = summary_result
                    
                    # Step 4: Embeddings
                    embedding_result = self.embedding_model.predict({"text": text})
                    results["embeddings"] = embedding_result
                    
                    # Store in vector DB
                    if "embedding" in embedding_result:
                        embedding_vector = embedding_result["embedding"]
                        import numpy as np
                        self.vector_db.add_vectors(
                            np.array([embedding_vector]),
                            [{"file_path": file_path, "text": text[:100]}]
                        )
                        self.vector_db.save_index()
            
            logger.info("Document processing completed")
            return results
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def answer_question(self, question: str, context: str, job_id: Optional[int] = None) -> Dict[str, Any]:
        """Answer a question using RAG."""
        logger.info(f"Answering question: {question[:50]}...")
        
        try:
            # Step 1: Get relevant context from vector DB (if job_id provided)
            if job_id and self.vector_db:
                # Get document embedding
                query_embedding = self.embedding_model.encode(question)
                import numpy as np
                query_vector = np.array([query_embedding])
                
                # Search for relevant documents
                search_results = self.vector_db.search(query_vector, k=3)
                
                # Combine context from search results
                if search_results:
                    relevant_contexts = [r["metadata"].get("text", "") for r in search_results]
                    context = " ".join(relevant_contexts) + " " + context
            
            # Step 2: Use QA model
            qa_result = self.qa_model.predict({
                "question": question,
                "context": context
            })
            
            return qa_result
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise
    
    def get_model_versions(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "ocr": self.ocr_model.get_model_info() if self.ocr_model else None,
            "ner": self.ner_model.get_model_info() if self.ner_model else None,
            "summarization": self.summarization_model.get_model_info() if self.summarization_model else None,
            "qa": self.qa_model.get_model_info() if self.qa_model else None,
            "embedding": self.embedding_model.get_model_info() if self.embedding_model else None,
            "vector_db": self.vector_db.get_stats() if self.vector_db else None
        }

