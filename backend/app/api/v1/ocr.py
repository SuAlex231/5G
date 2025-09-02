from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.file import TicketImage, OCRResult
from app.models.ticket import Ticket
from app.schemas.file import OCRResultResponse, ApplyOCRRequest
import httpx
import json

router = APIRouter()

@router.post("/images/{image_id}/process")
async def trigger_image_ocr(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger OCR processing for an image"""
    # Get image
    image = db.query(TicketImage).filter(TicketImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    try:
        # Call OCR service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OCR_SERVICE_URL}/ocr",
                json={
                    "bucket": settings.MINIO_BUCKET_UPLOADS,
                    "object_key": image.minio_key
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OCR processing failed"
                )
            
            ocr_data = response.json()
            
            # Save OCR result
            ocr_result = OCRResult(
                image_id=image_id,
                text_data=ocr_data.get("texts", []),
                confidence=ocr_data.get("confidence", 0.0),
                bbox_data=ocr_data.get("boxes", []),
                processing_time=ocr_data.get("processing_time")
            )
            
            db.add(ocr_result)
            db.commit()
            db.refresh(ocr_result)
            
            return {"message": "OCR processing completed", "result_id": ocr_result.id}
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to communicate with OCR service: {str(e)}"
        )

@router.get("/images/{image_id}/results", response_model=OCRResultResponse)
async def get_image_ocr_results(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get OCR results for an image"""
    # Get latest OCR result for image
    ocr_result = db.query(OCRResult).filter(
        OCRResult.image_id == image_id
    ).order_by(OCRResult.created_at.desc()).first()
    
    if not ocr_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No OCR results found for this image"
        )
    
    return ocr_result

@router.post("/tickets/{ticket_id}/apply-ocr")
async def apply_ocr_to_ticket(
    ticket_id: int,
    apply_request: ApplyOCRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Apply OCR results to ticket fields"""
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Get ticket images and their OCR results
    images = db.query(TicketImage).filter(TicketImage.ticket_id == ticket_id).all()
    
    updated_data = ticket.data.copy()
    applied_mappings = {}
    
    for field_name, ocr_key in apply_request.field_mappings.items():
        # Find OCR result containing this key
        for image in images:
            ocr_result = db.query(OCRResult).filter(
                OCRResult.image_id == image.id
            ).order_by(OCRResult.created_at.desc()).first()
            
            if ocr_result and ocr_result.text_data:
                # Simple key-based lookup in OCR text data
                if ocr_key in ocr_result.text_data:
                    updated_data[field_name] = ocr_result.text_data[ocr_key]
                    applied_mappings[field_name] = ocr_result.text_data[ocr_key]
                    break
    
    # Update ticket data
    ticket.data = updated_data
    db.commit()
    
    return {
        "message": "OCR results applied to ticket",
        "applied_mappings": applied_mappings
    }

@router.get("/tickets/{ticket_id}/available-ocr-data")
async def get_available_ocr_data(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all available OCR data for a ticket"""
    # Get ticket images and their OCR results
    images = db.query(TicketImage).filter(TicketImage.ticket_id == ticket_id).all()
    
    ocr_data = {}
    
    for image in images:
        ocr_result = db.query(OCRResult).filter(
            OCRResult.image_id == image.id
        ).order_by(OCRResult.created_at.desc()).first()
        
        if ocr_result:
            ocr_data[f"image_{image.id}"] = {
                "image_filename": image.original_filename,
                "text_data": ocr_result.text_data,
                "confidence": ocr_result.confidence,
                "processing_time": ocr_result.processing_time
            }
    
    return ocr_data