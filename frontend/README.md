# GeoNews AI - Interactive War Intelligence Platform

![Status](https://img.shields.io/badge/status-active-success.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black)
![React](https://img.shields.io/badge/React-19.2.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)

## 🎯 Overview

**GeoNews AI** is a comprehensive war intelligence platform that provides real-time analysis, geospatial visualization, and AI-powered predictions for Iran war-related news events.

## ✨ Key Features

- 📊 **Real-Time Intelligence Dashboard**
- 🤖 **AI-Powered Predictions** (OpenAI GPT-4o-mini)
- 🗺️ **Interactive Geospatial Map** (Leaflet)
- 📺 **Live News Stream** (Al Jazeera)
- 📈 **Advanced Analytics & Charts**
- 🌐 **Bilingual Support** (English/Arabic with RTL)

## 🚀 Quick Start

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```

Visit:
- English: http://localhost:3000/en
- Arabic: http://localhost:3000/ar

### Production
```bash
npm run build
npm start
```

## 📁 Structure

```
frontend/
├── app/[locale]/              # Internationalized routes
├── components/dashboard/      # Main components
├── lib/                       # API & utilities
├── messages/                  # Translations
└── types/                     # TypeScript types
```

## 🧩 Components

All components are reusable and exported through barrel files:

```typescript
import {
  AnalyticsSection,
  LiveStream,
  MapSection,
  MetricsOverview,
  NewsSidebar,
  PredictionsSection,
} from '@/components/dashboard';
```

## 📡 API Integration

Backend: `http://localhost:8000`

Key endpoints:
- `/api/v1/news/latest`
- `/api/v1/geographic-locations`
- `/api/v1/predictions/ai-intelligence-forecast`
- `/api/v1/analytics/*`

## 🗺️ Map Technology

- **Leaflet** (free, no API key)
- **CartoDB Dark Matter** tiles
- Custom markers sized by event count
- Interactive popups with bilingual support

## 🤖 AI Features

- **Model**: OpenAI GPT-4o-mini
- 7-day event forecasts
- Trend analysis (escalating/stable/de-escalating)
- Risk assessment (critical/high/medium/low)

## 🌐 Languages

- **English** (`/en`)
- **Arabic** (`/ar`) with RTL support

## 📦 Tech Stack

- Next.js 16.1.6
- React 19.2.3
- TypeScript 5
- Tailwind CSS 4
- React Query
- Leaflet
- next-intl

## 📚 Documentation

- [Architecture Guide](./ARCHITECTURE.md)
- [Setup Instructions](./README_SETUP.md)

## 🐛 Troubleshooting

### Map Not Displaying
```bash
rm -rf .next
npm run dev
```

### API Issues
- Verify backend is running on port 8000
- Check CORS configuration

## 📝 License

Proprietary - GeoNews AI Platform

---

**Built with ❤️ for war intelligence analysis**
