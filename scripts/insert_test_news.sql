-- ============================================================================
-- Insert Test News Articles for Local Testing
-- ============================================================================
-- هذا السكريبت يدرج أخبار تجريبية من مصادر مختلفة
-- بما فيها المصدر 41 (BBC Arabic) والمصادر المستثناة 17 و 18
-- ============================================================================

-- تأكد من وجود اللغة العربية
INSERT INTO languages (code, name) 
VALUES ('ar', 'Arabic') 
ON CONFLICT (code) DO NOTHING;

-- الحصول على ID اللغة العربية
-- SELECT id FROM languages WHERE code = 'ar';

-- ============================================================================
-- 1. أخبار من مصدر 41 (BBC Arabic) - يجب أن تنشئ events
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  41,
  'وزير الدفاع الإسرائيلي: نتوغل في الأراضي اللبنانية للسيطرة على خط دفاع متقدم',
  'شاهد معنا بي بي سي نيوز عربي على موقعنا وعلى قناتنا على يوتيوب. وزير الدفاع الإسرائيلي أعلن اليوم عن عملية عسكرية جديدة في الأراضي اللبنانية. قال الوزير إن الهدف هو السيطرة على خط دفاع متقدم في المنطقة الحدودية. شارك في العملية آلاف الجنود والمعدات العسكرية الثقيلة. وأضاف أن العملية ستستمر حتى تحقيق الأهداف المرسومة. ردت السلطات اللبنانية بشكل حاد على هذه التصريحات.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '2 hours',
  NOW() - INTERVAL '2 hours',
  'https://x.com/BBCArabic/status/2036398263062925717'
);

-- ============================================================================
-- 2. أخبار من مصدر 41 (BBC Arabic) - خبر آخر عن سوريا
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  41,
  'تطورات جديدة في دمشق: اجتماعات سياسية مهمة',
  'عقدت قيادات سياسية سورية اجتماعات مهمة في دمشق اليوم. حضر الاجتماع ممثلون من عدة دول عربية وأجنبية. ناقشوا الأوضاع الأمنية والاقتصادية في سوريا والمنطقة. أكدوا على أهمية الاستقرار والسلام. وأشاروا إلى ضرورة التعاون الإقليمي لحل الأزمات.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '1 hour',
  NOW() - INTERVAL '1 hour',
  'https://x.com/BBCArabic/status/2036398263062925718'
);

-- ============================================================================
-- 3. أخبار من مصدر 7 (مصدر عادي) - يجب أن تنشئ events
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  7,
  'أنباء عن تطورات عسكرية في غزة',
  'أفادت مصادر محلية عن تطورات عسكرية جديدة في قطاع غزة. قالت المصادر إن هناك تحركات عسكرية متزايدة في المنطقة. وأشارت إلى أن الوضع الإنساني يزداد سوءاً. طالبت المنظمات الدولية بتدخل فوري لإيقاف العنف.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '30 minutes',
  NOW() - INTERVAL '30 minutes',
  'https://example.com/news/7'
);

-- ============================================================================
-- 4. أخبار من مصدر 17 (مصدر النهار - يجب استثناؤه) - لا يجب أن تنشئ events
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  17,
  'أخبار من بيروت والعراق',
  'أخبار من بيروت والعراق وفلسطين. هذا الخبر من مصدر 17 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '20 minutes',
  NOW() - INTERVAL '20 minutes',
  'https://example.com/news/17'
);

-- ============================================================================
-- 5. أخبار من مصدر 18 (مصدر النهار - يجب استثناؤه) - لا يجب أن تنشئ events
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  18,
  'أخبار من إيران والسعودية',
  'أخبار من إيران والسعودية والإمارات. هذا الخبر من مصدر 18 الذي يجب استثناؤه. لا يجب أن ينشئ events حتى لو كان يحتوي على أسماء مواقع.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '15 minutes',
  NOW() - INTERVAL '15 minutes',
  'https://example.com/news/18'
);

-- ============================================================================
-- 6. أخبار من مصدر 41 (BBC Arabic) - خبر عن فلسطين
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  41,
  'تطورات في القدس والضفة الغربية',
  'شهدت القدس والضفة الغربية تطورات جديدة اليوم. أفادت مصادر محلية عن اشتباكات في عدة مناطق. وقالت إن الوضع الأمني متوتر جداً. طالبت المنظمات الإنسانية بوقف فوري للعنف.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '10 minutes',
  NOW() - INTERVAL '10 minutes',
  'https://x.com/BBCArabic/status/2036398263062925719'
);

-- ============================================================================
-- 7. أخبار من مصدر 41 (BBC Arabic) - خبر عن العراق
-- ============================================================================
INSERT INTO raw_news 
(source_id, title_original, content_original, language_id, published_at, fetched_at, url)
VALUES 
(
  41,
  'بغداد تشهد احتجاجات واسعة',
  'شهدت العاصمة العراقية بغداد احتجاجات واسعة اليوم. خرج آلاف المتظاهرين إلى الشوارع. طالبوا بتحسين الخدمات والقضاء على الفساد. أغلقت السلطات عدة طرق رئيسية في بغداد.',
  (SELECT id FROM languages WHERE code = 'ar'),
  NOW() - INTERVAL '5 minutes',
  NOW() - INTERVAL '5 minutes',
  'https://x.com/BBCArabic/status/2036398263062925720'
);

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- تحقق من الأخبار المدرجة
-- SELECT id, source_id, title_original, published_at FROM raw_news 
-- WHERE source_id IN (7, 17, 18, 41) 
-- ORDER BY published_at DESC;

-- تحقق من عدد الأخبار من كل مصدر
-- SELECT source_id, COUNT(*) as count FROM raw_news 
-- WHERE source_id IN (7, 17, 18, 41) 
-- GROUP BY source_id;

-- تحقق من الأحداث المنشأة (يجب أن تكون من المصادر 7 و 41 فقط)
-- SELECT ne.id, ne.raw_news_id, ne.place_name, rn.source_id 
-- FROM news_events ne
-- JOIN raw_news rn ON ne.raw_news_id = rn.id
-- WHERE rn.source_id IN (7, 17, 18, 41)
-- ORDER BY ne.raw_news_id DESC;

-- تحقق من عدم وجود أحداث من المصادر 17 و 18
-- SELECT COUNT(*) as events_from_excluded_sources 
-- FROM news_events ne
-- JOIN raw_news rn ON ne.raw_news_id = rn.id
-- WHERE rn.source_id IN (17, 18);
-- (يجب أن تكون النتيجة 0)
