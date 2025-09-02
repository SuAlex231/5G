# 5G Ticketing System Architecture

## System Overview

The 5G Ticketing System is designed as a microservices architecture with clear separation of concerns and robust integration points for future enhancements.

## Architecture Principles

### 1. Service-Oriented Design
- **Backend API:** Central FastAPI service handling business logic
- **OCR Service:** Dedicated PaddleOCR microservice for text recognition
- **Web Frontend:** React SPA with modern UI components
- **Data Layer:** PostgreSQL with JSONB for flexible schema
- **File Storage:** MinIO for scalable object storage
- **Task Queue:** Redis + Celery for async processing

### 2. Security by Design
- **JWT Authentication:** Stateless token-based auth
- **RBAC:** Role-based access control with granular permissions
- **API Security:** CORS, input validation, secure headers
- **File Security:** Pre-signed URLs, type validation, size limits

### 3. Scalability Patterns
- **Horizontal Scaling:** Stateless services behind load balancers
- **Async Processing:** Long-running tasks via Celery queues
- **Caching:** Redis for session and query caching
- **CDN Ready:** Static assets and file downloads

### 4. Extensibility Focus
- **Plugin Architecture:** Easy addition of new ticket types
- **SSO Ready:** Authentication abstraction layer
- **API First:** All functionality exposed via REST API
- **Mobile Ready:** API supports future Android app

## Service Architecture

### Backend Service (FastAPI)
```
├── API Layer (FastAPI + Pydantic)
├── Business Logic (Services)
├── Data Access (SQLModel + Alembic)
├── Authentication (JWT + RBAC)
├── File Management (MinIO integration)
├── Task Queue (Celery integration)
└── OCR Integration (HTTP client)
```

**Key Components:**
- **Dynamic Forms:** JSONB-based flexible ticket schemas
- **RBAC Engine:** Role-permission matrix with endpoint guards
- **Import/Export:** Excel processing with fuzzy header matching
- **Audit Trail:** Complete change tracking
- **File Pipeline:** Upload → Process → Store → Serve

### OCR Service (PaddleOCR)
```
├── OCR Engine (PaddleOCR Chinese/English)
├── Image Processing (OpenCV + PIL)
├── API Interface (FastAPI)
├── Result Formatting (Structured JSON)
└── Performance Optimization (Model caching)
```

**Capabilities:**
- **Chinese Text Recognition:** Optimized for 5G network terminology  
- **Bounding Box Detection:** Precise text location data
- **Confidence Scoring:** Quality assessment for auto-mapping
- **Batch Processing:** Multiple images per request

### Web Frontend (React)
```
├── UI Components (Ant Design)
├── State Management (React Query + Context)
├── Routing (React Router)
├── Authentication (Token management)
├── API Layer (Axios + interceptors)
└── File Handling (Upload + preview)
```

**Features:**
- **Dynamic Forms:** Runtime form generation from API schema
- **Image Management:** Drag-drop upload, preview, reordering
- **OCR Integration:** Real-time text extraction and mapping
- **Role-Based UI:** Conditional rendering based on permissions

## Data Architecture

### Database Design (PostgreSQL)
```sql
-- Core entities
users → role_assignments ← roles
ticket_types → form_fields
ticket_types → tickets ← users (created_by)

-- Dynamic content  
tickets.form_data (JSONB)  -- Flexible field storage
tickets.images → ocr_results

-- Audit and jobs
tickets → audit_logs
jobs (import/export tracking)
```

**Key Patterns:**
- **JSONB Fields:** Dynamic form data with indexing
- **Audit Trail:** Complete change history
- **Soft References:** Foreign keys with nullable relationships
- **Migration Ready:** Alembic for schema evolution

### File Storage (MinIO)
```
buckets/
├── uploads/         # User-uploaded images
│   └── images/
│       └── {ticket_id}/
│           ├── {uuid}.jpg
│           └── ...
└── exports/         # Generated files
    ├── excel/
    └── docx/
```

### Cache Layer (Redis)
- **Session Storage:** JWT refresh tokens
- **Task Queue:** Celery job queue and results
- **API Caching:** Frequently accessed data
- **Rate Limiting:** API request throttling

## Integration Patterns

### OCR Workflow
```
1. User uploads image → MinIO
2. API triggers OCR job → Celery
3. Worker calls OCR service → PaddleOCR
4. OCR results stored → Database
5. Frontend polls for completion
6. User maps text to fields
7. Data applied to ticket
```

### Import/Export Flow
```
Excel Import:
1. File upload → MinIO
2. Background processing → Celery
3. Header fuzzy matching → Config YAML
4. Row validation → Structured report
5. Ticket creation → Database
6. Progress updates → WebSocket/Polling

Excel Export:
1. Query tickets → Database
2. Apply template → Excel generation
3. Save to MinIO → Pre-signed URL
4. Download link → Frontend
```

## Security Architecture

### Authentication Flow
```
1. Login → JWT access + refresh tokens
2. API requests → Bearer token validation
3. Token expiry → Auto-refresh
4. Logout → Token invalidation
```

### Authorization Matrix
| Role | Tickets | Images | OCR | Import | Export | Users |
|------|---------|--------|-----|--------|--------|-------|
| Viewer | Read | Read | - | - | Read | - |
| Handler | Read/Update | Read | Trigger | - | Read | - |
| Publisher | Full | Full | Full | Full | Full | - |
| Admin | Full | Full | Full | Full | Full | Full |

### File Security
- **Upload Validation:** Type, size, virus scanning ready
- **Access Control:** Pre-signed URLs with expiration
- **Audit Trail:** All file operations logged

## Performance Considerations

### Backend Optimization
- **Connection Pooling:** Database and Redis
- **Query Optimization:** Indexes on common filters
- **Async Processing:** Non-blocking I/O operations
- **Pagination:** Large dataset handling

### Frontend Optimization  
- **Code Splitting:** Route-based lazy loading
- **Asset Optimization:** Compression and caching
- **API Efficiency:** Request batching and caching
- **Image Optimization:** Thumbnails and lazy loading

### OCR Performance
- **Model Caching:** In-memory model loading
- **Image Preprocessing:** Optimization before OCR
- **Batch Processing:** Multiple images per request
- **Resource Management:** Memory cleanup after processing

## Deployment Architecture

### Container Strategy
```
├── Frontend (nginx + React build)
├── Backend (uvicorn + FastAPI)  
├── OCR Service (uvicorn + PaddleOCR)
├── Worker (Celery worker)
├── Database (PostgreSQL)
├── Cache (Redis)
└── Storage (MinIO)
```

### Network Design
```
External → Load Balancer → Frontend
         → API Gateway → Backend Services
         → Database (internal only)
```

### Monitoring Ready
- **Health Checks:** All services expose /health
- **Logging:** Structured JSON logs
- **Metrics:** Performance counters
- **Alerts:** Critical failure notifications

## Future Extensions

### SSO Integration Points
```
├── Auth Service Interface (abstracted)
├── User Sync (external → internal users)  
├── Role Mapping (external → internal roles)
└── Session Management (federated tokens)
```

### Mobile API Extensions
```
├── Mobile-Optimized Endpoints
├── Offline Sync Capabilities
├── Push Notification Hooks
└── Location-Aware Features
```

### Advanced OCR Features
```
├── Custom Model Training
├── Field-Specific Recognition
├── Multi-Language Support  
└── AI-Powered Auto-Mapping
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Vite + Ant Design | Modern UI/UX |
| API | FastAPI + Pydantic | High-performance API |
| Database | PostgreSQL + SQLModel | Relational data with flexibility |
| Cache | Redis | Session and task management |
| Storage | MinIO | Scalable file storage |
| OCR | PaddleOCR | Chinese text recognition |
| Queue | Celery | Async task processing |
| Container | Docker + Compose | Service orchestration |

This architecture provides a solid foundation for the current MVP while maintaining flexibility for future enhancements and scalability requirements.