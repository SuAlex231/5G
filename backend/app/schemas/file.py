from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TicketImageBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    order_index: int = 0
    metadata: Dict[str, Any] = {}

class TicketImageCreate(TicketImageBase):
    ticket_id: int
    minio_key: str

class TicketImageUpdate(BaseModel):
    order_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class TicketImageResponse(TicketImageBase):
    id: int
    ticket_id: int
    minio_key: str
    created_at: datetime

    class Config:
        from_attributes = True

class AttachmentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    metadata: Dict[str, Any] = {}

class AttachmentCreate(AttachmentBase):
    ticket_id: int
    minio_key: str

class AttachmentResponse(AttachmentBase):
    id: int
    ticket_id: int
    minio_key: str
    created_at: datetime

    class Config:
        from_attributes = True

class OCRResultBase(BaseModel):
    text_data: Dict[str, Any] = {}
    confidence: float = 0.0
    bbox_data: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

class OCRResultCreate(OCRResultBase):
    image_id: int

class OCRResultResponse(OCRResultBase):
    id: int
    image_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    upload_url: str
    file_key: str
    fields: Dict[str, Any] = {}

class ApplyOCRRequest(BaseModel):
    field_mappings: Dict[str, str]  # field_name -> ocr_text_key