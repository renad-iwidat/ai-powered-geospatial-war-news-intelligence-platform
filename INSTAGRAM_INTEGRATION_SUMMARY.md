# Instagram Integration Summary

## ✅ ما تم إنجازه

تم إضافة Instagram API integration كاملة للتطبيق بحيث يقرا آخر 10 ريلز/بوست من صفحة Instagram business account مع تحديث البيانات كل 15 دقيقة.

## 📁 الملفات المضافة/المعدلة

### ملفات جديدة:
1. **app/schemas/instagram_content.py** - Pydantic models
   - `InstagramMedia` - بيانات الـ post/reel
   - `InstagramBusinessAccount` - معلومات الحساب
   - `InstagramMediaInsight` - الـ engagement metrics
   - `InstagramFeedResponse` - الـ response model

2. **app/services/instagram_service.py** - Service layer
   - `get_account_info()` - جلب معلومات الحساب
   - `get_latest_media()` - جلب آخر 10 ريلز/بوست
   - `get_media_insights()` - جلب الـ engagement metrics
   - `get_feed_with_cache()` - جلب البيانات مع caching

3. **app/api/v1/endpoints/instagram_feed.py** - API endpoints
   - `GET /api/v1/instagram/feed` - آخر 10 ريلز/بوست
   - `GET /api/v1/instagram/account` - معلومات الحساب
   - `GET /api/v1/instagram/reels` - الريلز فقط
   - `GET /api/v1/instagram/media/{id}/insights` - الـ insights

4. **scripts/test_instagram_api.py** - اختبار الـ API

5. **INSTAGRAM_API_SETUP.md** - دليل الإعداد الكامل

### ملفات معدلة:
1. **app/core/config.py** - إضافة متغيرات Instagram
2. **app/api/v1/router.py** - إضافة Instagram endpoints
3. **.env** و **.env.example** - متغيرات البيئة

## 🔧 الإعدادات المطلوبة

أضف هذه المتغيرات إلى `.env`:

```env
# Instagram Configuration
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400400533878
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here
INSTAGRAM_API_VERSION=v18.0
INSTAGRAM_CACHE_DURATION_MINUTES=15
```

## 🚀 كيفية الاستخدام

### 1. الحصول على آخر 10 ريلز/بوست:
```bash
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"
```

### 2. الحصول على الريلز فقط:
```bash
curl "http://localhost:7235/api/v1/instagram/reels?limit=10"
```

### 3. الحصول على معلومات الحساب:
```bash
curl "http://localhost:7235/api/v1/instagram/account"
```

### 4. الحصول على Insights لـ media معين:
```bash
curl "http://localhost:7235/api/v1/instagram/media/{media_id}/insights"
```

## 💾 نظام الـ Caching

- البيانات تُخزن في الـ memory لمدة **15 دقيقة**
- بعد انتهاء الـ 15 دقيقة، يتم جلب البيانات الجديدة تلقائياً
- الـ response يحتوي على:
  - `cached`: هل البيانات من الـ cache
  - `next_update_in_minutes`: كم دقيقة باقية للتحديث

## 📊 Response Example

```json
{
  "account": {
    "id": "17841400400533878",
    "name": "Account Name",
    "biography": "Bio text",
    "followers_count": 1000,
    "media_count": 50,
    "profile_picture_url": "https://..."
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
      "comments_count": 25
    }
  ],
  "total_count": 10,
  "last_updated": "2024-03-18T10:30:00",
  "next_update_in_minutes": 15,
  "cached": true
}
```

## 🧪 الاختبار

لاختبار الـ API:

```bash
python scripts/test_instagram_api.py
```

## ⚙️ المتطلبات

- Instagram Business Account
- Facebook App مع الـ permissions المطلوبة
- Long-Lived Access Token (صلاحيته 60 يوم)

## 📝 ملاحظات

1. **Rate Limiting**: Instagram API لديها rate limits
2. **Token Expiration**: يجب تحديث الـ token كل 60 يوم
3. **Caching**: يقلل من عدد الـ API calls
4. **Performance**: الـ in-memory cache سريع جداً

## 🔗 المراجع

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api)
- [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md) - دليل الإعداد الكامل
