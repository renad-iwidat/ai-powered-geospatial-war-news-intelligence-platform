# Docker Quick Start

## 1. Setup Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL (from Render)
# - OPENAI_API_KEY
# - BACKEND_PORT (default: 7235)
# - FRONTEND_PORT (default: 3001)
```

## 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps
```

## 3. Access Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:7235
- **API Documentation**: http://localhost:7235/docs

## 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 5. Stop Services

```bash
docker-compose down
```

## Configuration

### Ports
- Backend: 7235 (inside container) → BACKEND_PORT (external)
- Frontend: 3001 (inside container) → FRONTEND_PORT (external)

### Database
- Hosted on Render
- Configured via DATABASE_URL in .env

### API Communication
- Frontend uses NEXT_PUBLIC_API_URL environment variable
- Default: http://localhost:BACKEND_PORT

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Port conflicts
```bash
# Change ports in .env
BACKEND_PORT=7236
FRONTEND_PORT=3002

# Restart
docker-compose down
docker-compose up -d
```

### Database connection issues
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Verify firewall allows connection

## Development

### Rebuild after code changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access container shell
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

### View real-time logs
```bash
docker-compose logs -f --tail=50
```
