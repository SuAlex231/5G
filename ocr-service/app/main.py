from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime

app = FastAPI(
    title="OCR Service",
    description="PaddleOCR-based text recognition service for Chinese text",
    version="1.0.0"
)

# Initialize PaddleOCR (CPU version)
# Use Chinese and English models
ocr = PaddleOCR(
    use_angle_cls=True, 
    lang='ch',  # Chinese + English
    use_gpu=False,  # CPU only
    show_log=False
)


class OCRRequest(BaseModel):
    image_data: Optional[str] = None  # Base64 encoded image
    image_path: Optional[str] = None  # Path to image file
    
    
class OCRTextBlock(BaseModel):
    text: str
    confidence: float
    bbox: Dict[str, Any]  # Bounding box coordinates


class OCRResponse(BaseModel):
    text_blocks: List[OCRTextBlock]
    full_text: str
    processing_time_ms: int


def process_image_bytes(image_bytes: bytes) -> List[OCRTextBlock]:
    """Process image bytes and return OCR results."""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        # Run OCR
        results = ocr.ocr(img, cls=True)
        
        text_blocks = []
        if results and results[0]:
            for line in results[0]:
                if line:
                    # PaddleOCR returns: [bbox, (text, confidence)]
                    bbox_coords = line[0]  # 4 corner points
                    text_info = line[1]
                    text = text_info[0]
                    confidence = text_info[1]
                    
                    # Convert bbox to simple format
                    x_coords = [point[0] for point in bbox_coords]
                    y_coords = [point[1] for point in bbox_coords]
                    
                    bbox = {
                        "x": min(x_coords),
                        "y": min(y_coords),
                        "width": max(x_coords) - min(x_coords),
                        "height": max(y_coords) - min(y_coords),
                        "coordinates": bbox_coords
                    }
                    
                    text_blocks.append(OCRTextBlock(
                        text=text,
                        confidence=confidence,
                        bbox=bbox
                    ))
        
        return text_blocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OCR Service",
        "version": "1.0.0"
    }


@app.post("/ocr", response_model=OCRResponse)
async def perform_ocr(
    file: Optional[UploadFile] = File(None),
    request_data: Optional[OCRRequest] = None
):
    """Perform OCR on uploaded image or base64 data."""
    start_time = datetime.now()
    
    try:
        image_bytes = None
        
        if file:
            # Handle uploaded file
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            image_bytes = await file.read()
            
        elif request_data and request_data.image_data:
            # Handle base64 data
            try:
                image_bytes = base64.b64decode(request_data.image_data)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid base64 image data")
                
        elif request_data and request_data.image_path:
            # Handle file path (for MinIO integration)
            # TODO: Implement MinIO file retrieval
            raise HTTPException(status_code=400, detail="File path processing not yet implemented")
        
        else:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        if not image_bytes:
            raise HTTPException(status_code=400, detail="No image data received")
        
        # Process image
        text_blocks = process_image_bytes(image_bytes)
        
        # Combine all text
        full_text = " ".join([block.text for block in text_blocks])
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return OCRResponse(
            text_blocks=text_blocks,
            full_text=full_text,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/ocr/batch")
async def batch_ocr(files: List[UploadFile] = File(...)):
    """Perform OCR on multiple images."""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed per batch")
    
    results = []
    for i, file in enumerate(files):
        try:
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "error": "File must be an image"
                })
                continue
            
            image_bytes = await file.read()
            text_blocks = process_image_bytes(image_bytes)
            full_text = " ".join([block.text for block in text_blocks])
            
            results.append({
                "filename": file.filename,
                "text_blocks": [block.dict() for block in text_blocks],
                "full_text": full_text
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "OCR Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )