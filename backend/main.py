from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, users, tickets, files, ocr
from app.models import user, ticket, file, audit  # Import to ensure tables are created

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="5G Ticketing System API",
    description="Production-ready MVP 5G ticketing system with OCR capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])

@app.get("/")
async def root():
    return {"message": "5G Ticketing System API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "5g-ticketing-backend",
        "version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True if settings.ENVIRONMENT == "development" else False
    )