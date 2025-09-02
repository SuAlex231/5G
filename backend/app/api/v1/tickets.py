from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import get_current_active_user, require_publisher, require_handler, require_viewer
from app.models.user import User
from app.models.ticket import Ticket, TicketType, FormField, TicketStatus
from app.schemas.ticket import (
    Ticket as TicketSchema, 
    TicketCreate, 
    TicketUpdate, 
    TicketWithDetails,
    TicketListResponse,
    TicketType as TicketTypeSchema,
    TicketTypeCreate,
    FormField as FormFieldSchema,
    FormFieldCreate
)
import uuid

router = APIRouter()

def generate_ticket_number() -> str:
    """Generate unique ticket number"""
    return f"TK-{str(uuid.uuid4()).upper()[:8]}"

@router.get("/", response_model=TicketListResponse)
async def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TicketStatus] = None,
    search: Optional[str] = None,
    ticket_type_id: Optional[int] = None
):
    """List tickets with filtering"""
    query = db.query(Ticket)
    
    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    
    if ticket_type_id:
        query = query.filter(Ticket.ticket_type_id == ticket_type_id)
    
    if search:
        query = query.filter(
            or_(
                Ticket.title.ilike(f"%{search}%"),
                Ticket.ticket_number.ilike(f"%{search}%")
            )
        )
    
    # Count total
    total = query.count()
    
    # Get paginated results
    tickets = query.offset(skip).limit(limit).all()
    
    return TicketListResponse(
        items=tickets,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=TicketSchema)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_publisher)
):
    """Create a new ticket"""
    # Verify ticket type exists
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket.ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Create ticket
    db_ticket = Ticket(
        ticket_type_id=ticket.ticket_type_id,
        user_id=current_user.id,
        ticket_number=generate_ticket_number(),
        title=ticket.title,
        data=ticket.data,
        status=TicketStatus.draft
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

@router.get("/{ticket_id}", response_model=TicketWithDetails)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer)
):
    """Get ticket by ID"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return ticket

@router.put("/{ticket_id}", response_model=TicketSchema)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_handler)
):
    """Update ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update fields
    update_data = ticket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    db.commit()
    db.refresh(ticket)
    
    return ticket

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_publisher)
):
    """Delete ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    db.delete(ticket)
    db.commit()
    
    return {"message": "Ticket deleted successfully"}

# Ticket Types endpoints
@router.get("/types/", response_model=List[TicketTypeSchema])
async def list_ticket_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer)
):
    """List all ticket types"""
    ticket_types = db.query(TicketType).filter(TicketType.is_active == True).all()
    return ticket_types

@router.post("/types/", response_model=TicketTypeSchema)
async def create_ticket_type(
    ticket_type: TicketTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_publisher)
):
    """Create a new ticket type"""
    db_ticket_type = TicketType(**ticket_type.dict())
    db.add(db_ticket_type)
    db.commit()
    db.refresh(db_ticket_type)
    return db_ticket_type

@router.get("/types/{ticket_type_id}/fields", response_model=List[FormFieldSchema])
async def get_ticket_type_fields(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer)
):
    """Get form fields for a ticket type"""
    fields = db.query(FormField).filter(
        FormField.ticket_type_id == ticket_type_id
    ).order_by(FormField.order_index).all()
    
    return fields