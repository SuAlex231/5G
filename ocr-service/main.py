from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from paddleocr import PaddleOCR
from PIL import Image
import io
import time
import logging
import os
from typing import List, Dict, Any, Optional
from minio import Minio
from minio.error import S3Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="5G Ticketing OCR Service",
    description="PaddleOCR-based text extraction service for 5G ticketing system",
    version="1.0.0"
)

# Initialize PaddleOCR
try:
    # CPU-only mode with Chinese and English support
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
    logger.info("PaddleOCR initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
    ocr_engine = None

class OCRRequest(BaseModel):
    bucket: str
    object_key: str

class OCRDirectRequest(BaseModel):
    image_base64: str

class OCRResponse(BaseModel):
    texts: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    boxes: Optional[List[List[List[int]]]] = None

def extract_text_from_image(image: Image.Image) -> Dict[str, Any]:
    """Extract text from PIL Image using PaddleOCR"""
    if ocr_engine is None:
        raise HTTPException(status_code=500, detail="OCR engine not initialized")
    
    start_time = time.time()
    
    try:
        # Convert PIL image to numpy array
        import numpy as np
        image_array = np.array(image)
        
        # Run OCR
        results = ocr_engine.ocr(image_array, cls=True)
        
        processing_time = time.time() - start_time
        
        if not results or not results[0]:
            return {
                "texts": [],
                "confidence": 0.0,
                "processing_time": processing_time,
                "boxes": []
            }
        
        # Process results
        texts = []
        boxes = []
        total_confidence = 0.0
        valid_results = 0
        
        for line in results[0]:
            if len(line) >= 2:
                box = line[0]  # Bounding box coordinates
                text_info = line[1]  # Text and confidence
                
                text = text_info[0] if isinstance(text_info, (list, tuple)) else str(text_info)
                confidence = text_info[1] if isinstance(text_info, (list, tuple)) and len(text_info) > 1 else 0.8
                
                texts.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": box
                })
                boxes.append(box)
                
                total_confidence += confidence
                valid_results += 1
        
        avg_confidence = total_confidence / valid_results if valid_results > 0 else 0.0
        
        # Create simplified key-value extraction based on common patterns
        simplified_texts = {}
        for item in texts:
            text = item["text"].strip()
            
            # Common field patterns for 5G ticketing
            if "工单号" in text or "ticket" in text.lower():
                simplified_texts["ticket_number"] = text
            elif "区县" in text or "district" in text.lower():
                simplified_texts["district"] = text
            elif "PCI" in text.upper():
                simplified_texts["pci"] = text
            elif "SINR" in text.upper():
                simplified_texts["sinr"] = text
            elif "RSRP" in text.upper():
                simplified_texts["rsrp"] = text
            elif "上传" in text or "upload" in text.lower():
                simplified_texts["upload_speed"] = text
            elif "下载" in text or "download" in text.lower():
                simplified_texts["download_speed"] = text
            elif "频率" in text or "freq" in text.lower():
                simplified_texts["frequency"] = text
            elif "小区" in text or "cell" in text.lower():
                simplified_texts["cell_id"] = text
            
            # Store by index as well
            simplified_texts[f"text_{len(simplified_texts)}"] = text
        
        return {
            "texts": simplified_texts,
            "raw_texts": texts,
            "confidence": avg_confidence,
            "processing_time": processing_time,
            "boxes": boxes
        }
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "service": "5G Ticketing OCR Service",
        "version": "1.0.0",
        "status": "healthy" if ocr_engine else "unhealthy",
        "engine": "PaddleOCR"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if ocr_engine else "unhealthy",
        "engine_loaded": ocr_engine is not None
    }

@app.post("/ocr", response_model=Dict[str, Any])
async def process_ocr_from_minio(request: OCRRequest):
    """Process OCR from MinIO object"""
    try:
        # Initialize MinIO client
        minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        minio_secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_secure
        )
        
        # Get object from MinIO
        response = client.get_object(request.bucket, request.object_key)
        image_data = response.read()
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process OCR
        result = extract_text_from_image(image)
        
        return result
        
    except S3Error as e:
        logger.error(f"MinIO error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"File not found in MinIO: {str(e)}")
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.post("/ocr-upload", response_model=Dict[str, Any])
async def process_ocr_from_upload(file: UploadFile = File(...)):
    """Process OCR from direct file upload"""
    try:
        # Read file
        content = await file.read()
        
        # Open image
        image = Image.open(io.BytesIO(content))
        
        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process OCR
        result = extract_text_from_image(image)
        
        return result
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)