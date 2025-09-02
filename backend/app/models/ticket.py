from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TicketStatus(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class TicketType(Base):
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    schema_config = Column(JSON, nullable=False, default={})  # Configuration for dynamic form
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    form_fields = relationship("FormField", back_populates="ticket_type")
    tickets = relationship("Ticket", back_populates="ticket_type")

class FormField(Base):
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)  # text, number, date, select, textarea, array
    field_label = Column(String(255), nullable=False)
    config = Column(JSON, nullable=False, default={})  # Field-specific configuration
    order_index = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket_type = relationship("TicketType", back_populates="form_fields")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.draft)
    data = Column(JSON, nullable=False, default={})  # Dynamic field values
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    ticket_type = relationship("TicketType", back_populates="tickets")
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    images = relationship("TicketImage", back_populates="ticket")
    attachments = relationship("Attachment", back_populates="ticket")