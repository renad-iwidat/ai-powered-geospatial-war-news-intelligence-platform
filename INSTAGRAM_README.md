# Instagram API Integration

## 🎯 الهدف
API endpoint يقرا من Instagram ويرجع آخر 10 ريلز/بوست من صفحة business account، مع تحديث البيانات كل 15 دقيقة.

## 🚀 البدء السريع

### 1. إضافة متغيرات البيئة

في `.env`:
```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400400533878
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_API_VERSION=v18.0
INSTAGRAM_CACHE_DURATION_MINUTES=15
```

### 2. استخدام الـ API

```bash
# آخر 10 ريلز/بوست
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"

# الريلز فقط
curl "http://localhost:7235/api/v1/instagram/reels?limit=10"

# معلومات الحساب
curl "http://localhost:7235/api/v1/instagram/account"
```

## 📚 الملفات الرئيسية

| الملف | الوصف |
|------|-------|
| `app/services/instagram_service.py` | Service layer للـ Instagram API |
| `app/api/v1/endpoints/instagram_feed.py` | API endpoints |
| `app/schemas/instagram_content.py` | Pydantic models |
| `INSTAGRAM_API_SETUP.md` | دليل الإعداد الكامل |
| `INSTAGRAM_FRONTEND_INTEGRATION.md` | دليل الـ Frontend |

## 🔧 الإعدادات

### الحصول على Access Token

1. اذهب إلى [Facebook Developers](https://developers.facebook.com/)
2. اضغط "My Apps" → "Create App"
3. استخدم Graph API Explorer للحصول على token
4. اختر الـ permissions المطلوبة

### الحصول على Business Account ID

```bash
# استخدم Graph API Explorer
GET /me/instagram_business_accounts
```

## 📊 Response Example

```json
{
  "account": {
    "id": "17841400400533878",
    "name": "Account Name",
    "followers_count": 1000,
    "media_count": 50
  },
  "media": [
    {
      "id": "18123456789",
      "caption": "Post caption",
      "media_type": "REELS",
      "media_url": "https://...",
      "like_count": 150,
      "comments_count": 25,
      "timestamp": "2024-03-18T10:30:00"
    }
  ],
  "total_count": 10,
  "cached": true,
  "next_update_in_minutes": 15
}
```

## 💾 Caching

- البيانات تُخزن لمدة **15 دقيقة**
- بعدها يتم جلب البيانات الجديدة تلقائياً
- الـ response يحتوي على `cached` و `next_update_in_minutes`

## 🧪 الاختبار

```bash
python scripts/test_instagram_api.py
```

## 📖 المراجع

- [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md) - دليل الإعداد الكامل
- [INSTAGRAM_FRONTEND_INTEGRATION.md](./INSTAGRAM_FRONTEND_INTEGRATION.md) - دليل الـ Frontend
- [INSTAGRAM_INTEGRATION_SUMMARY.md](./INSTAGRAM_INTEGRATION_SUMMARY.md) - ملخص التطبيق

## ⚠️ ملاحظات مهمة

1. استخدم **Long-Lived Access Token** (60 يوم)
2. تأكد من أن الـ account هو **Business Account**
3. الـ token ينتهي بعد 60 يوم، يجب تحديثه
4. Instagram API لديها rate limits

## 🔗 API Endpoints

| الـ Endpoint | الوصف |
|-----------|-------|
| `GET /api/v1/instagram/feed` | آخر 10 ريلز/بوست |
| `GET /api/v1/instagram/reels` | الريلز فقط |
| `GET /api/v1/instagram/account` | معلومات الحساب |
| `GET /api/v1/instagram/media/{id}/insights` | الـ insights |

## 🆘 Troubleshooting

### "Invalid access token"
- تأكد من أن الـ token صحيح
- تأكد من أن الـ token لم ينتهي

### "User does not have permission"
- تأكد من الـ permissions
- أعد تفويض الـ app

### "No media found"
- تأكد من أن الحساب لديه posts
- تأكد من أن الـ account ID صحيح
