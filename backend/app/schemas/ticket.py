from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ticket import TicketStatus

class TicketTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    schema_config: Dict[str, Any] = {}
    is_active: bool = True

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schema_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TicketType(TicketTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FormFieldBase(BaseModel):
    field_name: str
    field_type: str
    field_label: str
    config: Dict[str, Any] = {}
    order_index: int = 0
    is_required: bool = False

class FormFieldCreate(FormFieldBase):
    ticket_type_id: int

class FormField(FormFieldBase):
    id: int
    ticket_type_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TicketBase(BaseModel):
    title: str
    data: Dict[str, Any] = {}

class TicketCreate(TicketBase):
    ticket_type_id: int

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TicketStatus] = None
    data: Optional[Dict[str, Any]] = None
    assigned_to: Optional[int] = None

class Ticket(TicketBase):
    id: int
    ticket_type_id: int
    user_id: int
    ticket_number: str
    status: TicketStatus
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketWithDetails(Ticket):
    ticket_type: TicketType
    images: List["TicketImageResponse"] = []

class TicketListResponse(BaseModel):
    items: List[Ticket]
    total: int
    page: int
    size: int
    pages: int