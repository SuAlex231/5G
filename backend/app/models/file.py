from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TicketImage(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    minio_key = Column(String(512), nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    metadata = Column(JSON, nullable=False, default={})  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="images")
    ocr_results = relationship("OCRResult", back_populates="image")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    minio_key = Column(String(512), nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    text_data = Column(JSON, nullable=False, default={})  # Extracted text with positions
    confidence = Column(Integer, nullable=False, default=0)  # Overall confidence
    bbox_data = Column(JSON, nullable=True, default={})  # Bounding box information
    processing_time = Column(Integer, nullable=True)  # Time taken for OCR
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    image = relationship("TicketImage", back_populates="ocr_results")