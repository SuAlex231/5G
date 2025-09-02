# 5G Ticketing System - Deployment Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 5173, 8000, 8001, 9000, 9001, 5432, 6379 available

### Step 1: Clone and Configure
```bash
git clone <your-repo-url>
cd 5G

# Copy environment files
cp .env.example .env
cp web/.env.example web/.env
```

### Step 2: Start All Services
```bash
# Start all services
docker compose up -d

# Wait for services to be ready (check logs)
docker compose logs -f backend
```

### Step 3: Initialize Database
```bash
# Run database initialization
docker compose exec backend python init_db.py
```

### Step 4: Access the System
- **Web App**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

**Default Admin Login:**
- Email: `admin@5g-ticketing.com`
- Password: `admin123`

## Service Architecture

### Core Services
1. **PostgreSQL** (port 5432) - Primary database
2. **Redis** (port 6379) - Cache and message broker
3. **MinIO** (ports 9000/9001) - Object storage
4. **Backend** (port 8000) - FastAPI application
5. **Worker** - Celery async processing
6. **OCR Service** (port 8001) - PaddleOCR text extraction
7. **Web App** (port 5173) - React frontend

### Data Flow
```
User → Web App → Backend API → Database/MinIO
                      ↓
OCR Images → OCR Service → Celery Worker → Results
```

## Configuration

### Changing Host/IP Address
To deploy on a different host (e.g., 192.168.1.100):

1. **Update `.env`**:
```bash
VITE_API_BASE_URL=http://192.168.1.100:8000
CORS_ORIGINS=http://192.168.1.100:5173
```

2. **Update `web/.env`**:
```bash
VITE_API_BASE_URL=http://192.168.1.100:8000
```

3. **Rebuild and restart**:
```bash
docker compose down
docker compose up -d --build
```

### Production Configuration
For production deployment:

1. **Security**:
```bash
# In .env
JWT_SECRET=your-super-secure-random-string-here
MINIO_ROOT_PASSWORD=secure-minio-password
POSTGRES_PASSWORD=secure-postgres-password
```

2. **Performance**:
```bash
# Scale services
docker compose up -d --scale worker=3
```

## Features Overview

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- 4 roles: admin, publisher, handler, viewer

### Ticket Management
- Dynamic form generation based on ticket types
- Complaint ticket type with 5G network testing fields
- Status tracking (draft → submitted → in_progress → completed)
- File attachment support (up to 8 images per ticket)

### OCR Integration
- PaddleOCR for Chinese and English text extraction
- Automatic field mapping for common 5G terms
- Confidence scoring and bounding box detection
- Manual field selection and mapping

### File Management
- MinIO S3-compatible object storage
- Pre-signed URLs for secure upload/download
- Image preview and management
- Support for common image formats

## API Documentation

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Tickets
- `GET /api/v1/tickets` - List tickets (with filtering)
- `POST /api/v1/tickets` - Create new ticket
- `GET /api/v1/tickets/{id}` - Get ticket details
- `PUT /api/v1/tickets/{id}` - Update ticket
- `DELETE /api/v1/tickets/{id}` - Delete ticket

### Files & Images
- `POST /api/v1/files/upload-url` - Get pre-signed upload URL
- `GET /api/v1/files/tickets/{id}/images` - List ticket images
- `POST /api/v1/files/tickets/{id}/images` - Add image to ticket
- `DELETE /api/v1/files/images/{id}` - Delete image

### OCR
- `POST /api/v1/ocr/images/{id}/process` - Trigger OCR processing
- `GET /api/v1/ocr/images/{id}/results` - Get OCR results
- `POST /api/v1/ocr/tickets/{id}/apply-ocr` - Apply OCR to fields

Full API documentation: http://localhost:8000/docs

## User Roles & Permissions

| Action | Viewer | Handler | Publisher | Admin |
|--------|--------|---------|-----------|-------|
| View tickets | ✅ | ✅ | ✅ | ✅ |
| Update tickets | ❌ | ✅ | ✅ | ✅ |
| Create tickets | ❌ | ❌ | ✅ | ✅ |
| Delete tickets | ❌ | ❌ | ✅ | ✅ |
| User management | ❌ | ❌ | ❌ | ✅ |
| Import/Export | ❌ | ❌ | ✅ | ✅ |

## Troubleshooting

### Common Issues

1. **Services won't start**
```bash
# Check service status
docker compose ps

# View service logs
docker compose logs backend
docker compose logs postgres
```

2. **Database connection errors**
```bash
# Restart database services
docker compose restart postgres redis

# Check if database is initialized
docker compose exec postgres psql -U postgres -d 5g_ticketing -c "\dt"
```

3. **OCR not working**
```bash
# Check OCR service
docker compose logs ocr
curl http://localhost:8001/health

# Test OCR directly
curl -X POST http://localhost:8001/ocr-upload -F "file=@test-image.jpg"
```

4. **File upload issues**
```bash
# Check MinIO service
docker compose logs minio
curl http://localhost:9000/minio/health/live

# Access MinIO console
# http://localhost:9001 (minioadmin/minioadmin123)
```

### Performance Tuning

1. **Database optimization**
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('5g_ticketing'));

-- Monitor connections
SELECT count(*) FROM pg_stat_activity;
```

2. **Scale workers**
```bash
# Increase Celery workers for OCR processing
docker compose up -d --scale worker=3
```

3. **Memory monitoring**
```bash
# Check container memory usage
docker stats
```

## Development

### Local Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd web
npm install
npm run dev

# OCR Service
cd ocr-service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

### Database Migrations
```bash
# Generate new migration
docker compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker compose exec backend alembic upgrade head
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd web
npm test
```

## Security Considerations

### Production Checklist
- [ ] Change default JWT secret
- [ ] Use strong passwords for all services
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Backup strategy
- [ ] Monitor logs for suspicious activity

### Backup Strategy
```bash
# Database backup
docker compose exec postgres pg_dump -U postgres 5g_ticketing > backup.sql

# MinIO backup
docker run --rm -v minio_data:/data alpine tar czf /backup.tar.gz /data
```

## Monitoring & Logging

### Log Locations
- Backend logs: `docker compose logs backend`
- OCR logs: `docker compose logs ocr`
- Web app logs: Browser developer console
- Database logs: `docker compose logs postgres`

### Health Checks
- Backend: http://localhost:8000/health
- OCR Service: http://localhost:8001/health
- MinIO: http://localhost:9000/minio/health/live

## Support

For technical support or feature requests:
1. Check the troubleshooting guide above
2. Review the API documentation at http://localhost:8000/docs
3. Check service logs using `docker compose logs [service-name]`
4. Verify environment configuration in `.env` files