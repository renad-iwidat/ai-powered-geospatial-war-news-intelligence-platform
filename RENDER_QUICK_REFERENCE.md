# Render Deployment - Quick Reference

## 📊 Server Size

**Pro Plan (Recommended)**
- RAM: 4 GB
- CPU: 2
- Storage: 20 GB
- Cost: $19/month

**Why Pro?**
- Dependencies: ~3.5 GB
- Enough RAM for API + Scheduler
- Good performance
- Reasonable cost

---

## 💰 Total Cost

```
Backend:    $19/month (Pro)
Scheduler:  $19/month (Pro)
Database:   $15/month (PostgreSQL)
Frontend:   $7/month (Vercel Free)
────────────────────────────
Total:      ~$60/month
```

---

## 🚀 Deployment Steps

### 1. Backend Service
```
Name: geonews-backend
Plan: Pro ($19/month)
Dockerfile: ./Dockerfile
Start: uvicorn app.main:app --host 0.0.0.0 --port 7235
```

### 2. Scheduler Service
```
Name: geonews-scheduler
Plan: Pro ($19/month)
Dockerfile: ./Dockerfile.scheduler
Start: python scripts/run_scheduler.py
```

### 3. Frontend
```
Framework: Next.js
Plan: Vercel Free (or Render Standard $7/month)
Build: npm run build
Start: npm run start
```

---

## 🔧 Environment Variables

### Backend
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
NEWS_VIEW_NAME=vw_news_ar_feed
CORS_ORIGINS_STR=http://localhost:3001,...
```

### Scheduler
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
NEWS_VIEW_NAME=vw_news_ar_feed
API_BASE_URL=https://geonews-backend.onrender.com
```

### Frontend
```
NEXT_PUBLIC_API_URL=https://geonews-backend.onrender.com
```

---

## ⏱️ Build Times

- First Build: 15-20 minutes
- Subsequent: 5-10 minutes
- Cold Start: 30-60 seconds
- Warm Start: <1 second

---

## 🧪 Testing

```bash
# Test backend health
curl https://geonews-backend.onrender.com/health

# View logs
# Go to Render Dashboard → Service → Logs

# Check scheduler
# Look for job execution messages in logs
```

---

## 📝 Files

- `render.yaml` - Render configuration
- `Dockerfile` - Backend image
- `Dockerfile.scheduler` - Scheduler image
- `RENDER_DEPLOYMENT_GUIDE.md` - Detailed guide

---

## ✅ Checklist

- [ ] Push to GitHub
- [ ] Create Backend Service (Pro)
- [ ] Create Scheduler Service (Pro)
- [ ] Deploy Frontend (Vercel)
- [ ] Configure Environment Variables
- [ ] Test Health Endpoints
- [ ] Monitor Logs
- [ ] Verify Scheduler Jobs

---

## 🎉 You're Live!

```
Backend:   https://geonews-backend.onrender.com
Scheduler: Running in background
Frontend:  https://your-frontend.vercel.app
```

---

## 💡 Tips

1. **Monitor Costs**: Check dashboard regularly
2. **Set Alerts**: Enable error notifications
3. **Backup DB**: Enable automatic backups
4. **Test Locally**: Always test with Docker first
5. **Update Deps**: Keep requirements.txt updated

---

## 📞 Support

- Render Docs: https://render.com/docs
- Render Support: https://render.com/support
