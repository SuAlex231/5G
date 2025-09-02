# Celery tasks
from celery import Celery
from app.worker.celery import celery_app
from app.core.database import SessionLocal
from app.models.file import OCRResult, TicketImage
from app.models.audit import Job, JobStatus, JobType
from app.services.minio_client import minio_client
from app.core.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_ocr(self, image_id: int):
    """Process OCR for an image"""
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(
            Job.parameters.contains({"image_id": image_id}),
            Job.job_type == JobType.ocr_processing
        ).first()
        
        if job:
            job.status = JobStatus.running
            db.commit()
        
        # Get image
        image = db.query(TicketImage).filter(TicketImage.id == image_id).first()
        if not image:
            raise Exception(f"Image {image_id} not found")
        
        # Call OCR service
        with httpx.Client() as client:
            response = client.post(
                f"{settings.OCR_SERVICE_URL}/ocr",
                json={
                    "bucket": settings.MINIO_BUCKET_UPLOADS,
                    "object_key": image.minio_key
                }
            )
            
            if response.status_code != 200:
                raise Exception("OCR service failed")
            
            ocr_data = response.json()
            
            # Save OCR result
            ocr_result = OCRResult(
                image_id=image_id,
                text_data=ocr_data.get("texts", {}),
                confidence=int(ocr_data.get("confidence", 0) * 100),
                bbox_data=ocr_data.get("boxes", []),
                processing_time=int(ocr_data.get("processing_time", 0))
            )
            
            db.add(ocr_result)
            
            if job:
                job.status = JobStatus.completed
                job.result = {"ocr_result_id": ocr_result.id}
            
            db.commit()
            
            return {"status": "success", "ocr_result_id": ocr_result.id}
            
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        
        if job:
            job.status = JobStatus.failed
            job.error_message = str(e)
            db.commit()
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True)
def export_excel(self, ticket_type_id: int, ticket_ids: list):
    """Export tickets to Excel"""
    # Placeholder for Excel export implementation
    return {"status": "success", "file_path": "exports/tickets.xlsx"}

@celery_app.task(bind=True)
def export_docx(self, ticket_id: int):
    """Export ticket to DOCX with images"""
    # Placeholder for DOCX export implementation
    return {"status": "success", "file_path": f"exports/ticket_{ticket_id}.docx"}