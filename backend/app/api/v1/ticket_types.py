from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
import uuid

from ...core.database import get_session
from ...core.deps import require_admin, require_any_role, require_admin_or_publisher
from ...models.models import TicketType, FormField, User
from ...schemas.schemas import (
    TicketTypeResponse, TicketTypeCreate, FormFieldResponse, FormFieldCreate,
    JobResponse, ImportResult
)
from ...tasks import process_import_task, process_export_task

router = APIRouter()


@router.get("/", response_model=List[TicketTypeResponse])
async def list_ticket_types(
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session),
    include_inactive: bool = False
):
    """List all ticket types."""
    statement = select(TicketType)
    if not include_inactive:
        statement = statement.where(TicketType.is_active == True)
    
    ticket_types = session.exec(statement).all()
    return [TicketTypeResponse.model_validate(tt) for tt in ticket_types]


@router.post("/", response_model=TicketTypeResponse)
async def create_ticket_type(
    ticket_type_data: TicketTypeCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Create a new ticket type (admin only)."""
    # Check if name already exists
    existing = session.exec(
        select(TicketType).where(TicketType.name == ticket_type_data.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket type name already exists"
        )
    
    ticket_type = TicketType(
        name=ticket_type_data.name,
        description=ticket_type_data.description
    )
    session.add(ticket_type)
    session.commit()
    session.refresh(ticket_type)
    
    return TicketTypeResponse.model_validate(ticket_type)


@router.get("/{ticket_type_id}", response_model=TicketTypeResponse)
async def get_ticket_type(
    ticket_type_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """Get ticket type by ID."""
    ticket_type = session.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    return TicketTypeResponse.model_validate(ticket_type)


@router.get("/{ticket_type_id}/fields", response_model=List[FormFieldResponse])
async def list_ticket_type_fields(
    ticket_type_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session)
):
    """List form fields for a ticket type."""
    ticket_type = session.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    statement = select(FormField).where(
        FormField.ticket_type_id == ticket_type_id
    ).order_by(FormField.display_order)
    
    fields = session.exec(statement).all()
    return [FormFieldResponse.model_validate(field) for field in fields]


@router.post("/{ticket_type_id}/fields", response_model=FormFieldResponse)
async def create_form_field(
    ticket_type_id: int,
    field_data: FormFieldCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Create a form field for a ticket type (admin only)."""
    ticket_type = session.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    form_field = FormField(
        ticket_type_id=ticket_type_id,
        field_name=field_data.field_name,
        field_label=field_data.field_label,
        field_type=field_data.field_type,
        field_options=field_data.field_options,
        is_required=field_data.is_required,
        display_order=field_data.display_order
    )
    session.add(form_field)
    session.commit()
    session.refresh(form_field)
    
    return FormFieldResponse.model_validate(form_field)


@router.post("/{ticket_type_id}/import")
async def import_excel(
    ticket_type_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin_or_publisher),
    session: Session = Depends(get_session)
):
    """Import tickets from Excel file."""
    ticket_type = session.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    # Save uploaded file temporarily
    temp_filename = f"/tmp/import_{uuid.uuid4().hex}.xlsx"
    with open(temp_filename, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Start import task
    task = process_import_task.delay(temp_filename, ticket_type_id, current_user.id)
    
    return {
        "message": "Import started",
        "job_id": task.id,
        "status": "pending"
    }


@router.post("/{ticket_type_id}/export")
async def export_excel(
    ticket_type_id: int,
    current_user: User = Depends(require_any_role),
    session: Session = Depends(get_session),
    status_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Export tickets to Excel file."""
    ticket_type = session.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Build filters
    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    # Start export task
    task = process_export_task.delay(ticket_type_id, filters)
    
    return {
        "message": "Export started",
        "job_id": task.id,
        "status": "pending"
    }