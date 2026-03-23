# شرح الكود: معالجة الأحداث واستخراج الدول 💻

## 📌 نقطة البداية: Scheduler

### الملف: `app/services/scheduler.py`

```python
class SchedulerManager:
    def start(self):
        """بدء المجدول"""
        self.scheduler = BackgroundScheduler(
            daemon=True,
            max_workers=2  # عاملين متوازيين
        )
        
        # كل 15 دقيقة: معالجة البيانات
        self.scheduler.add_job(
            self._run_data_processing_sync,
            trigger=IntervalTrigger(minutes=15),
            id='data_processing_job',
            max_instances=1,  # منع التداخل
        )
        
        # كل 10 ساعات: توليد التنبؤات
        self.scheduler.add_job(
            self._run_ai_forecast_sync,
            trigger=IntervalTrigger(hours=10),
            id='ai_forecast_job',
            max_instances=1,
        )
        
        self.scheduler.start()
```

**ماذا يحدث:**
1. ينشئ مجدول في الخلفية (Background)
2. يسجل مهمتين:
   - معالجة البيانات كل 15 دقيقة
   - توليد التنبؤات كل 10 ساعات
3. يبدأ المجدول

---

## 🌍 المرحلة 1: استخراج الأماكن

### الملف: `app/services/geo/location_processor.py`

#### الخطوة 1: قراءة الأخبار العربية

```python
async def _get_news_batch(conn, batch_size):
    """قراءة أخبار عربية من قاعدة البيانات"""
    
    ar_id = await _get_ar_language_id(conn)  # الحصول على ID اللغة العربية
    
    return await conn.fetch(
        """
        SELECT
          rn.id AS raw_news_id,
          COALESCE(t.title, rn.title_original) AS title_ar,
          COALESCE(t.content, rn.content_original) AS content_ar
        FROM raw_news rn
        LEFT JOIN translations t
          ON t.raw_news_id = rn.id AND t.language_id = $1
        WHERE
          (t.id IS NOT NULL OR rn.language_id = $1)  -- نص عربي
          AND NOT EXISTS (
            SELECT 1 FROM news_events ne 
            WHERE ne.raw_news_id = rn.id  -- لم تتم معالجته بعد
          )
        ORDER BY COALESCE(rn.published_at, rn.fetched_at) DESC
        LIMIT $2
        """,
        ar_id,
        batch_size
    )
```

**الاستعلام يجيب:**
- الأخبار التي لديها نص عربي (ترجمة أو أصلي)
- الأخبار التي لم تتم معالجتها بعد (لا توجد news_events لها)
- مرتبة حسب التاريخ (الأحدث أولاً)

**مثال النتيجة:**
```
raw_news_id: 123
title_ar: "غارات إسرائيلية على غزة"
content_ar: "شنت إسرائيل غارات جوية على قطاع غزة..."
```

#### الخطوة 2: تحضير النص

```python
def preprocess_text_for_ner(text):
    """فصل حروف الجر عن أسماء الأماكن"""
    
    # فصل حرف جر واحد قبل "ال"
    text = re.sub(r"\b([وفبكل])(?=ال)", r"\1 ", text)
    
    return text
```

**مثال:**
```
Input:  "غارات على الامارات والبحرين وبالسعودية"
Output: "غارات على الامارات و البحرين و ب السعودية"
```

**لماذا؟**
- NER يعمل بشكل أفضل عندما تكون الكلمات منفصلة
- حروف الجر (و، ب، ل، ك، ف) قد تكون ملتصقة بأسماء الأماكن

#### الخطوة 3: استخراج الأماكن (NER)

```python
# في app/services/nlp/ner_camel.py

def extract_places_ner(text):
    """استخراج أسماء الأماكن من النص العربي"""
    
    ner = get_ner()  # الحصول على نموذج CAMeL NER
    
    # تقسيم النص إلى جمل
    sentences = re.split(r'[\.!\؟\n]+', text)
    
    places = []
    
    for sentence in sentences:
        if len(sentence) < 3:
            continue
        
        # تشغيل NER على الجملة
        labels = ner.predict_sentence(sentence.split())
        
        # استخراج الكيانات من نوع LOC و GPE
        current_entity = []
        current_type = None
        
        for word, label in zip(sentence.split(), labels):
            if label.startswith('B-'):  # بداية كيان
                # حفظ الكيان السابق
                if current_entity and current_type in ('LOC', 'GPE'):
                    entity_text = ' '.join(current_entity)
                    normalized = normalize_ar(entity_text)
                    if len(normalized) >= 2:
                        places.append(normalized)
                
                # بدء كيان جديد
                current_entity = [word]
                current_type = label[2:]  # إزالة 'B-'
                
            elif label.startswith('I-') and current_entity:  # داخل كيان
                current_entity.append(word)
                
            else:  # خارج كيان
                if current_entity and current_type in ('LOC', 'GPE'):
                    entity_text = ' '.join(current_entity)
                    normalized = normalize_ar(entity_text)
                    if len(normalized) >= 2:
                        places.append(normalized)
                
                current_entity = []
                current_type = None
    
    # إزالة التكرارات
    seen = set()
    unique_places = []
    for place in places:
        if place not in seen:
            seen.add(place)
            unique_places.append(place)
    
    return unique_places
```

**مثال:**
```
الجملة: "غارات إسرائيلية على غزة والبحرين"
الكلمات: ["غارات", "إسرائيلية", "على", "غزة", "و", "البحرين"]

NER Labels:
- "غارات" → O (خارج)
- "إسرائيلية" → B-GPE (بداية كيان جيوسياسي)
- "على" → O (خارج)
- "غزة" → B-LOC (بداية موقع)
- "و" → O (خارج)
- "البحرين" → B-LOC (بداية موقع)

النتيجة:
- "إسرائيلية" → GPE
- "غزة" → LOC
- "البحرين" → LOC
```

#### الخطوة 4: تحويل الأسماء إلى إحداثيات (Geocoding)

```python
async def geocode_best_effort(place):
    """تحويل اسم مكان إلى إحداثيات"""
    
    geocoder = get_geocoder()  # Nominatim
    
    # فصل حرف جر إذا كان موجود
    place_cleaned = split_prefix_if_safe(place)
    
    # جرب الاسم النظيف أولاً
    if place_cleaned != place:
        geo = await geocoder.geocode_place(place_cleaned)
        
        if geo and geo.get("country_code") and geo.get("osm_id"):
            return geo, place_cleaned
    
    # جرب الاسم الأصلي
    geo = await geocoder.geocode_place(place)
    
    if geo and geo.get("country_code") and geo.get("osm_id"):
        return geo, place
    
    return None, None
```

**مثال:**
```
Input: "البحرين"

Nominatim Response:
{
  "name": "Bahrain",
  "country_code": "BH",
  "lat": 26.0667,
  "lng": 50.5577,
  "osm_id": 305938,
  "osm_type": "relation"
}
```

#### الخطوة 5: حفظ في قاعدة البيانات

```python
async def _upsert_location(conn, name, country_code, lat, lng, osm_id, osm_type):
    """إدراج أو تحديث مكان"""
    
    row = await conn.fetchrow(
        """
        INSERT INTO locations 
        (name, country_code, latitude, longitude, region_level, osm_id, osm_type)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (osm_type, osm_id)  -- إذا كان موجود
        DO UPDATE SET
          latitude = EXCLUDED.latitude,
          longitude = EXCLUDED.longitude,
          name = EXCLUDED.name,
          country_code = EXCLUDED.country_code
        RETURNING id
        """,
        name,
        country_code,
        lat,
        lng,
        "unknown",
        osm_id,
        osm_type
    )
    return int(row["id"])
```

**ماذا يحدث:**
1. يحاول إدراج المكان
2. إذا كان موجود (نفس osm_id و osm_type): يحدّث البيانات
3. يرجع ID المكان

#### الخطوة 6: ربط الأخبار بالأماكن

```python
async def _insert_event(conn, raw_news_id, location_id, place_name):
    """إنشاء ربط بين خبر ومكان"""
    
    await conn.execute(
        """
        INSERT INTO news_events 
        (raw_news_id, location_id, place_name, event_type)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (raw_news_id, location_id) DO NOTHING
        """,
        raw_news_id,
        location_id,
        place_name,
        "unknown"
    )
```

#### الدالة الرئيسية

```python
async def process_locations(pool, batch_size=20):
    """معالجة الأماكن في الأخبار"""
    
    # الخطوة 1: قراءة أخبار عربية
    async with pool.acquire() as conn:
        news_rows = await _get_news_batch(conn, batch_size)
    
    processed_news = 0
    places_detected = 0
    locations_upserted = 0
    events_created = 0
    
    # الخطوة 2: معالجة كل خبر
    for n in news_rows:
        processed_news += 1
        raw_news_id = int(n["raw_news_id"])
        
        # دمج العنوان والمحتوى
        text = (n["title_ar"] or "") + "\n" + (n["content_ar"] or "")
        
        # تحضير النص
        text = preprocess_text_for_ner(text)
        
        # الخطوة 3: استخراج الأماكن
        try:
            places = extract_places_simple(text)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            places = []
        
        if not places:
            continue
        
        # معالجة أول 3 أماكن فقط (لتقليل الطلبات)
        for place in places[:3]:
            places_detected += 1
            
            # الخطوة 4: Geocoding
            geo, place_clean = await geocode_best_effort(place)
            
            if not geo:
                continue
            
            # الخطوة 5 و 6: حفظ وربط
            async with pool.acquire() as conn:
                loc_id = await _upsert_location(
                    conn,
                    place_clean,
                    geo["country_code"],
                    geo["lat"],
                    geo["lng"],
                    geo["osm_id"],
                    geo["osm_type"],
                )
                locations_upserted += 1
                
                await _insert_event(conn, raw_news_id, loc_id, place)
                events_created += 1
    
    return {
        "processed_news": processed_news,
        "places_detected": places_detected,
        "locations_upserted": locations_upserted,
        "events_created": events_created
    }
```

---

## 📊 المرحلة 2: استخراج المقاييس

### الملف: `app/services/extraction/metrics_extractor.py`

#### الخطوة 1: تحويل الأرقام العربية

```python
def convert_arabic_number_words(text):
    """تحويل الأرقام العربية الكتابية إلى أرقام"""
    
    result = text
    
    # قاموس الأرقام العربية
    ARABIC_NUMBERS = {
        'واحد': 1, 'اثنين': 2, 'ثلاثة': 3, 'أربعة': 4, 'خمسة': 5,
        'ستة': 6, 'سبعة': 7, 'ثمانية': 8, 'تسعة': 9, 'عشرة': 10,
        'مئة': 100, 'ألف': 1000,
        # ... المزيد
    }
    
    # استبدال الأرقام الكتابية
    for word, number in sorted(ARABIC_NUMBERS.items(), 
                               key=lambda x: len(x[0]), 
                               reverse=True):  # الأطول أولاً
        result = re.sub(r'\b' + re.escape(word) + r'\b', 
                       str(number), 
                       result, 
                       flags=re.IGNORECASE)
    
    # التعامل مع صيغة المثنى
    dual_patterns = [
        (r'صاروخين', 'صاروخ'),
        (r'طائرتين', 'طائرة'),
        (r'جنديين', 'جندي'),
        # ... المزيد
    ]
    
    for dual_word, singular in dual_patterns:
        result = re.sub(r'\b' + dual_word + r'\b', 
                       f'2 {singular}', 
                       result, 
                       flags=re.IGNORECASE)
    
    return result
```

**مثال:**
```
Input:  "أطلقت إسرائيل ثلاثة صواريخ وطائرتين مسيرتين"
Output: "أطلقت إسرائيل 3 صواريخ و 2 طائرة مسيرة"
```

#### الخطوة 2: استخراج المقاييس بـ Regex

```python
PATTERNS = [
    # الصواريخ المطلقة
    (
        "missiles_launched",
        r"(?:أطلق|أطلقت|اطلق|اطلقت).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),
    
    # الصواريخ المعترضة
    (
        "missiles_intercepted",
        r"(?:اعترض|اعترضت|أسقط|أسقطت).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),
    
    # الطائرات المسيرة المطلقة
    (
        "drones_launched",
        r"(?:اطلق|اطلقت).{0,50}?(\d+)\s*(?:طائرة مسيرة|مسيرة|درون)"
    ),
    
    # القتلى
    (
        "killed",
        r"(?:مقتل|قتل|استشهاد).{0,30}?(\d+)\s*(?:شخص|شهيد|قتيل)?"
    ),
    
    # الجرحى
    (
        "injured",
        r"(?:اصابة|جرح|مصاب).{0,30}?(\d+)\s*(?:شخص|مصاب|جريح)?"
    ),
    
    # ... المزيد
]

def extract_metrics(text):
    """استخراج جميع المقاييس من النص"""
    
    metrics = []
    
    if not text:
        return metrics
    
    try:
        # تطبيع النص
        text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        
        # تحويل الأرقام العربية
        text = convert_arabic_number_words(text)
        
        # تقسيم إلى جمل
        sentences = re.split(r"[\.!\؟\n]", text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # جرب كل نمط
            for metric_type, pattern in PATTERNS:
                try:
                    matches = re.findall(pattern, sentence, re.IGNORECASE)
                    
                    for m in matches:
                        try:
                            value = int(m)
                            
                            # تصفية القيم غير المعقولة
                            if value <= 0 or value > 100000:
                                continue
                            
                            metrics.append({
                                "metric_type": metric_type,
                                "value": value,
                                "snippet": sentence[:200]
                            })
                        except (ValueError, TypeError):
                            continue
                except Exception:
                    continue
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return []
    
    return metrics
```

**مثال:**
```
النص:
"أطلقت إسرائيل 3 صواريخ على غزة، مما أسفر عن مقتل 15 شخص وإصابة 30 آخرين"

النتيجة:
[
  {
    "metric_type": "missiles_launched",
    "value": 3,
    "snippet": "أطلقت إسرائيل 3 صواريخ على غزة..."
  },
  {
    "metric_type": "killed",
    "value": 15,
    "snippet": "مما أسفر عن مقتل 15 شخص..."
  },
  {
    "metric_type": "injured",
    "value": 30,
    "snippet": "وإصابة 30 آخرين"
  }
]
```

#### الخطوة 3: حفظ المقاييس

```python
# في app/services/extraction/metrics_processor.py

async def process_metrics(pool, batch_size=20):
    """معالجة المقاييس"""
    
    # قراءة أحداث معالجة
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                ne.id AS event_id,
                ne.place_name,
                COALESCE(t.content, rn.content_original) AS content
            FROM news_events ne
            JOIN raw_news rn ON rn.id = ne.raw_news_id
            LEFT JOIN translations t ON t.raw_news_id = rn.id
            WHERE rn.has_numbers = true
            AND NOT EXISTS (
                SELECT 1 FROM event_metrics em
                WHERE em.event_id = ne.id
            )
            LIMIT $1
            """,
            batch_size
        )
    
    processed = 0
    metrics_created = 0
    
    # معالجة كل حدث
    for r in rows:
        processed += 1
        event_id = r["event_id"]
        text = r["content"] or ""
        
        # استخراج المقاييس
        try:
            metrics = extract_metrics(text)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            metrics = []
        
        if not metrics:
            continue
        
        # حفظ المقاييس
        async with pool.acquire() as conn:
            for m in metrics:
                try:
                    await conn.execute(
                        """
                        INSERT INTO event_metrics
                        (event_id, metric_type, value, snippet)
                        VALUES ($1, $2, $3, $4)
                        """,
                        event_id,
                        m["metric_type"],
                        m["value"],
                        m["snippet"][:200]
                    )
                    metrics_created += 1
                except Exception:
                    pass  # تخطي التكرارات
    
    return {
        "processed_events": processed,
        "metrics_created": metrics_created
    }
```

---

## 🔄 تدفق البيانات الكامل

```
┌─────────────────────────────────────────────────────────────┐
│ Scheduler (كل 15 دقيقة)                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ _run_data_processing()                                      │
│ ├─ POST /api/v1/data-processing/extract-locations          │
│ └─ POST /api/v1/data-processing/extract-metrics            │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │ process_locations()  │  │ process_metrics()    │
    │                      │  │                      │
    │ 1. قراءة أخبار      │  │ 1. قراءة أحداث      │
    │ 2. استخراج أماكن    │  │ 2. استخراج أرقام    │
    │ 3. Geocoding        │  │ 3. حفظ في DB        │
    │ 4. حفظ في DB        │  │                      │
    └──────────────────────┘  └──────────────────────┘
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │ قاعدة البيانات       │
                │ ├─ locations         │
                │ ├─ news_events       │
                │ └─ event_metrics     │
                └──────────────────────┘
```

---

## 🧪 مثال عملي كامل

### الخبر الأصلي:
```
"أطلقت إسرائيل ثلاثة صواريخ على غزة والبحرين، 
مما أسفر عن مقتل 15 شخص وإصابة 30 آخرين"
```

### الخطوات:

#### 1. قراءة الخبر
```python
raw_news_id = 123
title_ar = "غارات إسرائيلية على غزة والبحرين"
content_ar = "أطلقت إسرائيل ثلاثة صواريخ على غزة والبحرين..."
```

#### 2. تحضير النص
```python
text = "أطلقت إسرائيل ثلاثة صواريخ على غزة و البحرين..."
```

#### 3. استخراج الأماكن
```python
places = ["إسرائيلية", "غزة", "البحرين"]
```

#### 4. Geocoding
```python
# "إسرائيلية" → Israel (IL)
# "غزة" → Palestine (PS)
# "البحرين" → Bahrain (BH)

locations = [
    {"name": "إسرائيلية", "country_code": "IL", "lat": 31.95, "lng": 35.20},
    {"name": "غزة", "country_code": "PS", "lat": 31.95, "lng": 35.20},
    {"name": "البحرين", "country_code": "BH", "lat": 26.07, "lng": 50.56}
]
```

#### 5. حفظ الأماكن والأحداث
```python
# جدول locations
INSERT INTO locations VALUES (1, "إسرائيلية", "IL", 31.95, 35.20, ...)
INSERT INTO locations VALUES (2, "غزة", "PS", 31.95, 35.20, ...)
INSERT INTO locations VALUES (3, "البحرين", "BH", 26.07, 50.56, ...)

# جدول news_events
INSERT INTO news_events VALUES (1, 123, 1, "إسرائيلية", "unknown")
INSERT INTO news_events VALUES (2, 123, 2, "غزة", "unknown")
INSERT INTO news_events VALUES (3, 123, 3, "البحرين", "unknown")
```

#### 6. تحويل الأرقام العربية
```python
text = "أطلقت إسرائيل 3 صواريخ على غزة و البحرين، مما أسفر عن مقتل 15 شخص وإصابة 30 آخرين"
```

#### 7. استخراج المقاييس
```python
metrics = [
    {"metric_type": "missiles_launched", "value": 3, "snippet": "أطلقت إسرائيل 3 صواريخ..."},
    {"metric_type": "killed", "value": 15, "snippet": "مقتل 15 شخص..."},
    {"metric_type": "injured", "value": 30, "snippet": "إصابة 30 آخرين"}
]
```

#### 8. حفظ المقاييس
```python
# جدول event_metrics
INSERT INTO event_metrics VALUES (1, 1, "missiles_launched", 3, "أطلقت إسرائيل 3 صواريخ...")
INSERT INTO event_metrics VALUES (2, 1, "killed", 15, "مقتل 15 شخص...")
INSERT INTO event_metrics VALUES (3, 1, "injured", 30, "إصابة 30 آخرين")
```

### النتيجة النهائية:
```
news_events:
- event_id: 1, raw_news_id: 123, location_id: 1, place_name: "إسرائيلية"
- event_id: 2, raw_news_id: 123, location_id: 2, place_name: "غزة"
- event_id: 3, raw_news_id: 123, location_id: 3, place_name: "البحرين"

event_metrics:
- event_id: 1, metric_type: "missiles_launched", value: 3
- event_id: 1, metric_type: "killed", value: 15
- event_id: 1, metric_type: "injured", value: 30
```

---

## 📝 ملاحظات مهمة

### 1. معالجة الأخطاء
```python
try:
    places = extract_places_simple(text)
except Exception as e:
    logging.error(f"Error: {str(e)}")
    places = []  # تخطي الخبر والمتابعة
```

### 2. التخزين المؤقت
```python
# البحث عن مكان موجود
existing = await conn.fetchrow(
    "SELECT id FROM locations WHERE name = $1 LIMIT 1",
    name
)
if existing:
    return int(existing["id"])  # استخدام الموجود
```

### 3. منع التكرار
```python
ON CONFLICT (raw_news_id, location_id) DO NOTHING
# إذا كان الربط موجود: لا تفعل شيء
```

### 4. معدل الطلبات
```python
# Nominatim: 1 طلب/ثانية
# معالجة أول 3 أماكن فقط لكل خبر
for place in places[:3]:
    # ...
```

