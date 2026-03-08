# Docker Setup Guide

## Overview
This project uses Docker and Docker Compose to run the backend and frontend services. The database is hosted on Render and configured via environment variables.

## Architecture
- **Backend**: FastAPI running on port 7235 inside container
- **Frontend**: Next.js running on port 3001 inside container
- **Database**: PostgreSQL hosted on Render (via DATABASE_URL)

## Prerequisites
- Docker installed
- Docker Compose installed
- `.env` file configured with required variables

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database (from Render)
DATABASE_URL=postgresql://user:password@host:port/database

# API Keys
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o

# Port Configuration
BACKEND_PORT=7235
FRONTEND_PORT=3001

# CORS Origins
CORS_ORIGINS=http://localhost:3001,http://frontend:3001
```

## Running the Application

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

## Accessing the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:7235
- **API Docs**: http://localhost:7235/docs
- **API ReDoc**: http://localhost:7235/redoc

## Port Mapping

| Service | Internal Port | External Port | Env Variable |
|---------|---------------|---------------|--------------|
| Backend | 7235 | 7235 | BACKEND_PORT |
| Frontend | 3001 | 3001 | FRONTEND_PORT |

## Troubleshooting

### Backend Connection Issues
- Check DATABASE_URL is correct
- Verify Render database is accessible
- Check CORS_ORIGINS configuration

### Frontend API Connection Issues
- Verify NEXT_PUBLIC_API_URL is set correctly
- Check backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

### Port Already in Use
```bash
# Change ports in .env
BACKEND_PORT=7236
FRONTEND_PORT=3002

# Restart services
docker-compose down
docker-compose up -d
```

## Development

### Rebuild Images
```bash
docker-compose build --no-cache
```

### Run Specific Service
```bash
docker-compose up backend
docker-compose up frontend
```

### Access Container Shell
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Production Deployment

For production, ensure:
1. DATABASE_URL points to production database
2. OPENAI_API_KEY is set securely
3. CORS_ORIGINS includes production domain
4. Update BACKEND_PORT and FRONTEND_PORT as needed
