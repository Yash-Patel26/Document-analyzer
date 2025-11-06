"""Admin endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import User, ModelVersion
from api.dependencies import get_current_admin
from api.schemas import RetrainRequest, ModelVersionResponse
from utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/retrain")
async def retrain_model(
    request: RetrainRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Trigger model retraining."""
    logger.info(f"Retrain request for {request.model_type} by {current_user.username}")
    
    # This would typically trigger a background job
    # For now, return a placeholder response
    return {
        "message": f"Retraining initiated for {request.model_type}",
        "status": "pending",
        "requested_by": current_user.username
    }


@router.get("/models", response_model=list[ModelVersionResponse])
async def list_models(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all model versions."""
    models = db.query(ModelVersion).order_by(
        ModelVersion.created_at.desc()
    ).all()
    
    return [
        ModelVersionResponse(
            id=model.id,
            model_name=model.model_name,
            version=model.version,
            model_type=model.model_type,
            is_active=model.is_active,
            accuracy_metrics=model.accuracy_metrics,
            created_at=model.created_at,
            trained_at=model.trained_at
        )
        for model in models
    ]


@router.post("/models/{model_id}/activate")
async def activate_model(
    model_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate a model version."""
    model = db.query(ModelVersion).filter(ModelVersion.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Deactivate all models of the same type
    db.query(ModelVersion).filter(
        ModelVersion.model_type == model.model_type
    ).update({"is_active": False})
    
    # Activate this model
    model.is_active = True
    db.commit()
    
    logger.info(f"Model {model.model_name} v{model.version} activated by {current_user.username}")
    
    return {"message": "Model activated", "model_id": model_id}

