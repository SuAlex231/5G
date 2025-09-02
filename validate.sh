#!/bin/bash

# 5G Ticketing System - Quick Validation Script
# This script validates that all components are properly configured

echo "🚀 5G Ticketing System - Quick Validation"
echo "========================================="
echo ""

# Check if docker-compose exists
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check if .env files exist
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy from .env.example"
    exit 1
fi

if [ ! -f "web/.env" ]; then
    echo "❌ web/.env file not found. Please copy from web/.env.example"
    exit 1
fi

echo "✅ Environment files are configured"

# Validate docker-compose.yml
if ! docker compose config > /dev/null 2>&1; then
    echo "❌ Docker Compose configuration is invalid"
    exit 1
fi

echo "✅ Docker Compose configuration is valid"

# Check required directories
required_dirs=("backend" "web" "ocr-service" "docs")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Required directory missing: $dir"
        exit 1
    fi
done

echo "✅ All required directories present"

# Check key files
key_files=(
    "backend/main.py"
    "backend/requirements.txt" 
    "backend/Dockerfile"
    "backend/init_db.py"
    "web/package.json"
    "web/index.html"
    "web/src/main.tsx"
    "ocr-service/main.py"
    "ocr-service/requirements.txt"
)

for file in "${key_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ All key application files present"

# Check ports availability (optional)
ports=(5173 8000 8001 5432 6379 9000 9001)
unavailable_ports=()

for port in "${ports[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        unavailable_ports+=($port)
    fi
done

if [ ${#unavailable_ports[@]} -gt 0 ]; then
    echo "⚠️  Some ports may be in use: ${unavailable_ports[*]}"
    echo "   This is normal if services are already running"
else
    echo "✅ All required ports appear to be available"
fi

echo ""
echo "🎉 System validation complete!"
echo ""
echo "Quick Start Commands:"
echo "1. Start services:     docker compose up -d"
echo "2. Initialize DB:      docker compose exec backend python init_db.py" 
echo "3. View logs:          docker compose logs -f"
echo "4. Access web:         http://localhost:5173"
echo "5. Access API docs:    http://localhost:8000/docs"
echo "6. Access MinIO:       http://localhost:9001"
echo ""
echo "Default Admin Login:"
echo "Email: admin@5g-ticketing.com"
echo "Password: admin123"
echo ""
echo "For detailed deployment instructions, see DEPLOYMENT.md"