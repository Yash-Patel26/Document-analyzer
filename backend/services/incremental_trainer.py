"""Incremental training service that trains models on new data."""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
from config import settings
from utils.logger import logger
import subprocess
import json
from datetime import datetime


class IncrementalTrainer:
    """Service for incremental model training."""
    
    def __init__(self):
        self.training_data_dir = Path(settings.MODEL_STORAGE_PATH) / "training_data"
        self.models_dir = Path(settings.MODEL_STORAGE_PATH)
        self.min_samples_for_training = 10
        self.batch_train_size = 50  # Train after every N new samples
    
    async def check_and_train(self, model_type: str = "all"):
        """Check if enough data is collected and trigger training."""
        if model_type in ["summarization", "all"]:
            await self._check_and_train_summarization()
        
        if model_type in ["ner", "all"]:
            await self._check_and_train_ner()
        
        if model_type in ["qa", "all"]:
            await self._check_and_train_qa()
    
    async def _check_and_train_summarization(self):
        """Check and train summarization model."""
        data_dir = self.training_data_dir / "summarization"
        if not data_dir.exists():
            return
        
        files = list(data_dir.glob("*.json"))
        if len(files) < self.min_samples_for_training:
            return
        
        # Check if we have enough new samples since last training
        last_training = self._get_last_training_time("summarization")
        new_files = [f for f in files if f.stat().st_mtime > last_training]
        
        if len(new_files) >= self.batch_train_size:
            logger.info(f"Starting incremental training for summarization with {len(new_files)} new samples")
            await self._train_summarization_incremental(new_files)
    
    async def _check_and_train_ner(self):
        """Check and train NER model."""
        data_dir = self.training_data_dir / "ner"
        if not data_dir.exists():
            return
        
        files = list(data_dir.glob("*.json"))
        if len(files) < self.min_samples_for_training:
            return
        
        last_training = self._get_last_training_time("ner")
        new_files = [f for f in files if f.stat().st_mtime > last_training]
        
        if len(new_files) >= self.batch_train_size:
            logger.info(f"Starting incremental training for NER with {len(new_files)} new samples")
            await self._train_ner_incremental(new_files)
    
    async def _check_and_train_qa(self):
        """Check and train QA model."""
        data_dir = self.training_data_dir / "qa"
        if not data_dir.exists():
            return
        
        files = list(data_dir.glob("*.json"))
        if len(files) < self.min_samples_for_training:
            return
        
        last_training = self._get_last_training_time("qa")
        new_files = [f for f in files if f.stat().st_mtime > last_training]
        
        if len(new_files) >= self.batch_train_size:
            logger.info(f"Starting incremental training for QA with {len(new_files)} new samples")
            await self._train_qa_incremental(new_files)
    
    async def _train_summarization_incremental(self, data_files: list):
        """Train summarization model incrementally."""
        # Trigger training script in background
        import subprocess
        import sys
        
        training_script = Path(__file__).parent.parent / "models" / "training" / "incremental_train.py"
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(training_script),
                "--model", "summarization",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            logger.info(f"Incremental training for summarization completed")
        except Exception as e:
            logger.error(f"Error running incremental training: {e}")
        
        self._update_last_training_time("summarization")
    
    async def _train_ner_incremental(self, data_files: list):
        """Train NER model incrementally."""
        import subprocess
        training_script = Path(__file__).parent.parent / "models" / "training" / "incremental_train.py"
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(training_script),
                "--model", "ner",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            logger.info(f"Incremental training for NER completed")
        except Exception as e:
            logger.error(f"Error running incremental training: {e}")
        
        self._update_last_training_time("ner")
    
    async def _train_qa_incremental(self, data_files: list):
        """Train QA model incrementally."""
        import subprocess
        training_script = Path(__file__).parent.parent / "models" / "training" / "incremental_train.py"
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(training_script),
                "--model", "qa",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            logger.info(f"Incremental training for QA completed")
        except Exception as e:
            logger.error(f"Error running incremental training: {e}")
        
        self._update_last_training_time("qa")
    
    def _get_last_training_time(self, model_type: str) -> float:
        """Get last training timestamp."""
        timestamp_file = self.models_dir / f"{model_type}_last_training.txt"
        if timestamp_file.exists():
            try:
                with open(timestamp_file, 'r') as f:
                    return float(f.read().strip())
            except:
                return 0.0
        return 0.0
    
    def _update_last_training_time(self, model_type: str):
        """Update last training timestamp."""
        timestamp_file = self.models_dir / f"{model_type}_last_training.txt"
        with open(timestamp_file, 'w') as f:
            f.write(str(datetime.now().timestamp()))
    
    async def _run_training_script(self, model_type: str, *args):
        """Run training script in background."""
        # This would execute the training script asynchronously
        # For now, just log it
        logger.info(f"Would run training script for {model_type}")

