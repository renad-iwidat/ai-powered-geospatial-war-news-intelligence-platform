# Render Deployment Guide

## 📊 Server Size Analysis

### Dependencies Size:
- torch (camel-tools): 915 MB
- prophet: 200 MB
- pandas: 100 MB
- scikit-learn: 150 MB
- transformers: 500 MB
- Other: 200 MB
- **Total: ~2.5-3.5 GB**

### Recommended Server:
**Pro Plan (4 GB RAM, 2 CPU, 20 GB Storage) - $19/month**

---

## 💰 Total Cost Estimate:

```
Backend Service:    $19/month (Pro)
Scheduler Service:  $19/month (Pro)
Database:           $15/month (PostgreSQL)
Frontend:           $7/month (Vercel Free or Render Standard)
────────────────────────────────
Total:              ~$60/month
```

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create Backend Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: geonews-backend
   - **Environment**: Docker
   - **Plan**: Pro ($19/month)
   - **Region**: Oregon (or closest to you)
   - **Build Command**: `docker build -f Dockerfile -t backend .`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 7235`

5. Add Environment Variables:
   ```
   DATABASE_URL=postgresql://...
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o
   NEWS_VIEW_NAME=vw_news_ar_feed
   CORS_ORIGINS_STR=http://localhost:3001,https://your-frontend.vercel.app
   ```

6. Click "Create Web Service"

### Step 3: Create Scheduler Service

1. Click "New +" → "Background Worker"
2. Connect your GitHub repository
3. Configure:
   - **Name**: geonews-scheduler
   - **Environment**: Docker
   - **Plan**: Pro ($19/month)
   - **Region**: Oregon
   - **Build Command**: `docker build -f Dockerfile.scheduler -t scheduler .`
   - **Start Command**: `python scripts/run_scheduler.py`

4. Add Environment Variables:
   ```
   DATABASE_URL=postgresql://...
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o
   NEWS_VIEW_NAME=vw_news_ar_feed
   API_BASE_URL=https://geonews-backend.onrender.com
   ```

5. Click "Create Background Worker"

### Step 4: Deploy Frontend

#### Option A: Vercel (Recommended)
1. Go to https://vercel.com
2. Import your GitHub repository
3. Configure:
   - **Framework**: Next.js
   - **Root Directory**: ./frontend
   - **Build Command**: `npm run build`
   - **Start Command**: `npm run start`

4. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://geonews-backend.onrender.com
   ```

5. Click "Deploy"

#### Option B: Render
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: geonews-frontend
   - **Environment**: Node
   - **Plan**: Standard ($7/month)
   - **Build Command**: `cd frontend && npm run build`
   - **Start Command**: `cd frontend && npm run start`

4. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://geonews-backend.onrender.com
   ```

5. Click "Create Web Service"

---

## ⏱️ Build Times

- **First Build**: 15-20 minutes (downloading dependencies)
- **Subsequent Builds**: 5-10 minutes (cached layers)
- **Cold Start**: 30-60 seconds (loading models)
- **Warm Start**: <1 second

---

## 🔍 Monitoring

### View Logs
```bash
# Backend logs
# Go to Backend Service → Logs

# Scheduler logs
# Go to Scheduler Service → Logs
```

### Health Check
```bash
# Test backend health
curl https://geonews-backend.onrender.com/health

# Expected response:
# {"status": "healthy", "database": "connected", "version": "1.0.0"}
```

### Scheduler Status
```bash
# View scheduler logs for job execution
# Look for messages like:
# 🔄 Starting data processing at 2024-03-07T10:30:00
# ✅ Data processing completed
```

---

## 🛠️ Troubleshooting

### Build Fails
- Check Docker build logs
- Verify all dependencies are in requirements.txt
- Check Dockerfile syntax

### Service Won't Start
- Check environment variables are set
- Check logs for errors
- Verify DATABASE_URL is correct

### Scheduler Not Running
- Check scheduler service is deployed
- Check API_BASE_URL is correct
- Check backend service is running

### Database Connection Fails
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Ensure firewall allows connection

---

## 📈 Scaling

### If Backend is Slow:
1. Upgrade to Pro Plus (8 GB RAM, 4 CPU) - $29/month
2. Enable auto-scaling
3. Add caching layer (Redis)

### If Scheduler is Slow:
1. Upgrade to Pro Plus (8 GB RAM, 4 CPU) - $29/month
2. Reduce job frequency
3. Split jobs into multiple workers

---

## 🔐 Security

### Environment Variables
- ✅ DATABASE_URL: Secure (not in code)
- ✅ OPENAI_API_KEY: Secure (not in code)
- ✅ CORS_ORIGINS_STR: Configured

### HTTPS
- ✅ Render provides free HTTPS
- ✅ All traffic encrypted

### Database
- ✅ Render PostgreSQL with SSL
- ✅ Automatic backups

---

## 📝 Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: geonews-backend
    env: docker
    plan: pro
    # ... configuration
  
  - type: background_worker
    name: geonews-scheduler
    env: docker
    plan: pro
    # ... configuration
```

---

## ✅ Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Backend service deployed (Pro Plan)
- [ ] Scheduler service deployed (Pro Plan)
- [ ] Frontend deployed (Vercel or Render)
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] Logs showing normal operation
- [ ] Scheduler jobs executing on schedule

---

## 🎉 You're Live!

```
Backend:   https://geonews-backend.onrender.com
Scheduler: Running in background
Frontend:  https://your-frontend.vercel.app
Database:  Render PostgreSQL
```

---

## 📞 Support

### Render Support
- https://render.com/docs
- https://render.com/support

### Common Issues
- Build timeout: Increase build timeout in settings
- Memory issues: Upgrade to Pro Plus
- Cold starts: Use Render's auto-scaling

---

## 💡 Tips

1. **Monitor Costs**: Check Render dashboard regularly
2. **Set Alerts**: Enable email notifications for errors
3. **Backup Database**: Enable automatic backups
4. **Update Dependencies**: Keep requirements.txt updated
5. **Test Locally**: Always test with Docker locally first

---

## 🚀 Next Steps

1. Deploy backend service
2. Deploy scheduler service
3. Deploy frontend
4. Test all endpoints
5. Monitor logs and performance
6. Optimize if needed

Ready to deploy! 🎉
