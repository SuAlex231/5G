# 5G Ticketing System Architecture

## System Overview

The 5G Ticketing System is a microservices-based application designed for managing telecommunications service tickets with OCR capabilities. The system follows a distributed architecture pattern with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App    │    │   Admin Panel   │
│   (React/Vite)  │    │   (Future)      │    │   (React/Vite)  │
└─────────┬───────┘    └─────────────────┘    └─────────┬───────┘
          │                                              │
          └──────────────────┬───────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   Load Balancer   │
                   │    (Future)       │
                   └─────────┬─────────┘
                             │
                   ┌─────────▼─────────┐
                   │   Backend API     │
                   │   (FastAPI)       │
                   └─────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌─────────▼─────────┐
│   PostgreSQL      │ │   Redis     │ │     MinIO         │
│   (Primary DB)    │ │ (Cache/MQ)  │ │ (Object Storage)  │
└───────────────────┘ └─────────────┘ └───────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   Celery Worker   │
                   │ (Async Processing)│
                   └─────────┬─────────┘
                             │
                   ┌─────────▼─────────┐
                   │   OCR Service     │
                   │  (PaddleOCR)      │
                   └───────────────────┘
```

## Service Components

### 1. Web Application (Port 5173)
- **Technology**: React 18 + Vite + Ant Design + TypeScript
- **Purpose**: Primary user interface for ticket management
- **Features**:
  - Responsive design with mobile support
  - Role-based UI components
  - Real-time updates via WebSocket (future)
  - Offline capabilities (future)

### 2. Backend API (Port 8000)
- **Technology**: FastAPI + SQLAlchemy + Pydantic
- **Purpose**: Core business logic and API gateway
- **Features**:
  - RESTful API with OpenAPI documentation
  - JWT-based authentication
  - Role-based access control (RBAC)
  - Real-time WebSocket support (future)
  - API versioning support

### 3. OCR Service (Port 8001)
- **Technology**: FastAPI + PaddleOCR
- **Purpose**: Optical Character Recognition for image processing
- **Features**:
  - CPU-based OCR processing
  - Support for Chinese and English text
  - Confidence scoring
  - Bounding box detection

### 4. Celery Worker
- **Technology**: Celery + Redis
- **Purpose**: Asynchronous task processing
- **Features**:
  - OCR job processing
  - File export generation
  - Email notifications (future)
  - Scheduled tasks

### 5. PostgreSQL Database (Port 5432)
- **Purpose**: Primary data storage
- **Features**:
  - JSONB support for flexible schemas
  - Full-text search capabilities
  - Row-level security (future)
  - Backup and replication (future)

### 6. Redis Cache (Port 6379)
- **Purpose**: Caching and message broker
- **Features**:
  - Session storage
  - Celery message broker
  - API response caching
  - Real-time data caching

### 7. MinIO Object Storage (Ports 9000/9001)
- **Purpose**: File and image storage
- **Features**:
  - S3-compatible API
  - Pre-signed URL support
  - Bucket policies
  - Web console interface

## Data Flow

### 1. Ticket Creation Flow
```
User → Web App → Backend API → PostgreSQL
                     ↓
                 MinIO (images/attachments)
```

### 2. OCR Processing Flow
```
User uploads image → MinIO → Backend triggers OCR task → Celery Worker → OCR Service
                                      ↓
OCR results → Redis → Backend API → PostgreSQL → Web App (real-time update)
```

### 3. Import/Export Flow
```
Excel file → MinIO → Backend API → Celery Worker (processing) → PostgreSQL (data)
                                        ↓
Generated files → MinIO → Pre-signed URL → User download
```

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication with refresh token rotation
- **RBAC**: Four-tier role system (admin, publisher, handler, viewer)
- **CORS**: Configured for cross-origin requests
- **Rate Limiting**: API endpoint protection (future)

### Data Security
- **Encryption**: All sensitive data encrypted at rest and in transit
- **File Validation**: Strict file type and size validation
- **SQL Injection**: Protected by SQLAlchemy ORM
- **XSS Protection**: React built-in protection + CSP headers

## Scalability Considerations

### Horizontal Scaling
- **Backend API**: Stateless design allows multiple instances
- **Celery Workers**: Can scale based on queue depth
- **Database**: Read replicas for query distribution
- **Object Storage**: MinIO clustering support

### Performance Optimization
- **Database Indexing**: Optimized queries with proper indexes
- **Caching Strategy**: Multi-layer caching (Redis + application)
- **CDN**: Static asset delivery (future)
- **Connection Pooling**: Database connection optimization

## Data Model

### Core Entities

#### Users & Authorization
```sql
users (id, email, password_hash, full_name, created_at, updated_at)
roles (id, name, description)
role_assignments (user_id, role_id)
```

#### Ticket System
```sql
ticket_types (id, name, description, schema_config)
form_fields (id, ticket_type_id, field_name, field_type, config)
tickets (id, ticket_type_id, user_id, status, data[JSONB], created_at)
```

#### File Management
```sql
images (id, ticket_id, filename, minio_key, order_index, metadata)
attachments (id, ticket_id, filename, minio_key, file_type)
ocr_results (id, image_id, text_data[JSONB], confidence, bbox_data)
```

#### Audit & Jobs
```sql
audit_logs (id, user_id, action, resource_type, resource_id, timestamp)
jobs (id, job_type, status, parameters[JSONB], result[JSONB])
```

## Configuration Management

### Environment-Based Configuration
- **Development**: Local Docker Compose setup
- **Staging**: Similar to production with test data
- **Production**: Kubernetes deployment with secrets

### Configuration Sources
1. **Environment Variables**: Runtime configuration
2. **Config Files**: Static application settings
3. **Database**: Dynamic feature flags and business rules

## Monitoring & Observability

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Centralized Logging**: ELK stack integration (future)

### Metrics & Monitoring
- **Application Metrics**: Response times, error rates
- **Business Metrics**: Ticket processing times, OCR accuracy
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Health Checks**: Service availability monitoring

### Error Handling
- **Global Exception Handling**: Consistent error responses
- **Circuit Breaker Pattern**: Service resilience
- **Retry Logic**: Automatic recovery for transient failures

## Deployment Architecture

### Container Strategy
- **Multi-stage Builds**: Optimized Docker images
- **Health Checks**: Container lifecycle management
- **Resource Limits**: CPU and memory constraints
- **Security Scanning**: Vulnerability assessment

### Orchestration
- **Development**: Docker Compose
- **Production**: Kubernetes (future)
- **Service Mesh**: Istio integration (future)
- **GitOps**: ArgoCD deployment (future)

## Future Enhancements

### Planned Features
1. **Real-time Updates**: WebSocket integration
2. **Mobile App**: React Native implementation
3. **Advanced Analytics**: Business intelligence dashboard
4. **AI Integration**: Automated ticket categorization
5. **Multi-tenancy**: Organization isolation
6. **Workflow Engine**: Custom approval processes

### Technical Improvements
1. **Microservices Split**: Further service decomposition
2. **Event Sourcing**: Audit trail improvements
3. **CQRS Pattern**: Read/write model separation
4. **GraphQL API**: Alternative to REST
5. **Serverless Functions**: Event-driven processing