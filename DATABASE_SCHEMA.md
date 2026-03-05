# GeoNews AI - Database Schema

## 📊 Overview
قاعدة البيانات تحتوي على **8 جداول** و **3 views**

---

## 🗂️ Tables Structure

### 1. **sources** (16 rows)
مصادر الأخبار (مواقع، قنوات، إلخ)
```
id (PK)
source_type_id (FK → source_types)
name
url
is_active
created_at
```

### 2. **source_types** (2 rows)
أنواع المصادر (RSS, API, etc.)
```
id (PK)
name
description
```

### 3. **languages** (3 rows)
اللغات المدعومة
```
id (PK)
code (ar, en, etc.)
name
```

### 4. **raw_news** (237 rows) ⭐
الأخبار الأصلية
```
id (PK)
source_id (FK → sources)
url
title_original
content_original
language_id (FK → languages)
published_at
fetched_at
processing_status
has_numbers (boolean - للتحقق من وجود أرقام)
created_at
```

### 5. **translations** (118 rows)
ترجمات الأخبار
```
id (PK)
raw_news_id (FK → raw_news)
language_id (FK → languages)
title
content
created_at
```

### 6. **locations** (20 rows)
الأماكن الجغرافية المستخرجة
```
id (PK)
name
country_code
latitude
longitude
region_level
osm_id (OpenStreetMap ID)
osm_type (node/way/relation)
```

### 7. **news_events** (40 rows) ⭐
ربط الأخبار بالأماكن
```
id (PK)
raw_news_id (FK → raw_news)
location_id (FK → locations)
place_name
event_type
created_at
```

### 8. **event_metrics** (0 rows)
المقاييس المستخرجة من الأخبار
```
id (PK)
event_id (FK → news_events)
metric_type (killed, injured, missiles_launched, etc.)
value (integer)
snippet (نص الجملة)
created_at
```

---

## 👁️ Views

### 1. **v_news_ar**
عرض للأخبار العربية

### 2. **v_news_snapshot_ar**
عرض سريع للأخبار العربية

### 3. **vw_news_ar_feed** ⭐
العرض الرئيسي المستخدم في API
- يدمج raw_news مع translations
- يعرض النص العربي (أصلي أو مترجم)
- يحسب عدد الأحداث والمقاييس

---

## 🔗 Relationships Flow

```
source_types
    ↓
sources
    ↓
raw_news ←→ translations
    ↓           ↑
    ↓      languages
    ↓
news_events ←→ locations
    ↓
event_metrics
```

---

## 📈 Current Data Status

| Table | Rows | Status |
|-------|------|--------|
| raw_news | 237 | ✅ فيه بيانات |
| translations | 118 | ✅ فيه بيانات |
| news_events | 40 | ✅ فيه بيانات |
| locations | 20 | ✅ فيه بيانات |
| event_metrics | 0 | ⚠️ فاضي - لازم نشغل metrics processor |
| sources | 16 | ✅ فيه بيانات |
| languages | 3 | ✅ فيه بيانات |
| source_types | 2 | ✅ فيه بيانات |

---

## 🎯 Processing Pipeline

1. **Data Collection**: الأخبار تيجي من sources وتتخزن في raw_news
2. **Translation**: إذا مش عربي، تترجم وتتخزن في translations
3. **Location Extraction**: 
   - NER يستخرج أسماء أماكن من النص العربي
   - Geocoding يحول الأسماء لإحداثيات
   - تتخزن في locations و news_events
4. **Metrics Extraction**: 
   - يستخرج أرقام (قتلى، صواريخ، إلخ)
   - تتخزن في event_metrics
   - ⚠️ **لسا ما اشتغل - الجدول فاضي**

---

## 🔍 Key Observations

1. ✅ عندك 237 خبر في raw_news
2. ✅ 118 ترجمة (يعني تقريباً نص الأخبار مترجمة)
3. ✅ 40 حدث مربوط بأماكن (news_events)
4. ✅ 20 مكان جغرافي محدد
5. ⚠️ **event_metrics فاضي** - لازم نشغل `/process/metrics` endpoint

---

## 🚀 Next Steps

1. تشغيل metrics processor لاستخراج الأرقام
2. معالجة باقي الأخبار (197 خبر لسا ما إلهم events)
3. فحص الـ views وشوف شو بترجع
