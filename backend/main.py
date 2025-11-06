"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the app."""
    # Startup
    logger.info("Starting background training service...")
    from services.background_trainer import start_background_training
    # Start background trainer in background
    import asyncio
    asyncio.create_task(start_background_training())
    yield
    # Shutdown
    logger.info("Shutting down background training service...")
    from services.background_trainer import background_trainer
    background_trainer.stop()


# Create FastAPI app
app = FastAPI(
    title="AI Document Analysis API",
    description="Self-hosted AI document analysis system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from api import auth, upload, jobs, chat, admin, export, feedback

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(export.router)
app.include_router(feedback.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Document Analysis API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

