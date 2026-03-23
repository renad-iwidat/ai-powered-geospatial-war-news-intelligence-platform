# شرح قاعدة البيانات: معالجة الأحداث واستخراج الدول 🗄️

## 📊 العلاقات بين الجداول

```
┌─────────────────────────────────────────────────────────────────────┐
│                         raw_news                                    │
│                    (الأخبار الخام)                                  │
├─────────────────────────────────────────────────────────────────────┤
│ id (PK)                                                             │
│ title_original (عنوان الخبر الأصلي)                                │
│ content_original (محتوى الخبر الأصلي)                              │
│ language_id (FK → languages)                                        │
│ source_id (FK → sources)                                            │
│ published_at (تاريخ النشر)                                          │
│ fetched_at (تاريخ الجلب)                                            │
│ has_numbers (هل يحتوي على أرقام)                                   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │   translations       │  │   news_events        │
        │  (الترجمات)          │  │  (الأحداث الإخبارية) │
        ├──────────────────────┤  ├──────────────────────┤
        │ id (PK)              │  │ id (PK)              │
        │ raw_news_id (FK)     │  │ raw_news_id (FK)     │
        │ language_id (FK)     │  │ location_id (FK)     │
        │ title (عنوان)        │  │ place_name           │
        │ content (محتوى)      │  │ event_type           │
        │ translated_at        │  │ created_at           │
        └──────────────────────┘  └──────────────────────┘
                                            │
                                            ▼
                                ┌──────────────────────┐
                                │   locations          │
                                │  (الأماكن الجغرافية) │
                                ├──────────────────────┤
                                │ id (PK)              │
                                │ name (اسم المكان)    │
                                │ country_code         │
                                │ latitude             │
                                │ longitude            │
                                │ osm_id               │
                                │ osm_type             │
                                └──────────────────────┘
                                            │
                                            ▼
                                ┌──────────────────────┐
                                │  event_metrics       │
                                │   (المقاييس)         │
                                ├──────────────────────┤
                                │ id (PK)              │
                                │ event_id (FK)        │
                                │ metric_type          │
                                │ value                │
                                │ snippet              │
                                │ created_at           │
                                └──────────────────────┘
```

---

## 📋 تفاصيل الجداول

### 1. جدول `raw_news` (الأخبار الخام)

**الوصف:** يحتوي على جميع الأخبار المجلوبة من المصادر

**الأعمدة:**
```sql
CREATE TABLE raw_news (
    id SERIAL PRIMARY KEY,
    title_original VARCHAR(500),           -- عنوان الخبر الأصلي
    content_original TEXT,                 -- محتوى الخبر الأصلي
    language_id INTEGER REFERENCES languages(id),  -- اللغة
    source_id INTEGER REFERENCES sources(id),      -- المصدر
    published_at TIMESTAMP,                -- تاريخ النشر
    fetched_at TIMESTAMP,                  -- تاريخ الجلب
    has_numbers BOOLEAN,                   -- هل يحتوي على أرقام
    created_at TIMESTAMP DEFAULT NOW()
);
```

**مثال:**
```
id: 123
title_original: "غارات إسرائيلية على غزة والبحرين"
content_original: "شنت إسرائيل غارات جوية على قطاع غزة والبحرين..."
language_id: 1 (عربي)
source_id: 5 (مصدر معين)
published_at: 2024-01-15 10:30:00
fetched_at: 2024-01-15 11:00:00
has_numbers: true
```

---

### 2. جدول `translations` (الترجمات)

**الوصف:** يحتوي على ترجمات الأخبار إلى لغات مختلفة

**الأعمدة:**
```sql
CREATE TABLE translations (
    id SERIAL PRIMARY KEY,
    raw_news_id INTEGER REFERENCES raw_news(id),
    language_id INTEGER REFERENCES languages(id),
    title VARCHAR(500),                    -- عنوان مترجم
    content TEXT,                          -- محتوى مترجم
    translated_at TIMESTAMP DEFAULT NOW()
);
```

**مثال:**
```
id: 456
raw_news_id: 123
language_id: 1 (عربي)
title: "غارات إسرائيلية على غزة والبحرين"
content: "شنت إسرائيل غارات جوية على قطاع غزة والبحرين..."
```

**ملاحظة:** إذا كان الخبر الأصلي عربياً، قد لا توجد ترجمة عربية (أو تكون نفس الأصلي)

---

### 3. جدول `locations` (الأماكن الجغرافية)

**الوصف:** يحتوي على جميع الأماكن المستخرجة من الأخبار

**الأعمدة:**
```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),                     -- اسم المكان
    country_code VARCHAR(2),               -- رمز الدولة (ISO 3166-1 alpha-2)
    latitude DECIMAL(10, 8),               -- خط العرض
    longitude DECIMAL(11, 8),              -- خط الطول
    region_level VARCHAR(50),              -- مستوى المنطقة
    osm_id BIGINT,                         -- معرف OpenStreetMap
    osm_type VARCHAR(20),                  -- نوع OpenStreetMap
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(osm_type, osm_id)               -- فريد: نوع + معرف OSM
);
```

**مثال:**
```
id: 1
name: "غزة"
country_code: "PS"
latitude: 31.95
longitude: 35.20
region_level: "city"
osm_id: 123456
osm_type: "relation"

id: 2
name: "البحرين"
country_code: "BH"
latitude: 26.0667
longitude: 50.5577
region_level: "country"
osm_id: 305938
osm_type: "relation"
```

**ملاحظة:** `osm_id` و `osm_type` يأتيان من Nominatim (OpenStreetMap)

---

### 4. جدول `news_events` (الأحداث الإخبارية)

**الوصف:** يربط الأخبار بالأماكن الجغرافية

**الأعمدة:**
```sql
CREATE TABLE news_events (
    id SERIAL PRIMARY KEY,
    raw_news_id INTEGER REFERENCES raw_news(id),
    location_id INTEGER REFERENCES locations(id),
    place_name VARCHAR(255),               -- اسم المكان (كما استخرج من NER)
    event_type VARCHAR(50),                -- نوع الحدث
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(raw_news_id, location_id)       -- فريد: خبر + مكان
);
```

**مثال:**
```
id: 1
raw_news_id: 123
location_id: 1
place_name: "غزة"
event_type: "unknown"
created_at: 2024-01-15 11:05:00

id: 2
raw_news_id: 123
location_id: 2
place_name: "البحرين"
event_type: "unknown"
created_at: 2024-01-15 11:05:00
```

**ملاحظة:** `UNIQUE(raw_news_id, location_id)` يمنع إنشاء نفس الربط مرتين

---

### 5. جدول `event_metrics` (المقاييس)

**الوصف:** يحتوي على المقاييس الرقمية المستخرجة من الأحداث

**الأعمدة:**
```sql
CREATE TABLE event_metrics (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES news_events(id),
    metric_type VARCHAR(100),              -- نوع المقياس
    value INTEGER,                         -- القيمة الرقمية
    snippet TEXT,                          -- النص الأصلي
    created_at TIMESTAMP DEFAULT NOW()
);
```

**أنواع المقاييس:**
```
missiles_launched          - الصواريخ المطلقة
missiles_intercepted       - الصواريخ المعترضة
drones_launched            - الطائرات المسيرة المطلقة
drones_intercepted         - الطائرات المسيرة المعترضة
aircraft_downed            - الطائرات المسقوطة
airstrikes                 - الغارات الجوية
killed                     - القتلى
civilians_killed           - المدنيين القتلى
soldiers_killed            - الجنود القتلى
injured                    - الجرحى
civilians_injured          - المدنيين الجرحى
military_operations        - العمليات العسكرية
targets_hit                - الأهداف المستهدفة
buildings_destroyed        - المباني المدمرة
troops_deployed            - القوات المنتشرة
tanks_deployed             - الدبابات المنتشرة
evacuated                  - المجلاة
displaced                  - النازحين
```

**مثال:**
```
id: 1
event_id: 1
metric_type: "missiles_launched"
value: 3
snippet: "أطلقت إسرائيل 3 صواريخ على غزة"
created_at: 2024-01-15 11:10:00

id: 2
event_id: 1
metric_type: "killed"
value: 15
snippet: "مما أسفر عن مقتل 15 شخص"
created_at: 2024-01-15 11:10:00

id: 3
event_id: 1
metric_type: "injured"
value: 30
snippet: "وإصابة 30 آخرين"
created_at: 2024-01-15 11:10:00
```

---

## 🔄 تدفق البيانات عبر الجداول

### مثال: معالجة خبر واحد

#### الخبر الأصلي:
```
"أطلقت إسرائيل 3 صواريخ على غزة والبحرين، مما أسفر عن مقتل 15 شخص"
```

#### الخطوة 1: إدراج في `raw_news`
```sql
INSERT INTO raw_news 
(title_original, content_original, language_id, source_id, has_numbers)
VALUES (
    'غارات إسرائيلية على غزة والبحرين',
    'أطلقت إسرائيل 3 صواريخ على غزة والبحرين، مما أسفر عن مقتل 15 شخص',
    1,  -- عربي
    5,  -- مصدر
    true
);
-- النتيجة: raw_news_id = 123
```

#### الخطوة 2: استخراج الأماكن وإدراج في `locations`
```sql
INSERT INTO locations 
(name, country_code, latitude, longitude, osm_id, osm_type)
VALUES 
('غزة', 'PS', 31.95, 35.20, 123456, 'relation'),
('البحرين', 'BH', 26.0667, 50.5577, 305938, 'relation');
-- النتيجة: location_id = 1, 2
```

#### الخطوة 3: ربط الأخبار بالأماكن في `news_events`
```sql
INSERT INTO news_events 
(raw_news_id, location_id, place_name, event_type)
VALUES 
(123, 1, 'غزة', 'unknown'),
(123, 2, 'البحرين', 'unknown');
-- النتيجة: event_id = 1, 2
```

#### الخطوة 4: استخراج المقاييس وإدراج في `event_metrics`
```sql
INSERT INTO event_metrics 
(event_id, metric_type, value, snippet)
VALUES 
(1, 'missiles_launched', 3, 'أطلقت إسرائيل 3 صواريخ...'),
(1, 'killed', 15, 'مما أسفر عن مقتل 15 شخص');
-- النتيجة: metric_id = 1, 2
```

---

## 📊 الاستعلامات الشائعة

### 1. الحصول على جميع الأحداث لخبر معين
```sql
SELECT 
    ne.id,
    ne.place_name,
    l.country_code,
    l.latitude,
    l.longitude
FROM news_events ne
JOIN locations l ON ne.location_id = l.id
WHERE ne.raw_news_id = 123;
```

**النتيجة:**
```
id | place_name | country_code | latitude | longitude
---|---|---|---|---
1  | غزة        | PS           | 31.95    | 35.20
2  | البحرين    | BH           | 26.0667  | 50.5577
```

### 2. الحصول على جميع المقاييس لحدث معين
```sql
SELECT 
    metric_type,
    value,
    snippet
FROM event_metrics
WHERE event_id = 1;
```

**النتيجة:**
```
metric_type        | value | snippet
---|---|---
missiles_launched  | 3     | أطلقت إسرائيل 3 صواريخ...
killed             | 15    | مما أسفر عن مقتل 15 شخص
```

### 3. الحصول على جميع الأخبار لدولة معينة
```sql
SELECT 
    rn.id,
    rn.title_original,
    l.country_code,
    COUNT(em.id) as metrics_count
FROM raw_news rn
JOIN news_events ne ON rn.id = ne.raw_news_id
JOIN locations l ON ne.location_id = l.id
LEFT JOIN event_metrics em ON ne.id = em.event_id
WHERE l.country_code = 'PS'
GROUP BY rn.id, l.country_code;
```

### 4. الحصول على إحصائيات المقاييس
```sql
SELECT 
    metric_type,
    COUNT(*) as count,
    SUM(value) as total,
    AVG(value) as average,
    MAX(value) as maximum,
    MIN(value) as minimum
FROM event_metrics
GROUP BY metric_type
ORDER BY total DESC;
```

**النتيجة:**
```
metric_type        | count | total | average | maximum | minimum
---|---|---|---|---|---
killed             | 150   | 2500  | 16.67   | 100     | 1
injured            | 145   | 3200  | 22.07   | 150     | 2
missiles_launched  | 80    | 450   | 5.63    | 50      | 1
```

### 5. الحصول على الأخبار التي لم تتم معالجتها بعد
```sql
SELECT 
    rn.id,
    rn.title_original,
    rn.published_at
FROM raw_news rn
WHERE NOT EXISTS (
    SELECT 1 FROM news_events ne 
    WHERE ne.raw_news_id = rn.id
)
ORDER BY rn.published_at DESC
LIMIT 50;
```

---

## 🔍 العلاقات والقيود

### 1. Foreign Keys (المفاتيح الأجنبية)

```
raw_news.language_id → languages.id
raw_news.source_id → sources.id
translations.raw_news_id → raw_news.id
translations.language_id → languages.id
news_events.raw_news_id → raw_news.id
news_events.location_id → locations.id
event_metrics.event_id → news_events.id
```

### 2. Unique Constraints (القيود الفريدة)

```
locations: UNIQUE(osm_type, osm_id)
  - منع إدراج نفس المكان مرتين

news_events: UNIQUE(raw_news_id, location_id)
  - منع ربط نفس الخبر بنفس المكان مرتين
```

### 3. Indexes (الفهارس)

```sql
CREATE INDEX idx_raw_news_language ON raw_news(language_id);
CREATE INDEX idx_raw_news_source ON raw_news(source_id);
CREATE INDEX idx_translations_raw_news ON translations(raw_news_id);
CREATE INDEX idx_news_events_raw_news ON news_events(raw_news_id);
CREATE INDEX idx_news_events_location ON news_events(location_id);
CREATE INDEX idx_event_metrics_event ON event_metrics(event_id);
CREATE INDEX idx_event_metrics_type ON event_metrics(metric_type);
```

---

## 📈 حجم البيانات المتوقع

### بعد معالجة 1000 خبر:

```
raw_news:           1,000 صف
locations:          2,000 صف (متوسط 2 مكان لكل خبر)
news_events:        2,000 صف (ربط الأخبار بالأماكن)
event_metrics:      5,000 صف (متوسط 2.5 مقياس لكل حدث)
```

### بعد معالجة 100,000 خبر:

```
raw_news:           100,000 صف
locations:          200,000 صف
news_events:        200,000 صف
event_metrics:      500,000 صف
```

---

## 🔧 الصيانة والتحسينات

### 1. تنظيف البيانات المكررة
```sql
-- حذف الأماكن المكررة
DELETE FROM locations l1
WHERE l1.id > (
    SELECT MIN(l2.id) FROM locations l2
    WHERE l2.osm_type = l1.osm_type 
    AND l2.osm_id = l1.osm_id
);
```

### 2. تحديث الإحصائيات
```sql
-- تحديث إحصائيات الجداول (لتحسين الأداء)
ANALYZE raw_news;
ANALYZE locations;
ANALYZE news_events;
ANALYZE event_metrics;
```

### 3. النسخ الاحتياطي
```bash
# النسخ الاحتياطي الكامل
pg_dump database_name > backup.sql

# النسخ الاحتياطي المضغوط
pg_dump database_name | gzip > backup.sql.gz
```

---

## 📝 ملاحظات مهمة

1. **الأداء:** استخدم الفهارس على الأعمدة المستخدمة بكثرة في WHERE و JOIN
2. **التخزين:** قد تحتاج إلى تقسيم الجداول الكبيرة (partitioning) بعد ملايين الصفوف
3. **النسخ الاحتياطي:** قم بنسخ احتياطي منتظم للبيانات
4. **المراقبة:** راقب حجم الجداول والأداء بانتظام

