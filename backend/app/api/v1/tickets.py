from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
import uuid
from datetime import datetime

from ...core.database import get_session
from ...core.deps import get_current_active_user, require_admin_or_publisher, require_any_role
from ...models.models import Ticket, TicketType, User, Image, OCRResult, AuditLog
from ...schemas.schemas import (
    TicketResponse, TicketCreate, TicketUpdate, 
    ImageResponse, OCRResultResponse, OCRApplyRequest
)
from ...tasks import process_ocr_task
from ...services.minio_service import MinIOService
from ...services.docx_service import create_ticket_docx

router = APIRouter()
minio_service = MinIOService()


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    ticket_type_id: Optional[int] = None
):
    """List tickets with filtering."""
    statement = select(Ticket)
    
    # Apply filters
    if status_filter:
        statement = statement.where(Ticket.status == status_filter)
    if ticket_type_id:
        statement = statement.where(Ticket.ticket_type_id == ticket_type_id)
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit).order_by(Ticket.created_at.desc())
    
    tickets = session.exec(statement).all()
    return [TicketResponse.model_validate(ticket) for ticket in tickets]


@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Create a new ticket."""
    # Verify ticket type exists
    ticket_type = session.get(TicketType, ticket_data.ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Generate ticket number
    ticket_number = f"T{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Create ticket
    ticket = Ticket(
        ticket_type_id=ticket_data.ticket_type_id,
        ticket_number=ticket_number,
        title=ticket_data.title,
        form_data=ticket_data.form_data,
        priority=ticket_data.priority,
        created_by_id=current_user.id
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Log creation
    audit_log = AuditLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="create",
        description=f"Ticket created: {ticket.title}",
        new_values=ticket_data.model_dump()
    )
    session.add(audit_log)
    session.commit()
    
    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """Get ticket by ID."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return TicketResponse.model_validate(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Update ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Store old values for audit
    old_values = {
        "title": ticket.title,
        "form_data": ticket.form_data,
        "status": ticket.status,
        "priority": ticket.priority,
        "assigned_to_id": ticket.assigned_to_id
    }
    
    # Update ticket
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    ticket.updated_at = datetime.utcnow()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Log update
    audit_log = AuditLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="update",
        description=f"Ticket updated: {ticket.title}",
        old_values=old_values,
        new_values=update_data
    )
    session.add(audit_log)
    session.commit()
    
    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}/images", response_model=List[ImageResponse])
async def list_ticket_images(
    ticket_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """List images for a ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    statement = select(Image).where(Image.ticket_id == ticket_id).order_by(Image.display_order)
    images = session.exec(statement).all()
    
    return [ImageResponse.model_validate(image) for image in images]


@router.post("/{ticket_id}/images", response_model=ImageResponse)
async def upload_ticket_image(
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Upload image for a ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check image count limit
    image_count = session.exec(select(Image).where(Image.ticket_id == ticket_id)).all()
    if len(image_count) >= 8:  # MAX_IMAGES_PER_TICKET
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {8} images allowed per ticket"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # Upload to MinIO
    filename = f"images/{ticket_id}/{uuid.uuid4()}.jpg"
    file_url = await minio_service.upload_file(file, filename)
    
    # Create image record
    image = Image(
        ticket_id=ticket_id,
        filename=filename,
        original_filename=file.filename,
        file_path=file_url,
        file_size=file.size,
        mime_type=file.content_type,
        display_order=len(image_count)
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    
    return ImageResponse.model_validate(image)


@router.delete("/{ticket_id}/images/{image_id}")
async def delete_ticket_image(
    ticket_id: int,
    image_id: int,
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Delete an image from a ticket."""
    image = session.get(Image, image_id)
    if not image or image.ticket_id != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete from MinIO
    await minio_service.delete_file(image.filename)
    
    # Delete from database
    session.delete(image)
    session.commit()
    
    return {"message": "Image deleted successfully"}


@router.post("/{ticket_id}/images/{image_id}/ocr")
async def trigger_ocr(
    ticket_id: int,
    image_id: int,
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Trigger OCR processing for an image."""
    image = session.get(Image, image_id)
    if not image or image.ticket_id != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Start OCR task
    task = process_ocr_task.delay(image_id)
    
    return {"message": "OCR processing started", "task_id": task.id}


@router.get("/{ticket_id}/images/{image_id}/ocr-result", response_model=List[OCRResultResponse])
async def get_ocr_result(
    ticket_id: int,
    image_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """Get OCR results for an image."""
    image = session.get(Image, image_id)
    if not image or image.ticket_id != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    statement = select(OCRResult).where(OCRResult.image_id == image_id)
    ocr_results = session.exec(statement).all()
    
    return [OCRResultResponse.model_validate(result) for result in ocr_results]


@router.post("/{ticket_id}/apply-ocr")
async def apply_ocr_to_ticket(
    ticket_id: int,
    apply_data: OCRApplyRequest,
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Apply selected OCR text to ticket fields."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update form data with OCR mappings
    updated_form_data = ticket.form_data.copy()
    for field_name, selected_text in apply_data.field_mappings.items():
        updated_form_data[field_name] = selected_text
    
    # Store old values for audit
    old_form_data = ticket.form_data
    
    # Update ticket
    ticket.form_data = updated_form_data
    ticket.updated_at = datetime.utcnow()
    session.add(ticket)
    session.commit()
    
    # Log OCR application
    audit_log = AuditLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="apply_ocr",
        description="Applied OCR text to ticket fields",
        old_values={"form_data": old_form_data},
        new_values={"form_data": updated_form_data}
    )
    session.add(audit_log)
    session.commit()
    
    return {"message": "OCR data applied successfully"}


@router.get("/{ticket_id}/export-docx")
async def export_ticket_docx(
    ticket_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """Export ticket images to DOCX."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Get ticket images
    statement = select(Image).where(Image.ticket_id == ticket_id).order_by(Image.display_order)
    images = session.exec(statement).all()
    
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images found for this ticket"
        )
    
    # Generate DOCX
    docx_file = await create_ticket_docx(ticket, images)
    
    return {"message": "DOCX export completed", "download_url": docx_file}