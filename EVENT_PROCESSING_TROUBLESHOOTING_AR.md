# دليل التشغيل والتصحيح: معالجة الأحداث 🔧

## 🚀 كيفية تشغيل النظام

### 1. التأكد من المتطلبات

```bash
# التحقق من Python
python --version  # يجب أن يكون 3.8+

# التحقق من PostgreSQL
psql --version  # يجب أن يكون 12+

# التحقق من المكتبات المطلوبة
pip list | grep -E "fastapi|asyncpg|apscheduler|camel-tools|geopy"
```

### 2. تثبيت المكتبات

```bash
# تثبيت المكتبات الأساسية
pip install -r requirements.txt

# تثبيت CAMeL Tools (لـ NER)
pip install camel-tools

# تثبيت geopy (لـ Geocoding)
pip install geopy
```

### 3. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات
createdb news_events_db

# تشغيل migrations (إذا كانت موجودة)
alembic upgrade head

# أو تشغيل SQL مباشرة
psql news_events_db < schema.sql
```

### 4. إعداد متغيرات البيئة

```bash
# إنشاء ملف .env
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/news_events_db
OPENAI_API_KEY=your_api_key_here
NOMINATIM_USER_AGENT=news-events-app
EOF
```

### 5. بدء التطبيق

```bash
# بدء FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 7235

# أو باستخدام gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### 6. التحقق من أن المجدول يعمل

```bash
# في سجل التطبيق، يجب أن ترى:
# ✅ Scheduler started successfully
# 📅 Jobs scheduled:
#    - Data Processing: Every 15 minutes
#    - AI Forecast: Every 10 hours
```

---

## 🐛 التصحيح والمشاكل الشائعة

### المشكلة 1: المجدول لا يعمل

**الأعراض:**
```
❌ Scheduler is not running
```

**الحل:**
```python
# في app/main.py
from app.services.scheduler import start_scheduler

@app.on_event("startup")
async def startup_event():
    start_scheduler()  # تأكد من استدعاء هذا
```

### المشكلة 2: خطأ في الاتصال بقاعدة البيانات

**الأعراض:**
```
Error: could not connect to server: Connection refused
```

**الحل:**
```bash
# تحقق من أن PostgreSQL يعمل
sudo systemctl status postgresql

# أو ابدأه
sudo systemctl start postgresql

# تحقق من بيانات الاتصال
psql -U user -d news_events_db -h localhost
```

### المشكلة 3: CAMeL NER لا يعمل

**الأعراض:**
```
CAMeL NER model not available
Falling back to simple NER
```

**الحل:**
```bash
# تثبيت CAMeL Tools بشكل صحيح
pip install camel-tools[full]

# تحميل النموذج
python -c "from camel_tools.ner import NERecognizer; NERecognizer.pretrained()"
```

### المشكلة 4: Nominatim يرفع أخطاء

**الأعراض:**
```
Error: Nominatim service unavailable
```

**الحل:**
```python
# في app/services/geo/geocoder_geopy.py
# أضف معالجة للأخطاء
try:
    location = geolocator.geocode(place, timeout=10)
except Exception as e:
    logging.error(f"Geocoding error: {str(e)}")
    return None

# أو استخدم خدمة geocoding بديلة
# مثل: Google Maps API
```

### المشكلة 5: استخراج الأماكن لا يعمل بشكل صحيح

**الأعراض:**
```
places_detected: 0
locations_upserted: 0
```

**الحل:**
```python
# تحقق من أن النص عربي
text = "غارات على غزة"
print(f"Text: {text}")
print(f"Is Arabic: {any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text)}")

# جرب NER مباشرة
from app.services.nlp.ner_camel import extract_places_ner
places = extract_places_ner(text)
print(f"Places: {places}")
```

### المشكلة 6: استخراج المقاييس لا يعمل

**الأعراض:**
```
metrics_created: 0
```

**الحل:**
```python
# تحقق من أن النص يحتوي على أرقام
text = "أطلقت إسرائيل 3 صواريخ"
print(f"Text: {text}")

# جرب استخراج المقاييس مباشرة
from app.services.extraction.metrics_extractor import extract_metrics
metrics = extract_metrics(text)
print(f"Metrics: {metrics}")

# تحقق من الأنماط (regex)
import re
pattern = r"(?:أطلق|أطلقت).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
matches = re.findall(pattern, text, re.IGNORECASE)
print(f"Matches: {matches}")
```

---

## 📊 المراقبة والتصحيح

### 1. عرض سجلات المجدول

```python
# في app/services/scheduler.py
import logging

logger = logging.getLogger(__name__)

# سيطبع السجلات مثل:
# 🔄 Starting data processing at 2024-01-15T10:00:00
# ✓ Locations extracted: 50 articles processed
# ✓ Metrics extracted: 100 events processed
# ✅ Data processing completed at 2024-01-15T10:15:00
```

### 2. فحص قاعدة البيانات

```sql
-- عدد الأخبار المعالجة
SELECT COUNT(*) FROM raw_news;

-- عدد الأماكن المستخرجة
SELECT COUNT(*) FROM locations;

-- عدد الأحداث
SELECT COUNT(*) FROM news_events;

-- عدد المقاييس
SELECT COUNT(*) FROM event_metrics;

-- آخر 10 أخبار معالجة
SELECT id, title_original, created_at 
FROM raw_news 
ORDER BY created_at DESC 
LIMIT 10;

-- الأماكن الأكثر استخراجاً
SELECT name, country_code, COUNT(*) as count
FROM locations
GROUP BY name, country_code
ORDER BY count DESC
LIMIT 10;

-- أنواع المقاييس الأكثر استخراجاً
SELECT metric_type, COUNT(*) as count, SUM(value) as total
FROM event_metrics
GROUP BY metric_type
ORDER BY count DESC;
```

### 3. اختبار المكونات بشكل منفصل

```python
# اختبار NER
from app.services.nlp.ner_camel import extract_places_ner

text = "غارات على غزة والبحرين"
places = extract_places_ner(text)
print(f"Places: {places}")
# النتيجة المتوقعة: ['غزة', 'البحرين']

# اختبار Geocoding
from app.services.geo.geocoder_geopy import get_geocoder
import asyncio

async def test_geocoding():
    geocoder = get_geocoder()
    geo = await geocoder.geocode_place("البحرين")
    print(f"Geocoding result: {geo}")

asyncio.run(test_geocoding())
# النتيجة المتوقعة: {'name': 'Bahrain', 'country_code': 'BH', ...}

# اختبار استخراج المقاييس
from app.services.extraction.metrics_extractor import extract_metrics

text = "أطلقت إسرائيل 3 صواريخ، مما أسفر عن مقتل 15 شخص"
metrics = extract_metrics(text)
print(f"Metrics: {metrics}")
# النتيجة المتوقعة: [
#   {'metric_type': 'missiles_launched', 'value': 3, ...},
#   {'metric_type': 'killed', 'value': 15, ...}
# ]
```

---

## 🧪 الاختبار

### 1. اختبار وحدة (Unit Tests)

```python
# tests/test_ner.py
import pytest
from app.services.nlp.ner_camel import extract_places_ner

def test_extract_places_simple():
    text = "غارات على غزة"
    places = extract_places_ner(text)
    assert "غزة" in places

def test_extract_places_multiple():
    text = "غارات على غزة والبحرين"
    places = extract_places_ner(text)
    assert "غزة" in places
    assert "البحرين" in places

def test_extract_places_with_prefixes():
    text = "غارات على الامارات والبحرين"
    places = extract_places_ner(text)
    assert "الامارات" in places or "امارات" in places
```

### 2. اختبار التكامل (Integration Tests)

```python
# tests/test_location_processor.py
import pytest
import asyncpg
from app.services.geo.location_processor import process_locations

@pytest.mark.asyncio
async def test_process_locations():
    # إنشاء pool اختبار
    pool = await asyncpg.create_pool(
        dsn="postgresql://user:password@localhost/test_db"
    )
    
    try:
        result = await process_locations(pool, batch_size=10)
        
        assert result["processed_news"] > 0
        assert result["places_detected"] > 0
        assert result["locations_upserted"] > 0
        assert result["events_created"] > 0
    finally:
        await pool.close()
```

### 3. تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# تشغيل اختبار معين
pytest tests/test_ner.py::test_extract_places_simple

# تشغيل مع التفاصيل
pytest -v

# تشغيل مع التغطية
pytest --cov=app
```

---

## 📈 تحسين الأداء

### 1. تحسين استعلامات قاعدة البيانات

```sql
-- إضافة فهارس
CREATE INDEX idx_raw_news_language ON raw_news(language_id);
CREATE INDEX idx_news_events_raw_news ON news_events(raw_news_id);
CREATE INDEX idx_event_metrics_event ON event_metrics(event_id);

-- تحليل الاستعلامات
EXPLAIN ANALYZE
SELECT * FROM news_events ne
JOIN locations l ON ne.location_id = l.id
WHERE ne.raw_news_id = 123;
```

### 2. تحسين معالجة البيانات

```python
# استخدام batch processing
batch_size = 100  # معالجة 100 خبر في كل مرة

# استخدام connection pooling
pool = await asyncpg.create_pool(
    dsn=settings.DATABASE_URL,
    min_size=5,
    max_size=20
)

# استخدام async/await
async def process_batch(pool, batch):
    tasks = [process_item(pool, item) for item in batch]
    await asyncio.gather(*tasks)
```

### 3. تحسين NER و Geocoding

```python
# استخدام cache للنتائج
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_geocoding(place):
    return geocode_place(place)

# استخدام parallel processing
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
futures = [executor.submit(geocode_place, place) for place in places]
results = [f.result() for f in futures]
```

---

## 🔍 التصحيح المتقدم

### 1. تفعيل السجلات التفصيلية

```python
# في app/core/logging.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# أو في .env
LOG_LEVEL=DEBUG
```

### 2. استخدام debugger

```python
# في app/services/geo/location_processor.py
import pdb

async def process_locations(pool, batch_size=20):
    # ...
    for n in news_rows:
        # ضع breakpoint هنا
        pdb.set_trace()
        
        # الآن يمكنك فحص المتغيرات
        # (Pdb) print(n)
        # (Pdb) print(places)
```

### 3. استخدام profiler

```python
# قياس الأداء
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# الكود المراد قياسه
result = await process_locations(pool)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # أعلى 10 دوال
```

---

## 📝 قائمة التحقق (Checklist)

### قبل الإطلاق
- [ ] تثبيت جميع المكتبات
- [ ] إعداد قاعدة البيانات
- [ ] إعداد متغيرات البيئة
- [ ] اختبار الاتصال بقاعدة البيانات
- [ ] اختبار NER و Geocoding
- [ ] تشغيل الاختبارات

### أثناء التشغيل
- [ ] مراقبة السجلات
- [ ] التحقق من أن المجدول يعمل
- [ ] فحص قاعدة البيانات بانتظام
- [ ] مراقبة استهلاك الموارد

### بعد الإطلاق
- [ ] التحقق من البيانات المستخرجة
- [ ] تحليل الأخطاء والمشاكل
- [ ] تحسين الأداء
- [ ] النسخ الاحتياطي المنتظم

---

## 🆘 الدعم والمساعدة

### الأسئلة الشائعة

**س: كيف أتحقق من أن المجدول يعمل؟**
```bash
# افحص السجلات
tail -f app.log | grep "Scheduler"

# أو افحص قاعدة البيانات
SELECT COUNT(*) FROM news_events 
WHERE created_at > NOW() - INTERVAL '15 minutes';
```

**س: كيف أوقف المجدول؟**
```python
from app.services.scheduler import stop_scheduler
stop_scheduler()
```

**س: كيف أعيد تشغيل المجدول؟**
```python
from app.services.scheduler import stop_scheduler, start_scheduler
stop_scheduler()
start_scheduler()
```

**س: كيف أغير معدل المعالجة؟**
```python
# في app/services/scheduler.py
self.scheduler.add_job(
    self._run_data_processing_sync,
    trigger=IntervalTrigger(minutes=30),  # غيّر من 15 إلى 30
)
```

**س: كيف أضيف نوع مقياس جديد؟**
```python
# في app/services/extraction/metrics_extractor.py
PATTERNS = [
    # ... الأنماط الموجودة
    (
        "new_metric_type",
        r"(?:pattern1|pattern2).{0,50}?(\d+)\s*(?:unit1|unit2)"
    ),
]
```

---

## 📞 الاتصال بالدعم

إذا واجهت مشكلة:

1. **تحقق من السجلات** (logs)
2. **اختبر المكونات بشكل منفصل**
3. **ابحث عن الخطأ في قاعدة البيانات**
4. **جرب الحل المقترح أعلاه**
5. **اطلب المساعدة من الفريق**

