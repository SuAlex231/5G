from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_active_user, require_viewer
from app.core.config import settings
from app.models.user import User
from app.models.ticket import Ticket
from app.models.file import TicketImage, Attachment
from app.schemas.file import (
    TicketImageResponse, 
    TicketImageUpdate, 
    FileUploadResponse,
    AttachmentResponse
)
from app.services.minio_client import minio_client

router = APIRouter()

@router.post("/upload-url", response_model=FileUploadResponse)
async def get_upload_url(
    current_user: User = Depends(get_current_active_user)
):
    """Generate pre-signed URL for file upload"""
    try:
        result = minio_client.generate_presigned_upload_url(
            bucket=settings.MINIO_BUCKET_UPLOADS
        )
        
        return FileUploadResponse(
            upload_url=result["upload_url"],
            file_key=result["object_key"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )

@router.get("/tickets/{ticket_id}/images", response_model=List[TicketImageResponse])
async def list_ticket_images(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer)
):
    """List images for a ticket"""
    # Verify ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    images = db.query(TicketImage).filter(
        TicketImage.ticket_id == ticket_id
    ).order_by(TicketImage.order_index).all()
    
    return images

@router.post("/tickets/{ticket_id}/images", response_model=TicketImageResponse)
async def add_ticket_image(
    ticket_id: int,
    minio_key: str = Form(...),
    filename: str = Form(...),
    original_filename: str = Form(...),
    file_size: int = Form(...),
    mime_type: str = Form(...),
    order_index: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add image to ticket after upload to MinIO"""
    # Verify ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check image limit
    current_count = db.query(TicketImage).filter(
        TicketImage.ticket_id == ticket_id
    ).count()
    
    if current_count >= settings.MAX_IMAGES_PER_TICKET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_IMAGES_PER_TICKET} images allowed per ticket"
        )
    
    # Create image record
    image = TicketImage(
        ticket_id=ticket_id,
        filename=filename,
        original_filename=original_filename,
        minio_key=minio_key,
        file_size=file_size,
        mime_type=mime_type,
        order_index=order_index
    )
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return image

@router.put("/images/{image_id}", response_model=TicketImageResponse)
async def update_image(
    image_id: int,
    image_update: TicketImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update image metadata"""
    image = db.query(TicketImage).filter(TicketImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Update fields
    update_data = image_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(image, field, value)
    
    db.commit()
    db.refresh(image)
    
    return image

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete image from ticket and MinIO"""
    image = db.query(TicketImage).filter(TicketImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete from MinIO
    try:
        minio_client.delete_object(settings.MINIO_BUCKET_UPLOADS, image.minio_key)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to delete from MinIO: {str(e)}")
    
    # Delete from database
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}

@router.get("/images/{image_id}/download")
async def get_image_download_url(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer)
):
    """Get download URL for image"""
    image = db.query(TicketImage).filter(TicketImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    try:
        download_url = minio_client.generate_presigned_download_url(
            bucket=settings.MINIO_BUCKET_UPLOADS,
            object_key=image.minio_key
        )
        
        return {"download_url": download_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )