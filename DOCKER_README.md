# GeoNews AI - Docker Setup

## 🚀 تشغيل المشروع (3 خطوات)

### 1. إعداد البيئة
```bash
# انسخ ملف البيئة
cp .env.docker .env

# عدل الملف وحط API keys تبعك
nano .env
```

### 2. شغل كل شي
```bash
# بناء الصور
docker-compose build

# تشغيل الخدمات
docker-compose up -d
```

### 3. الوصول للتطبيق
- **الفرونت**: http://localhost:3000
- **الباك إند**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📦 الخدمات المتوفرة

| الخدمة | البورت | الوصف |
|--------|--------|-------|
| Frontend | 3000 | واجهة Next.js |
| Backend | 8000 | API FastAPI |
| PostgreSQL | 5432 | قاعدة البيانات |
| Processor | - | معالجة البيانات كل 15 دقيقة (NER + Geocoding + Metrics) |

---

## 🛠️ الأوامر الأساسية

### تشغيل وإيقاف
```bash
# تشغيل كل الخدمات
docker-compose up -d

# إيقاف كل الخدمات
docker-compose down

# إعادة تشغيل
docker-compose restart

# عرض الخدمات الشغالة
docker-compose ps
```

### عرض اللوجات
```bash
# كل الخدمات
docker-compose logs -f

# خدمة معينة
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f processor
```

### التحكم بالـ Processor
```bash
# إيقاف
docker-compose stop processor

# تشغيل
docker-compose start processor

# عرض اللوجات
docker-compose logs -f processor
```

### قاعدة البيانات
```bash
# فتح PostgreSQL shell
docker-compose exec postgres psql -U geonews_user -d geonews_db

# عمل backup
docker-compose exec postgres pg_dump -U geonews_user geonews_db > backup.sql

# استرجاع backup
docker-compose exec -T postgres psql -U geonews_user -d geonews_db < backup.sql
```

### التنظيف
```bash
# حذف كل شي (Containers + Volumes + Images)
docker-compose down -v --rmi all

# حذف Volumes بس
docker-compose down -v

# إعادة بناء من الصفر
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## ⚙️ تعديل الإعدادات

### تغيير وقت الـ Processor

عدل `docker-compose.yml`:
```yaml
processor:
  command: >
    sh -c "
      while true; do
        python scripts/process_all_data.py
        sleep 900  # 900 = 15 دقيقة
      done
    "
```

---

## 🐛 حل المشاكل

### الخدمة ما بتشتغل؟
```bash
# شوف اللوجات
docker-compose logs backend

# أعد تشغيل
docker-compose restart backend
```

### مشكلة بقاعدة البيانات؟
```bash
# تحقق من حالة قاعدة البيانات
docker-compose exec postgres pg_isready -U geonews_user

# أعد تشغيل قاعدة البيانات
docker-compose restart postgres
```

### مساحة ممتلئة؟
```bash
# نظف الصور والـ containers القديمة
docker system prune -a

# نظف الـ volumes
docker volume prune
```

---

## 📝 متغيرات البيئة (.env)

```env
# قاعدة البيانات
POSTGRES_DB=geonews_db
POSTGRES_USER=geonews_user
POSTGRES_PASSWORD=your_password_here

# API Keys
OPENAI_API_KEY=sk-your-key-here
ALPHA_VANTAGE_API_KEY=your-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ✅ التحقق من الصحة

```bash
# تحقق من صحة الباك إند
curl http://localhost:8000/health

# تحقق من صحة قاعدة البيانات
docker-compose exec postgres pg_isready -U geonews_user

# شوف استخدام الموارد
docker stats
```

---

## 🎉 خلص!

المنصة الآن شغالة مع:
- ✅ معالجة بيانات تلقائية كل 15 دقيقة (NER + Geocoding + Metrics)
- ✅ API شغال
- ✅ واجهة تفاعلية
- ✅ قاعدة بيانات دائمة

---

**محتاج مساعدة؟** شوف اللوجات: `docker-compose logs -f`

