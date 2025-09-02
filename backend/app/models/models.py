from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import Column, String, JSON

if TYPE_CHECKING:
    from sqlalchemy.orm import RelationshipProperty


class RoleEnum(str, Enum):
    ADMIN = "admin"
    PUBLISHER = "publisher"
    HANDLER = "handler"
    VIEWER = "viewer"


class Role(SQLModel, table=True):
    __tablename__ = "roles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: RoleEnum = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    role_assignments: List["RoleAssignment"] = Relationship(back_populates="role")


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    role_assignments: List["RoleAssignment"] = Relationship(back_populates="user")


class RoleAssignment(SQLModel, table=True):
    __tablename__ = "role_assignments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="role_assignments")
    role: Role = Relationship(back_populates="role_assignments")


class TicketType(SQLModel, table=True):
    __tablename__ = "ticket_types"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    form_fields: List["FormField"] = Relationship(back_populates="ticket_type")
    tickets: List["Ticket"] = Relationship(back_populates="ticket_type")


class FormField(SQLModel, table=True):
    __tablename__ = "form_fields"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_type_id: int = Field(foreign_key="ticket_types.id")
    field_name: str
    field_label: str
    field_type: str  # text, number, date, select, textarea, array
    field_options: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    is_required: bool = Field(default=False)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ticket_type: TicketType = Relationship(back_populates="form_fields")


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_type_id: int = Field(foreign_key="ticket_types.id")
    ticket_number: str = Field(unique=True, index=True)
    title: str
    status: str = Field(default="draft")  # draft, submitted, processing, completed, cancelled
    priority: str = Field(default="normal")  # low, normal, high, urgent
    
    # Dynamic form data stored as JSON
    form_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Metadata
    created_by_id: int = Field(foreign_key="users.id")
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ticket_type: TicketType = Relationship(back_populates="tickets")
    images: List["Image"] = Relationship(back_populates="ticket")
    attachments: List["Attachment"] = Relationship(back_populates="ticket")
    audit_logs: List["AuditLog"] = Relationship(back_populates="ticket")


class Image(SQLModel, table=True):
    __tablename__ = "images"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id")
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    display_order: int = Field(default=0)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ticket: Ticket = Relationship(back_populates="images")
    ocr_results: List["OCRResult"] = Relationship(back_populates="image")


class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id")
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ticket: Ticket = Relationship(back_populates="attachments")


class OCRResult(SQLModel, table=True):
    __tablename__ = "ocr_results"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    image_id: int = Field(foreign_key="images.id")
    text_content: str
    confidence: float
    bbox_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    image: Image = Relationship(back_populates="ocr_results")


class Job(SQLModel, table=True):
    __tablename__ = "jobs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True)
    job_type: str  # import, export, ocr
    status: str = Field(default="pending")  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: Optional[int] = Field(default=None, foreign_key="tickets.id")
    user_id: int = Field(foreign_key="users.id")
    action: str
    description: str
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ticket: Optional[Ticket] = Relationship(back_populates="audit_logs")