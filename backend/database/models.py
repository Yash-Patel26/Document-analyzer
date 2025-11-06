"""Database models for the application."""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
import enum


class UserRole(str, enum.Enum):
    """User roles enum."""
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class JobStatus(str, enum.Enum):
    """Job status enum."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    """Refresh token model."""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class Job(Base):
    """Document analysis job model."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default=JobStatus.PENDING.value)
    progress = Column(Float, default=0.0)
    current_step = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Analysis results
    ocr_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    entities = Column(JSON, nullable=True)
    embeddings = Column(JSON, nullable=True)  # Vector embeddings
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="jobs")
    chat_messages = relationship("ChatMessage", back_populates="job")


class ChatMessage(Base):
    """Chat message model for QA."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="chat_messages")


class ModelVersion(Base):
    """AI model version tracking."""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_path = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # ocr, ner, summarization, qa, embedding
    is_active = Column(Boolean, default=False)
    accuracy_metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trained_at = Column(DateTime(timezone=True), nullable=True)

