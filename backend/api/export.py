"""Report export endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import User
from api.dependencies import get_current_user
from services.job_service import JobService
from utils.logger import logger
import json
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter(prefix="/jobs", tags=["export"])


@router.get("/{job_id}/export")
async def export_report(
    job_id: str,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analysis report in various formats."""
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
    
    if format == "json":
        # Export as JSON
        data = {
            "job_id": job.job_id,
            "filename": job.filename,
            "created_at": job.created_at.isoformat(),
            "ocr_text": job.ocr_text,
            "summary": job.summary,
            "entities": job.entities
        }
        
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{job.filename}_report.json"'}
        )
    
    elif format == "csv":
        # Export as CSV
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Field", "Value"])
        writer.writerow(["Job ID", job.job_id])
        writer.writerow(["Filename", job.filename])
        writer.writerow(["Created At", job.created_at.isoformat()])
        writer.writerow(["Summary", job.summary or ""])
        
        if job.entities:
            writer.writerow([])
            writer.writerow(["Entity Type", "Entity Text"])
            for entity in job.entities.get("entities", []):
                writer.writerow([entity.get("type", ""), entity.get("text", "")])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{job.filename}_report.csv"'}
        )
    
    elif format == "pdf":
        # Export as PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"Document Analysis Report: {job.filename}", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Summary
        if job.summary:
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(job.summary, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Entities
        if job.entities:
            story.append(Paragraph("Extracted Entities", styles['Heading2']))
            for entity in job.entities.get("entities", [])[:20]:  # Limit to 20
                entity_text = f"{entity.get('type', '')}: {entity.get('text', '')}"
                story.append(Paragraph(entity_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # OCR Text (excerpt)
        if job.ocr_text:
            story.append(Paragraph("Extracted Text (Excerpt)", styles['Heading2']))
            excerpt = job.ocr_text[:500] + "..." if len(job.ocr_text) > 500 else job.ocr_text
            story.append(Paragraph(excerpt, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{job.filename}_report.pdf"'}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported: pdf, json, csv"
        )

