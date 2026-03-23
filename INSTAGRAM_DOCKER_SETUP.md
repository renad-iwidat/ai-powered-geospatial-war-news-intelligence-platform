# Instagram API - Docker Setup

## تحديث docker-compose.yml

إذا كنت تستخدم Docker، تأكد من أن متغيرات Instagram موجودة في `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      # ... existing variables ...
      INSTAGRAM_BUSINESS_ACCOUNT_ID: ${INSTAGRAM_BUSINESS_ACCOUNT_ID}
      INSTAGRAM_ACCESS_TOKEN: ${INSTAGRAM_ACCESS_TOKEN}
      INSTAGRAM_API_VERSION: ${INSTAGRAM_API_VERSION}
      INSTAGRAM_CACHE_DURATION_MINUTES: ${INSTAGRAM_CACHE_DURATION_MINUTES}
```

## تحديث .env للـ Docker

أضف إلى `.env`:

```env
# Instagram Configuration
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400400533878
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here
INSTAGRAM_API_VERSION=v18.0
INSTAGRAM_CACHE_DURATION_MINUTES=15
```

## تشغيل Docker

```bash
# Build and run
docker-compose up --build

# أو بدون rebuild
docker-compose up

# في terminal آخر، اختبر الـ API
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"
```

## التحقق من الـ Logs

```bash
# شوف logs الـ backend
docker-compose logs -f backend

# شوف logs الـ frontend
docker-compose logs -f frontend
```

## إعادة تشغيل الـ Backend

```bash
docker-compose restart backend
```

## إيقاف الـ Services

```bash
docker-compose down
```

## ملاحظات

1. تأكد من أن `.env` يحتوي على جميع المتغيرات المطلوبة
2. الـ Instagram token يجب يكون Long-Lived (60 يوم)
3. الـ caching يعمل داخل الـ container
4. إذا غيّرت الـ token، أعد تشغيل الـ backend

## Troubleshooting

### الـ API ترجع 503
```
Unable to fetch Instagram account information. Check credentials.
```

**الحل:**
- تأكد من أن الـ token صحيح
- تأكد من أن الـ account ID صحيح
- تأكد من أن الـ token لم ينتهي

### الـ Container لا يبدأ
```bash
# شوف الـ logs
docker-compose logs backend

# أعد بناء الـ image
docker-compose build --no-cache backend
```

### الـ API بطيء
- الـ caching يجب يكون يعمل (15 دقيقة)
- تأكد من أن الـ network سريع
- تأكد من أن Instagram API responsive
