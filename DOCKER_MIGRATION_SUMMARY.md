# Docker Migration Summary

## Overview
Migrated the entire application to Docker and Docker Compose with the following configuration:
- **Backend**: FastAPI on port 7235
- **Frontend**: Next.js on port 3001
- **Database**: Hosted on Render (via DATABASE_URL env variable)

## Changes Made

### 1. Backend Configuration

#### Dockerfile
- Updated port from 8000 to 7235
- Removed database initialization (now external on Render)
- Kept CAMeL Tools NER model download (optional fallback)

#### app/main.py
- Updated scheduler initialization to use port 7235

#### app/services/scheduler.py
- Updated default API base URL from `http://localhost:8000` to `http://localhost:7235`
- Updated all scheduler manager instances

#### app/core/config.py
- Updated default CORS_ORIGINS to `["http://localhost:3001"]`
- Reads CORS_ORIGINS from environment variable

### 2. Frontend Configuration

#### frontend/Dockerfile
- Updated exposed port from 3000 to 3001
- Uses FRONTEND_PORT environment variable from docker-compose
- Accepts NEXT_PUBLIC_API_URL as build argument

#### frontend/lib/api-client.ts
- Updated default API URL from `http://localhost:8000` to `http://localhost:7235`
- Uses NEXT_PUBLIC_API_URL environment variable

### 3. Docker Compose

#### docker-compose.yml
- Removed PostgreSQL service (database on Render)
- Backend service:
  - Maps BACKEND_PORT:7235
  - Uses DATABASE_URL from .env
  - Sets CORS_ORIGINS from .env
- Frontend service:
  - Maps FRONTEND_PORT:3001
  - Sets NEXT_PUBLIC_API_URL to `http://backend:7235` (internal network)
  - Passes NEXT_PUBLIC_API_URL as build argument

### 4. Environment Configuration

#### .env
Added new variables:
```
BACKEND_PORT=7235
FRONTEND_PORT=3001
CORS_ORIGINS=http://localhost:3001,http://frontend:3001
```

#### .env.example
Updated with all required variables and documentation

### 5. Documentation

Created new documentation files:
- **DOCKER_SETUP.md**: Comprehensive Docker setup guide
- **DOCKER_QUICKSTART.md**: Quick start guide for running services
- **DOCKER_MIGRATION_SUMMARY.md**: This file

## Running the Application

### Quick Start
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# 2. Start services
docker-compose up -d

# 3. Access application
# Frontend: http://localhost:3001
# Backend: http://localhost:7235
# API Docs: http://localhost:7235/docs
```

### Port Configuration
- Backend internal port: 7235 (fixed)
- Frontend internal port: 3001 (fixed)
- External ports configurable via BACKEND_PORT and FRONTEND_PORT in .env

## Network Architecture

```
┌─────────────────────────────────────────────────────┐
│         Docker Compose Network                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │  Frontend    │         │   Backend    │        │
│  │  :3001       │────────→│   :7235      │        │
│  │  (Next.js)   │         │  (FastAPI)   │        │
│  └──────────────┘         └──────────────┘        │
│                                  │                 │
│                                  ↓                 │
│                          ┌──────────────┐         │
│                          │  Render DB   │         │
│                          │  (External)  │         │
│                          └──────────────┘         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string (from Render)
- `OPENAI_API_KEY`: OpenAI API key

### Optional
- `BACKEND_PORT`: External backend port (default: 7235)
- `FRONTEND_PORT`: External frontend port (default: 3001)
- `OPENAI_MODEL`: OpenAI model (default: gpt-4o)
- `NEWS_VIEW_NAME`: Database view name (default: vw_news_ar_feed)
- `CORS_ORIGINS`: Comma-separated CORS origins

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Database connection fails
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Ensure firewall allows connection

### Frontend can't reach backend
- Check backend is running: `docker-compose ps`
- Verify NEXT_PUBLIC_API_URL is set correctly
- Check backend logs: `docker-compose logs backend`

### Port conflicts
- Change BACKEND_PORT and FRONTEND_PORT in .env
- Restart services: `docker-compose down && docker-compose up -d`

## Next Steps

1. Update CI/CD pipelines to use Docker
2. Configure production environment variables
3. Set up Docker registry for image storage
4. Configure health checks and monitoring
5. Set up log aggregation
