# 5G Ticketing System

Internal-only 5G network complaint ticketing system with OCR and Excel import/export capabilities.

## 🚀 Quickstart

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available for Docker

### Get Started

1. **Clone and configure:**
   ```bash
   cp .env.example .env
   cp web/.env.example web/.env
   # Edit .env files if needed (defaults work for localhost)
   ```

2. **Start all services:**
   ```bash
   docker compose up -d
   ```

3. **Wait for services to be ready** (1-2 minutes for first run)

4. **Access the application:**
   - **Web Interface:** http://localhost:5173
   - **API Documentation:** http://localhost:8000/docs
   - **MinIO Console:** http://localhost:9001 (admin/admin123)

## 🔐 Default Admin Credentials

- **Email:** admin@example.com
- **Password:** Admin123!

## 📋 Services

| Service | Port | Description |
|---------|------|-------------|
| Web (React) | 5173 | Frontend application |
| Backend (FastAPI) | 8000 | REST API server |
| OCR Service | 8001 | PaddleOCR text recognition |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache and job queue |
| MinIO | 9000/9001 | Object storage |

## 🔧 Configuration

### Single-Point Host/IP Change

To run on a different host or make services accessible externally:

1. **Update `.env`:** Change hostnames in DATABASE_URL, REDIS_URL, MINIO_ENDPOINT, OCR_SERVICE_URL
2. **Update `web/.env`:** Change VITE_API_BASE_URL to your server IP
3. **Rebuild web:** `docker compose build web && docker compose up -d`

Example for server at 192.168.1.100:
```env
# In .env
DATABASE_URL=postgresql://postgres:postgres@192.168.1.100:5432/ticketing_db
REDIS_URL=redis://192.168.1.100:6379/0
MINIO_ENDPOINT=http://192.168.1.100:9000
OCR_SERVICE_URL=http://192.168.1.100:8001

# In web/.env
VITE_API_BASE_URL=http://192.168.1.100:8000
```

## 🎯 Key Features

### Ticketing System
- **RBAC:** Admin, Publisher, Handler, Viewer roles
- **Dynamic Forms:** Configurable ticket types with custom fields
- **Complaint Type:** Pre-configured with Chinese 5G network fields
- **File Management:** Image uploads with MinIO storage

### OCR Integration
- **PaddleOCR:** Chinese text recognition
- **Auto-mapping:** Keyword-based field population
- **Interactive Selection:** Manual text-to-field mapping

### Import/Export
- **Fuzzy Matching:** Excel headers matched to fields automatically  
- **Validation Reports:** Row-by-row import results
- **Matrix Support:** Test results array fields
- **DOCX Export:** Ticket images in document format

### Complaint Ticket Fields
- Basic: Complaint number, district, complainant name, phone, address
- Type: Complaint type and content
- Test Results Matrix: PCI, frequency, cell ID, RSRP, SINR, speeds, interference

## 🛠 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development  
```bash
cd web
npm install
npm run dev
```

### Database Setup
```bash
# Initialize database with default data
cd backend
python -m app.init_db
```

## 🔍 Troubleshooting

### Common Issues

**Services not starting:**
- Check Docker has enough memory (4GB+)
- Verify ports 5173, 8000, 8001, 5432, 6379, 9000, 9001 are available
- Check logs: `docker compose logs [service-name]`

**Web app can't reach backend:**
- Verify VITE_API_BASE_URL in web/.env
- Check backend health: `curl http://localhost:8000/health`

**Database connection errors:**
- Wait for PostgreSQL to be ready (check with `docker compose logs postgres`)
- Verify DATABASE_URL in .env

**MinIO permissions errors:**
- Check MinIO console at http://localhost:9001
- Verify MINIO_ACCESS_KEY and MINIO_SECRET_KEY in .env

**OCR not working:**
- OCR service takes time to load PaddleOCR models on first run
- Check OCR service health: `curl http://localhost:8001/health`

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f web
docker compose logs -f ocr
```

### Reset Data
```bash
# Stop services and remove data
docker compose down -v

# Restart fresh
docker compose up -d
```

## 📁 Project Structure

```
├── backend/           # FastAPI backend service
├── ocr-service/       # PaddleOCR microservice  
├── web/              # React frontend
├── docs/             # Architecture documentation
├── .env.example      # Backend configuration template
├── docker-compose.yml # Service orchestration
└── README.md         # This file
```

## 🔗 API Endpoints

Key endpoints available at http://localhost:8000/docs:

- **Auth:** `/api/v1/auth/login`, `/api/v1/auth/refresh`
- **Users:** `/api/v1/users/` (CRUD with RBAC)
- **Tickets:** `/api/v1/tickets/` (CRUD with dynamic forms)
- **Images:** `/api/v1/tickets/{id}/images` (upload/manage)
- **OCR:** `/api/v1/tickets/{id}/images/{image_id}/ocr`
- **Import/Export:** `/api/v1/ticket-types/{id}/import|export`

## 🚧 Future Enhancements

- SSO integration (auth system is isolated for easy migration)
- Android mobile app (architecture ready)
- Advanced OCR field mapping
- Real-time notifications
- Advanced reporting and analytics

## 📄 License

Internal use only.