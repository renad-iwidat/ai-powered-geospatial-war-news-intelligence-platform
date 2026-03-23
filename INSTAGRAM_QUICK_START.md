# Instagram API - Quick Start Guide

## ⚡ البدء السريع (5 دقائق)

### الخطوة 1: الحصول على Access Token

1. اذهب إلى https://developers.facebook.com/
2. اضغط "My Apps" → "Create App"
3. اختر "Business" كنوع التطبيق
4. في Dashboard، اذهب إلى "Tools" → "Graph API Explorer"
5. اختر الـ app من القائمة العلوية
6. اضغط "Get User Access Token"
7. اختر الـ permissions:
   - `instagram_business_content_publish`
   - `pages_read_engagement`
   - `pages_read_user_content`
8. اضغط "Generate Access Token"
9. انسخ الـ token

### الخطوة 2: الحصول على Business Account ID

في Graph API Explorer، اكتب:
```
GET /me/instagram_business_accounts
```

ستحصل على response زي:
```json
{
  "data": [
    {
      "instagram_business_account": {
        "id": "17841400400533878"
      }
    }
  ]
}
```

انسخ الـ ID.

### الخطوة 3: تحديث .env

أضف إلى `.env`:
```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400400533878
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_API_VERSION=v18.0
INSTAGRAM_CACHE_DURATION_MINUTES=15
```

### الخطوة 4: اختبر الـ API

```bash
# في terminal
curl "http://localhost:7235/api/v1/instagram/feed?limit=10"
```

يجب ترجع JSON مع آخر 10 ريلز/بوست.

## 🎯 الـ Endpoints

### 1. آخر 10 ريلز/بوست
```
GET /api/v1/instagram/feed?limit=10&include_insights=false
```

**Response:**
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

### 2. الريلز فقط
```
GET /api/v1/instagram/reels?limit=10
```

### 3. معلومات الحساب
```
GET /api/v1/instagram/account
```

### 4. Insights لـ media معين
```
GET /api/v1/instagram/media/{media_id}/insights
```

## 💻 استخدام من Frontend

```typescript
// جلب البيانات
const response = await fetch('/api/v1/instagram/feed?limit=10');
const data = await response.json();

// عرض الريلز
data.media.forEach(media => {
  console.log(media.caption);
  console.log(media.media_url);
  console.log(media.like_count);
});
```

## 🔄 Caching

- البيانات تُخزن لمدة **15 دقيقة**
- بعدها يتم جلب البيانات الجديدة تلقائياً
- الـ response يحتوي على:
  - `cached`: هل البيانات من الـ cache
  - `next_update_in_minutes`: كم دقيقة باقية

## ⚠️ مشاكل شائعة

### "Invalid access token"
- تأكد من أن الـ token صحيح
- تأكد من أن الـ token لم ينتهي (60 يوم)

### "User does not have permission"
- تأكد من الـ permissions في الـ app
- أعد تفويض الـ app

### "No media found"
- تأكد من أن الحساب لديه posts/reels
- تأكد من أن الـ account ID صحيح

## 📚 المراجع

- [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md) - دليل الإعداد الكامل
- [INSTAGRAM_FRONTEND_INTEGRATION.md](./INSTAGRAM_FRONTEND_INTEGRATION.md) - دليل الـ Frontend
- [INSTAGRAM_INTEGRATION_SUMMARY.md](./INSTAGRAM_INTEGRATION_SUMMARY.md) - ملخص التطبيق

## 🧪 اختبار الـ API

```bash
python scripts/test_instagram_api.py
```

## ✅ Checklist

- [ ] تم إنشاء Facebook App
- [ ] تم الحصول على Access Token
- [ ] تم الحصول على Business Account ID
- [ ] تم تحديث .env
- [ ] تم اختبار الـ API
- [ ] تم دمج الـ API في Frontend

## 🎉 تمام!

الآن لديك Instagram API integration كاملة. يمكنك:
- جلب آخر 10 ريلز/بوست
- عرضها في الـ Frontend
- البيانات تُحدّث كل 15 دقيقة تلقائياً
