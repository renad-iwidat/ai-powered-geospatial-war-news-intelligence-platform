# Instagram API Integration - Complete Setup

## ✅ ما تم إنجازه

تم إضافة Instagram API integration كاملة للتطبيق بحيث:
- ✅ يقرا آخر 10 ريلز/بوست من صفحة Instagram business account
- ✅ يحدّث البيانات كل 15 دقيقة تلقائياً
- ✅ يخزن البيانات في الـ memory cache
- ✅ يرجع معلومات الحساب والـ engagement metrics
- ✅ يدعم filtering للريلز فقط

## 📁 الملفات المضافة/المعدلة

### ملفات جديدة:

1. **app/schemas/instagram_content.py** (95 lines)
   - Pydantic models للـ Instagram data
   - InstagramMedia, InstagramBusinessAccount, InstagramMediaInsight

2. **app/services/instagram_service.py** (165 lines)
   - Service layer للـ Instagram API
   - Caching system (15 دقيقة)
   - Methods: get_account_info, get_latest_media, get_media_insights, get_feed_with_cache

3. **app/api/v1/endpoints/instagram_feed.py** (155 lines)
   - 4 API endpoints
   - GET /api/v1/instagram/feed
   - GET /api/v1/instagram/reels
   - GET /api/v1/instagram/account
   - GET /api/v1/instagram/media/{id}/insights

4. **scripts/test_instagram_api.py** (85 lines)
   - اختبار الـ API
   - التحقق من الـ configuration
   - اختبار الـ caching

### ملفات معدلة:

1. **app/core/config.py**
   - إضافة 4 متغيرات Instagram

2. **app/api/v1/router.py**
   - إضافة Instagram endpoints

3. **.env** و **.env.example**
   - إضافة متغيرات Instagram

### ملفات التوثيق:

1. **INSTAGRAM_README.md** - ملخص سريع
2. **INSTAGRAM_QUICK_START.md** - البدء السريع (5 دقائق)
3. **INSTAGRAM_API_SETUP.md** - دليل الإعداد الكامل
4. **INSTAGRAM_FRONTEND_INTEGRATION.md** - دليل الـ Frontend
5. **INSTAGRAM_DOCKER_SETUP.md** - دليل Docker
6. **INSTAGRAM_INTEGRATION_SUMMARY.md** - ملخص التطبيق

## 🚀 الخطوات التالية

### 1. الحصول على Instagram Credentials

```bash
# اذهب إلى Facebook Developers
# https://developers.facebook.com/

# 1. Create App
# 2. Get Access Token من Graph API Explorer
# 3. Get Business Account ID من /me/instagram_business_accounts
```

### 2. تحديث .env

```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400400533878
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_API_VERSION=v18.0
INSTAGRAM_CACHE_DURATION_MINUTES=15
```

### 3. اختبار الـ API

```bash
# اختبار الـ service
python scripts/test_instagram_api.py

# أو اختبر الـ endpoint مباشرة
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"
```

### 4. دمج في Frontend

```typescript
// استخدم الـ API من React component
const response = await fetch('/api/v1/instagram/feed?limit=10');
const data = await response.json();
```

## 📊 API Endpoints

| الـ Endpoint | الوصف | Query Params |
|-----------|-------|--------------|
| `GET /api/v1/instagram/feed` | آخر 10 ريلز/بوست | limit, include_insights |
| `GET /api/v1/instagram/reels` | الريلز فقط | limit |
| `GET /api/v1/instagram/account` | معلومات الحساب | - |
| `GET /api/v1/instagram/media/{id}/insights` | الـ insights | - |

## 💾 Caching

```
First Request (0 min):
  ├─ Fetch from Instagram API
  ├─ Store in memory
  └─ Return data (cached: false)

Requests 1-14 (1-14 min):
  ├─ Return cached data
  └─ (cached: true, next_update_in_minutes: X)

Request 15 (15 min):
  ├─ Cache expired
  ├─ Fetch fresh data
  └─ Update cache
```

## 🔧 Configuration

```python
# app/core/config.py
INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = None
INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
INSTAGRAM_API_VERSION: str = "v18.0"
INSTAGRAM_CACHE_DURATION_MINUTES: int = 15
```

## 📝 Response Example

```json
{
  "account": {
    "id": "17841400400533878",
    "name": "Account Name",
    "biography": "Bio text",
    "followers_count": 1000,
    "follows_count": 500,
    "media_count": 50,
    "profile_picture_url": "https://...",
    "website": "https://example.com"
  },
  "media": [
    {
      "id": "18123456789",
      "caption": "Post caption",
      "media_type": "REELS",
      "media_url": "https://...",
      "permalink": "https://instagram.com/p/...",
      "timestamp": "2024-03-18T10:30:00",
      "like_count": 150,
      "comments_count": 25,
      "insights": null
    }
  ],
  "total_count": 10,
  "last_updated": "2024-03-18T10:30:00",
  "next_update_in_minutes": 15,
  "cached": true
}
```

## 🧪 Testing

```bash
# اختبار الـ service
python scripts/test_instagram_api.py

# اختبار الـ endpoint
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"

# مع include_insights
curl "http://localhost:7235/api/v1/instagram/feed?limit=10&include_insights=true"

# الريلز فقط
curl "http://localhost:7235/api/v1/instagram/reels?limit=10"

# معلومات الحساب
curl "http://localhost:7235/api/v1/instagram/account"
```

## ⚠️ ملاحظات مهمة

1. **Access Token**: استخدم Long-Lived token (60 يوم)
2. **Business Account**: الحساب يجب يكون business account
3. **Permissions**: تأكد من الـ permissions المطلوبة
4. **Rate Limiting**: Instagram API لديها rate limits
5. **Caching**: يقلل من عدد الـ API calls

## 🔗 المراجع

- [INSTAGRAM_QUICK_START.md](./INSTAGRAM_QUICK_START.md) - البدء السريع
- [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md) - دليل الإعداد الكامل
- [INSTAGRAM_FRONTEND_INTEGRATION.md](./INSTAGRAM_FRONTEND_INTEGRATION.md) - دليل الـ Frontend
- [INSTAGRAM_DOCKER_SETUP.md](./INSTAGRAM_DOCKER_SETUP.md) - دليل Docker

## 📚 الملفات الرئيسية

```
app/
├── schemas/
│   └── instagram_content.py          # Pydantic models
├── services/
│   └── instagram_service.py          # Service layer
├── api/v1/
│   ├── endpoints/
│   │   └── instagram_feed.py         # API endpoints
│   └── router.py                     # Router (updated)
└── core/
    └── config.py                     # Config (updated)

scripts/
└── test_instagram_api.py             # Test script

.env                                  # Environment variables (updated)
.env.example                          # Example (updated)
```

## ✅ Checklist

- [x] Service layer للـ Instagram API
- [x] API endpoints
- [x] Pydantic models
- [x] Caching system (15 دقيقة)
- [x] Configuration
- [x] Test script
- [x] Documentation
- [x] Frontend integration guide
- [x] Docker setup guide
- [ ] Add Instagram credentials to .env
- [ ] Test the API
- [ ] Integrate in Frontend

## 🎉 تمام!

الآن لديك Instagram API integration كاملة وجاهزة للاستخدام!
