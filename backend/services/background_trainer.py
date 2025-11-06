"""Background task for continuous model training."""
import asyncio
from services.incremental_trainer import IncrementalTrainer
from services.active_learning_service import ActiveLearningService
from utils.logger import logger
from config import settings
from pathlib import Path


class BackgroundTrainer:
    """Background service for automatic model training."""
    
    def __init__(self):
        self.incremental_trainer = IncrementalTrainer()
        self.active_learning = ActiveLearningService()
        self.is_running = False
    
    async def start(self):
        """Start background training loop."""
        self.is_running = True
        logger.info("Background trainer started")
        
        while self.is_running:
            try:
                # Check every hour for new training data
                await self.incremental_trainer.check_and_train(model_type="all")
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Error in background training: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error before retrying
    
    def stop(self):
        """Stop background training."""
        self.is_running = False
        logger.info("Background trainer stopped")


# Global background trainer instance
background_trainer = BackgroundTrainer()


async def start_background_training():
    """Start background training service."""
    await background_trainer.start()

