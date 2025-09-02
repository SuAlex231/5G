from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class JobStatus(enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class JobType(enum.Enum):
    ocr_processing = "ocr_processing"
    excel_import = "excel_import"
    excel_export = "excel_export"
    docx_export = "docx_export"
    email_notification = "email_notification"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.pending)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parameters = Column(JSON, nullable=False, default={})  # Job input parameters
    result = Column(JSON, nullable=True, default={})  # Job result data
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # create, read, update, delete
    resource_type = Column(String(50), nullable=False)  # ticket, user, role, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True, default={})  # Additional details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())