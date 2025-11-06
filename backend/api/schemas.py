"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Schemas
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobResult(BaseModel):
    job_id: str
    filename: str
    ocr_text: Optional[str] = None
    summary: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    created_at: datetime


# Chat Schemas
class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    message: str
    answer: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime


# Admin Schemas
class RetrainRequest(BaseModel):
    model_type: str  # ocr, ner, summarization, qa
    training_data_path: Optional[str] = None
    epochs: Optional[int] = 3
    batch_size: Optional[int] = 16


class ModelVersionResponse(BaseModel):
    id: int
    model_name: str
    version: str
    model_type: str
    is_active: bool
    accuracy_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    trained_at: Optional[datetime] = None

