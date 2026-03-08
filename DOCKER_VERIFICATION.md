# Docker Configuration Verification Checklist

## Environment Variables ✓

- [x] DATABASE_URL configured in .env (from Render)
- [x] OPENAI_API_KEY configured in .env
- [x] BACKEND_PORT set to 7235
- [x] FRONTEND_PORT set to 3001
- [x] CORS_ORIGINS configured

## Backend Configuration ✓

- [x] Dockerfile exposes port 7235
- [x] app/main.py uses port 7235 for scheduler
- [x] app/services/scheduler.py uses http://localhost:7235
- [x] app/core/config.py has correct CORS defaults
- [x] Health check endpoint configured

## Frontend Configuration ✓

- [x] frontend/Dockerfile exposes port 3001
- [x] frontend/lib/api-client.ts uses port 7235
- [x] NEXT_PUBLIC_API_URL environment variable supported
- [x] next.config.ts has standalone output

## Docker Compose ✓

- [x] Backend service configured correctly
- [x] Frontend service configured correctly
- [x] Database removed (external on Render)
- [x] Network configuration correct
- [x] Port mappings correct
- [x] Environment variables passed correctly
- [x] Health checks configured

## Documentation ✓

- [x] DOCKER_SETUP.md created
- [x] DOCKER_QUICKSTART.md created
- [x] DOCKER_MIGRATION_SUMMARY.md created
- [x] .env.example updated
- [x] This verification file created

## Pre-Launch Checklist

Before running `docker-compose up -d`:

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with:
   # - DATABASE_URL (from Render)
   # - OPENAI_API_KEY
   ```

2. **Verify Configuration**
   ```bash
   # Check .env file
   cat .env
   
   # Verify ports are available
   # Port 7235 (backend)
   # Port 3001 (frontend)
   ```

3. **Build Images**
   ```bash
   docker-compose build
   ```

4. **Start Services**
   ```bash
   docker-compose up -d
   ```

5. **Verify Services**
   ```bash
   # Check running containers
   docker-compose ps
   
   # Check backend health
   curl http://localhost:7235/health
   
   # Check frontend
   curl http://localhost:3001
   ```

## Testing Endpoints

### Backend API
- Health: `http://localhost:7235/health`
- API Docs: `http://localhost:7235/docs`
- ReDoc: `http://localhost:7235/redoc`

### Frontend
- Main: `http://localhost:3001`
- API calls should go to: `http://localhost:7235/api/v1`

## Troubleshooting Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Check network
docker network ls
docker network inspect geonews-network
```

## Port Verification

```bash
# Check if ports are in use
# On Linux/Mac
lsof -i :7235
lsof -i :3001

# On Windows
netstat -ano | findstr :7235
netstat -ano | findstr :3001
```

## Database Connection Test

```bash
# Test database connection from backend
docker-compose exec backend python -c "
import asyncpg
import asyncio
from app.core.config import settings

async def test():
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        result = await conn.fetchval('SELECT 1')
        print(f'✓ Database connected: {result}')
        await conn.close()
    except Exception as e:
        print(f'✗ Database error: {e}')

asyncio.run(test())
"
```

## API Communication Test

```bash
# Test frontend can reach backend
docker-compose exec frontend curl http://backend:7235/health

# Test backend health
curl http://localhost:7235/health
```

## Performance Monitoring

```bash
# Monitor container resource usage
docker stats

# View container logs with timestamps
docker-compose logs --timestamps -f

# Check container processes
docker-compose top backend
docker-compose top frontend
```

## Common Issues and Solutions

### Issue: "Port already in use"
**Solution**: Change BACKEND_PORT or FRONTEND_PORT in .env

### Issue: "Database connection refused"
**Solution**: Verify DATABASE_URL is correct and Render database is accessible

### Issue: "Frontend can't reach backend"
**Solution**: Check NEXT_PUBLIC_API_URL is set to http://backend:7235

### Issue: "Services won't start"
**Solution**: Run `docker-compose build --no-cache` and try again

### Issue: "Health check failing"
**Solution**: Check backend logs with `docker-compose logs backend`

## Success Indicators

✓ All containers running: `docker-compose ps` shows all services as "Up"
✓ Backend health: `curl http://localhost:7235/health` returns 200
✓ Frontend accessible: `http://localhost:3001` loads
✓ API communication: Frontend can call backend endpoints
✓ Database connected: Backend can query Render database
✓ No errors in logs: `docker-compose logs` shows no critical errors
