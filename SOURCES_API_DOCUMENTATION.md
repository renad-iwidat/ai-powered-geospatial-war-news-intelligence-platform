# News API – Frontend Documentation

# 1. Get All News Sources

**Endpoint**

```
GET /sources
```

**Query Parameters**

| Parameter | Type | Description |
|---|---|---|
| active_only | boolean | Return only active sources |

**Examples**

```bash
curl "http://localhost:8000/api/v1/sources"
```

```bash
curl "http://localhost:8000/api/v1/sources?active_only=true"
```

**Response**

```json
{
  "items": [
    {
      "id": 17,
      "name": "Annahar",
      "url": "https://www.annahar.com/rss",
      "is_active": true,
      "source_type_name": "RSS Feed",
      "articles_count": 45
    }
  ],
  "total": 16,
  "active_count": 11,
  "inactive_count": 5
}
```

---

# 2. Get Source Details

**Endpoint**

```
GET /sources/{source_id}
```

**Example**

```bash
curl "http://localhost:8000/api/v1/sources/17"
```

**Response**

```json
{
  "id": 17,
  "name": "Annahar",
  "url": "https://www.annahar.com/rss",
  "is_active": true,
  "source_type_name": "RSS Feed",
  "created_at": "2026-03-04T21:10:05",
  "articles_count": 45
}
```

---

# 3. Get Source Status

**Endpoint**

```
GET /sources/{source_id}/status
```

**Example**

```bash
curl "http://localhost:8000/api/v1/sources/17/status"
```

**Response**

```json
{
  "id": 17,
  "name": "Annahar",
  "is_active": true,
  "status": "Active",
  "articles_count": 45
}
```

---

# 4. Get Active Sources

**Endpoint**

```
GET /sources/status/active
```

Returns only active sources.

---

# 5. Get Inactive Sources

**Endpoint**

```
GET /sources/status/inactive
```

Returns only inactive sources.

---

# 6. Get News Articles by Source

**Endpoint**

```
GET /news-articles/by-source/{source_id}
```

**Path Parameter**

| Parameter | Description |
|---|---|
| source_id | Source ID |

---

## Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| limit | number | 50 | Number of articles returned |
| offset | number | 0 | Pagination offset |
| search | string | — | Search in title or content |

---

# Examples

### Get news from a specific source

```bash
curl "http://localhost:8000/api/v1/news-articles/by-source/17"
```

### Get news with search

```bash
curl "http://localhost:8000/api/v1/news-articles/by-source/17?search=الحرب&limit=20"
```

### Pagination example

```bash
curl "http://localhost:8000/api/v1/news-articles/by-source/17?limit=50&offset=50"
```

---

# Response

```json
{
  "items": [
    {
      "id": 1,
      "title": "News Title",
      "content": "Full article content",
      "url": "https://example.com/news/1",
      "source_name": "Annahar",
      "source_id": 17,
      "language_code": "ar",
      "published_at": "2026-03-12T10:30:00",
      "fetched_at": "2026-03-12T11:00:00"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "source_id": 17,
  "source_name": "Annahar"
}
```

---

# Frontend Notes

- Articles are returned **sorted by newest first**.
- Use **limit** and **offset** for pagination.
- **search** filters results by title and content.
- Supported languages may include: `ar`, `en`, `he`.