# Instagram Integration - Frontend Guide

## استخدام الـ API من الـ Frontend

### 1. جلب آخر 10 ريلز/بوست

```typescript
// app/lib/api-services.ts أو في أي component

async function getInstagramFeed(limit: number = 10) {
  try {
    const response = await fetch(
      `/api/v1/instagram/feed?limit=${limit}&include_insights=false`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch Instagram feed');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching Instagram feed:', error);
    throw error;
  }
}
```

### 2. جلب الريلز فقط

```typescript
async function getInstagramReels(limit: number = 10) {
  const response = await fetch(`/api/v1/instagram/reels?limit=${limit}`);
  return response.json();
}
```

### 3. جلب معلومات الحساب

```typescript
async function getInstagramAccount() {
  const response = await fetch('/api/v1/instagram/account');
  return response.json();
}
```

## مثال Component

```typescript
'use client';

import { useEffect, useState } from 'react';

interface InstagramMedia {
  id: string;
  caption: string;
  media_type: string;
  media_url: string;
  permalink: string;
  timestamp: string;
  like_count: number;
  comments_count: number;
}

interface InstagramFeed {
  account: {
    name: string;
    followers_count: number;
    profile_picture_url: string;
  };
  media: InstagramMedia[];
  cached: boolean;
  next_update_in_minutes: number;
}

export function InstagramFeedComponent() {
  const [feed, setFeed] = useState<InstagramFeed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const response = await fetch('/api/v1/instagram/feed?limit=10');
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setFeed(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchFeed();
    
    // Refresh every 15 minutes
    const interval = setInterval(fetchFeed, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading Instagram feed...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!feed) return <div>No data</div>;

  return (
    <div className="instagram-feed">
      <div className="account-info">
        <img 
          src={feed.account.profile_picture_url} 
          alt={feed.account.name}
          className="profile-pic"
        />
        <h2>{feed.account.name}</h2>
        <p>{feed.account.followers_count.toLocaleString()} followers</p>
      </div>

      <div className="media-grid">
        {feed.media.map((media) => (
          <div key={media.id} className="media-item">
            <a href={media.permalink} target="_blank" rel="noopener noreferrer">
              <img 
                src={media.media_url} 
                alt={media.caption}
                className="media-image"
              />
              <div className="media-overlay">
                <span className="likes">❤️ {media.like_count}</span>
                <span className="comments">💬 {media.comments_count}</span>
              </div>
            </a>
            {media.caption && (
              <p className="caption">{media.caption.substring(0, 100)}...</p>
            )}
          </div>
        ))}
      </div>

      <div className="cache-info">
        {feed.cached ? (
          <p>📦 Cached data (updates in {feed.next_update_in_minutes} min)</p>
        ) : (
          <p>🔄 Fresh data</p>
        )}
      </div>
    </div>
  );
}
```

## CSS Styling

```css
.instagram-feed {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.account-info {
  text-align: center;
  margin-bottom: 40px;
}

.profile-pic {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.media-item {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  background: #f0f0f0;
}

.media-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.media-item:hover .media-image {
  transform: scale(1.05);
}

.media-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  font-weight: bold;
}

.media-item:hover .media-overlay {
  opacity: 1;
}

.caption {
  padding: 10px;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cache-info {
  text-align: center;
  color: #666;
  font-size: 12px;
}
```

## React Hook للـ Instagram Feed

```typescript
// hooks/useInstagramFeed.ts

import { useState, useEffect } from 'react';

export function useInstagramFeed(limit: number = 10) {
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const response = await fetch(
          `/api/v1/instagram/feed?limit=${limit}`
        );
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setFeed(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchFeed();
    const interval = setInterval(fetchFeed, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [limit]);

  return { feed, loading, error };
}

// Usage in component:
// const { feed, loading, error } = useInstagramFeed(10);
```

## API Response Types

```typescript
interface InstagramMedia {
  id: string;
  caption: string | null;
  media_type: 'REELS' | 'VIDEO' | 'IMAGE' | 'CAROUSEL';
  media_url: string | null;
  permalink: string | null;
  timestamp: string;
  like_count: number | null;
  comments_count: number | null;
  insights?: {
    impressions: number | null;
    reach: number | null;
    engagement: number | null;
  };
}

interface InstagramAccount {
  id: string;
  name: string | null;
  biography: string | null;
  followers_count: number | null;
  follows_count: number | null;
  media_count: number | null;
  profile_picture_url: string | null;
  website: string | null;
}

interface InstagramFeedResponse {
  account: InstagramAccount;
  media: InstagramMedia[];
  total_count: number;
  last_updated: string;
  next_update_in_minutes: number;
  cached: boolean;
}
```

## Error Handling

```typescript
async function fetchInstagramFeedSafe(limit: number = 10) {
  try {
    const response = await fetch(
      `/api/v1/instagram/feed?limit=${limit}`
    );

    if (response.status === 503) {
      throw new Error('Instagram service unavailable. Check credentials.');
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch Instagram feed:', error);
    // Return fallback data or show error message
    return null;
  }
}
```

## Performance Tips

1. **Caching**: البيانات تُخزن لمدة 15 دقيقة، لا تحتاج لـ refresh متكرر
2. **Lazy Loading**: حمّل الصور بـ lazy loading
3. **Image Optimization**: استخدم Next.js Image component
4. **Pagination**: إذا كنت تريد أكثر من 10 items، استخدم `limit` parameter

```typescript
// استخدام Next.js Image component
import Image from 'next/image';

<Image
  src={media.media_url}
  alt={media.caption}
  width={250}
  height={250}
  loading="lazy"
/>
```
