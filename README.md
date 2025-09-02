# 5G Ticketing System

A production-ready MVP 5G ticketing system with Web (React) + Backend (FastAPI) + OCR microservice (PaddleOCR) architecture.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 5G
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   cp web/.env.example web/.env
   ```

3. **Start all services**
   ```bash
   docker compose up -d
   ```

4. **Wait for services to be ready** (usually 1-2 minutes)
   ```bash
   docker compose logs -f backend
   # Wait until you see "Application startup complete"
   ```

### 🔑 Default Credentials

- **Admin User**: 
  - Email: `admin@5g-ticketing.com`
  - Password: `admin123`

### 🌐 Service URLs

- **Web Application**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin123)

### 📊 Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Web App | 5173 | React frontend |
| Backend API | 8000 | FastAPI backend |
| OCR Service | 8001 | PaddleOCR microservice |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & message broker |
| MinIO API | 9000 | Object storage API |
| MinIO Console | 9001 | Object storage web UI |

## 🔧 Configuration

### Changing Host/IP from Localhost

To deploy on a different host or IP address:

1. **Update `.env` file**:
   ```bash
   # Change these values in .env
   VITE_API_BASE_URL=http://YOUR_HOST_IP:8000
   CORS_ORIGINS=http://YOUR_HOST_IP:5173
   # If MinIO needs to be accessible externally:
   MINIO_ENDPOINT=YOUR_HOST_IP:9000
   ```

2. **Update `web/.env` file**:
   ```bash
   VITE_API_BASE_URL=http://YOUR_HOST_IP:8000
   ```

3. **Rebuild and restart**:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

## 🎯 Features

### Core Functionality
- **Role-based Access Control (RBAC)**: 4 roles - admin, publisher, handler, viewer
- **Ticket Management**: Create, edit, assign tickets with dynamic forms
- **Image Upload**: Up to 8 images per ticket with ordering and management
- **OCR Integration**: Extract text from images using PaddleOCR
- **Excel Import/Export**: Fuzzy header matching for flexible Excel processing
- **Document Export**: Generate DOCX files with ticket images

### User Roles & Permissions

| Role | Create | Read | Update | Import/Export | Admin Actions |
|------|--------|------|--------|---------------|---------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Publisher** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Handler** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Viewer** | ❌ | ✅ | ❌ | ❌ | ❌ |

## 🏗️ Architecture

The system consists of 6 main services:

1. **Web App** (React + Vite + Ant Design): User interface
2. **Backend API** (FastAPI): Core business logic and API
3. **Worker** (Celery): Async task processing
4. **OCR Service** (FastAPI + PaddleOCR): Text extraction from images
5. **PostgreSQL**: Primary database
6. **Redis**: Cache and message broker
7. **MinIO**: Object storage for files and images

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token

### Users & Roles
- `GET /users` - List users (admin only)
- `POST /users` - Create user (admin only)
- `GET /roles` - List roles

### Tickets
- `GET /tickets` - List tickets (with filtering)
- `POST /tickets` - Create new ticket
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket
- `DELETE /tickets/{id}` - Delete ticket

### Images & OCR
- `POST /tickets/{id}/images` - Upload image
- `GET /tickets/{id}/images` - List ticket images
- `DELETE /images/{id}` - Delete image
- `POST /images/{id}/ocr` - Trigger OCR processing
- `GET /images/{id}/ocr-result` - Get OCR results
- `POST /tickets/{id}/apply-ocr` - Apply OCR results to fields

### Import/Export
- `POST /ticket-types/{id}/import` - Import Excel file
- `GET /ticket-types/{id}/export` - Export to Excel
- `GET /tickets/{id}/export-docx` - Export ticket to DOCX

## 🔍 Troubleshooting

### Services won't start
```bash
# Check service status
docker compose ps

# View logs
docker compose logs backend
docker compose logs ocr
docker compose logs web

# Restart specific service
docker compose restart backend
```

### Database connection issues
```bash
# Reset database
docker compose down -v
docker compose up -d
```

### Port conflicts
If ports are already in use, modify the ports in `.env`:
```bash
BACKEND_PORT=8001
WEB_PORT=3000
# etc.
```

## 🧪 Development

### Running individual services for development

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend only  
cd web
npm install
npm run dev

# OCR service only
cd ocr-service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

### Database migrations
```bash
# Generate migration
docker compose exec backend alembic revision --autogenerate -m "Description"

# Apply migration
docker compose exec backend alembic upgrade head
```

## 📄 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Fast Track Implementation Plan](docs/FAST_TRACK_PLAN.md)

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Ant Design, TypeScript
- **Backend**: FastAPI, SQLAlchemy, Pydantic, Alembic
- **OCR**: PaddleOCR (CPU-only)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **Task Queue**: Celery
- **Containerization**: Docker & Docker Compose

## 📋 Default Ticket Type

The system comes with a pre-configured "Complaint" ticket type that includes:

- Basic fields: 工单号, 区县, 问题描述, etc.
- Test results matrix: PCI, 频率, 小区ID, RSRP, SINR, 上传速率, 下载速率
- Support for multiple test result rows
- OCR integration for automatic field filling

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS protection
- File upload validation
- Pre-signed URLs for secure file access