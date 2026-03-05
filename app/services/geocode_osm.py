"""
=============================================================================
OpenStreetMap Geocoding Service
=============================================================================
يحول أسماء الأماكن إلى إحداثيات جغرافية باستخدام Nominatim API.

Nominatim هو خدمة مجانية من OpenStreetMap للبحث الجغرافي.
تحتاج إلى User-Agent صحيح وتأخير بين الطلبات (rate limiting).
=============================================================================
"""

import httpx
from typing import Optional, Dict


# ============================================================================
# Configuration
# ============================================================================
# رابط API الخاص بـ Nominatim
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


# ============================================================================
# Main Geocoding Function
# ============================================================================

async def geocode_nominatim(client: httpx.AsyncClient, q: str) -> Optional[Dict]:
    """
    البحث عن مكان باستخدام Nominatim API.
    
    Args:
        client: httpx async client
        q: اسم المكان المراد البحث عنه
    
    Returns:
        dict يحتوي على:
        - lat: خط العرض
        - lng: خط الطول
        - country_code: كود الدولة (مثل 'SY', 'IQ')
        - display_name: الاسم الكامل للمكان
        - osm_id: معرّف OpenStreetMap
        - osm_type: نوع الكيان (node, way, relation)
        
        أو None إذا لم يجد النتيجة أو حدث خطأ
    """
    
    # ============================================================================
    # Prepare Request
    # ============================================================================
    params = {
        "q": q,                    # اسم المكان
        "format": "json",           # صيغة الرد
        "limit": 1,                 # نتيجة واحدة فقط
        "addressdetails": 1,        # تفاصيل العنوان
    }

    # ============================================================================
    # Make Request
    # ============================================================================
    try:
        r = await client.get(NOMINATIM_URL, params=params, timeout=30)
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        # 403/429/5xx… خليه يمرّ بدون ما يوقع البروسس
        # (قد يكون الـ API مشغول أو بلوك)
        return None
    except httpx.RequestError:
        # خطأ في الاتصال
        return None

    # ============================================================================
    # Parse Response
    # ============================================================================
    data = r.json()
    if not data:
        return None

    item = data[0]
    address = item.get("address", {}) or {}
    cc = (address.get("country_code") or "").upper()

    # تأكد من وجود country_code
    if not cc:
        return None
    
    # ============================================================================
    # Return Structured Data
    # ============================================================================
    return {
        "lat": float(item["lat"]),
        "lng": float(item["lon"]),
        "country_code": cc,
        "display_name": item.get("display_name"),
        "osm_id": int(item["osm_id"]) if item.get("osm_id") else None,
        "osm_type": item.get("osm_type"),
    }
