from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.models import RoleEnum


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


# Role Schemas
class RoleResponse(BaseModel):
    id: int
    name: RoleEnum
    description: Optional[str] = None

    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Ticket Type Schemas
class TicketTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class TicketTypeCreate(TicketTypeBase):
    pass


class TicketTypeResponse(TicketTypeBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Form Field Schemas
class FormFieldBase(BaseModel):
    field_name: str
    field_label: str
    field_type: str
    field_options: Optional[Dict[str, Any]] = None
    is_required: bool = False
    display_order: int = 0


class FormFieldCreate(FormFieldBase):
    pass


class FormFieldResponse(FormFieldBase):
    id: int
    ticket_type_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Ticket Schemas
class TicketBase(BaseModel):
    title: str
    form_data: Dict[str, Any] = {}
    priority: str = "normal"


class TicketCreate(TicketBase):
    ticket_type_id: int


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None


class TicketResponse(TicketBase):
    id: int
    ticket_type_id: int
    ticket_number: str
    status: str
    created_by_id: int
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Image Schemas
class ImageResponse(BaseModel):
    id: int
    ticket_id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    display_order: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# OCR Schemas
class OCRResultResponse(BaseModel):
    id: int
    image_id: int
    text_content: str
    confidence: float
    bbox_data: Optional[Dict[str, Any]] = None
    processed_at: datetime

    class Config:
        from_attributes = True


class OCRApplyRequest(BaseModel):
    field_mappings: Dict[str, str]  # field_name -> selected_text


# Job Schemas
class JobResponse(BaseModel):
    id: int
    job_id: str
    job_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Import/Export Schemas
class ImportValidationResult(BaseModel):
    row_number: int
    errors: List[str] = []
    warnings: List[str] = []


class ImportResult(BaseModel):
    job_id: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    validation_results: List[ImportValidationResult] = []


# Generic Response
class MessageResponse(BaseModel):
    message: str


# Health Check
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"