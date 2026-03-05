# GeoNews AI - Frontend Architecture

## 🎯 Project Overview
**GeoNews AI** is an Interactive War Intelligence Platform that provides real-time analysis, geospatial visualization, and AI-powered predictions for war-related news events.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── [locale]/              # Internationalized routes (en/ar)
│   │   ├── layout.tsx         # Root layout with i18n
│   │   └── page.tsx           # Main dashboard page
│   ├── globals.css            # Global styles
│   └── layout.tsx             # Base layout
├── components/
│   ├── dashboard/             # Main dashboard components
│   │   ├── analytics-section.tsx    # Statistics & charts
│   │   ├── language-switcher.tsx    # Language toggle
│   │   ├── live-stream.tsx          # YouTube live stream
│   │   ├── map-component.tsx        # Leaflet map
│   │   ├── map-section.tsx          # Map wrapper
│   │   ├── metrics-overview.tsx     # Top metrics cards
│   │   ├── news-sidebar.tsx         # Breaking news feed
│   │   ├── predictions-section.tsx  # AI predictions
│   │   └── index.ts                 # Barrel exports
│   └── ui/                    # Reusable UI components
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── scroll-area.tsx
│       ├── select.tsx
│       ├── separator.tsx
│       └── tabs.tsx
├── lib/
│   ├── api-client.ts          # Axios instance
│   ├── api-services.ts        # API functions
│   ├── country-names.ts       # Country translations
│   ├── metric-names.ts        # Metric translations
│   └── utils.ts               # Utility functions
├── messages/
│   ├── ar.json                # Arabic translations
│   └── en.json                # English translations
├── types/
│   └── index.ts               # TypeScript types
└── i18n/
    └── request.ts             # i18n configuration
```

## 🧩 Component Architecture

### Reusable Components
All dashboard components are exported through a barrel file (`components/dashboard/index.ts`) for clean imports:

```typescript
import {
  AnalyticsSection,
  LanguageSwitcher,
  LiveStream,
  MapSection,
  MetricsOverview,
  NewsSidebar,
  PredictionsSection,
} from '@/components/dashboard';
```

### Component Responsibilities

#### 1. **MetricsOverview**
- Displays 4 key metrics cards
- Real-time data from backend API
- Bilingual support (AR/EN)

#### 2. **LiveStream**
- Embeds YouTube live stream (Al Jazeera)
- Auto-play with mute
- Responsive 16:9 aspect ratio

#### 3. **MapSection**
- Interactive Leaflet map
- Custom markers sized by event count
- Popups with location details
- Dark theme with CartoDB tiles

#### 4. **NewsSidebar**
- Breaking news feed
- Auto-refresh every 60 seconds
- Event and metric badges
- Scrollable with custom styling

#### 5. **PredictionsSection**
- AI-powered forecasts (OpenAI GPT-4o-mini)
- Trend analysis
- Risk assessment
- 7-day predictions

#### 6. **AnalyticsSection**
- Top countries by activity
- Recent activity timeline (14 days)
- Top metrics with country breakdown
- Hot locations (unique countries)
- Oil & gold price chart

## 🌐 Internationalization (i18n)

### Supported Languages
- **English** (`/en`)
- **Arabic** (`/ar`) - RTL support

### Translation Files
- `messages/en.json` - English translations
- `messages/ar.json` - Arabic translations

### Usage
```typescript
import { useTranslations, useLocale } from 'next-intl';

const t = useTranslations('app');
const locale = useLocale();

<h1>{t('title')}</h1>
```

## 🎨 Design System

### Color Palette
- **Background**: Slate 950/900 gradient
- **Cards**: Slate 800/50 with backdrop blur
- **Borders**: Slate 700
- **Primary**: Red 500 (war theme)
- **Secondary**: Purple 500 (AI features)
- **Success**: Green 500
- **Warning**: Yellow 500

### Typography
- **Sans**: Geist Sans
- **Mono**: Geist Mono
- **Arabic**: Cairo

### Dark War Theme
- High contrast colors
- Red accents for alerts
- Glowing effects on live indicators
- Smooth transitions and animations

## 📡 API Integration

### Backend URL
- Development: `http://localhost:8000`
- Production: Configure in `.env.local`

### API Services (`lib/api-services.ts`)
```typescript
fetchLatestNews(limit: number)
fetchLocations()
fetchMetrics()
fetchTopCountries()
fetchRecentActivity(days: number)
fetchTopMetrics()
fetchTopMetricsByCountry()
fetchHotLocations(limit: number)
fetchOilGoldPrices()
fetchAIIntelligenceForecast(days: number)
fetchAITrendAnalysis()
```

### React Query
- Automatic caching
- Background refetching
- Error handling
- Loading states

## 🗺️ Map Implementation

### Technology
- **Leaflet** (free, no API key required)
- **CartoDB Dark Matter** tiles
- Custom markers with event counts
- Hover effects and popups

### Features
- Dynamic marker sizing based on event count
- Color-coded by activity level
- Bilingual popups
- Auto-fit bounds to show all locations

## 🤖 AI Features

### OpenAI Integration
- Model: `gpt-4o-mini`
- Intelligence forecasting
- Trend analysis
- Risk assessment

### Predictions Display
- 7-day event forecasts
- Confidence levels
- Key influencing factors
- Highest/lowest risk days

## 📊 Analytics Features

### Top Countries
- Event count per country
- Average and maximum values
- Sorted by activity

### Recent Activity Timeline
- 14-day historical data
- Line chart visualization
- Event count trends

### Top Metrics
- Most frequent metrics
- Country breakdown per metric
- Occurrence counts

### Hot Locations
- 8 unique countries
- Prioritizes Arab countries and key players
- Event count per location

### Market Data
- Oil prices (7-day trend)
- Gold prices
- Percentage changes with color coding
- SVG line chart with gradients

## 🚀 Performance Optimizations

### Code Splitting
- Dynamic imports for heavy components
- Lazy loading for map component

### Caching
- React Query for API responses
- Next.js automatic code splitting

### SSR Considerations
- Client-side only components marked with `'use client'`
- Dynamic imports for browser-only libraries (Leaflet)

## 🔧 Development

### Prerequisites
```bash
Node.js 18+
npm or yarn
```

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Build
```bash
npm run build
npm start
```

### Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📱 Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Grid Layout
- Mobile: Single column
- Desktop: 2-column grid for main sections
- Full-width for analytics

## 🎯 Best Practices

### Component Design
- Single responsibility principle
- Reusable and composable
- TypeScript for type safety
- Proper error handling

### State Management
- React Query for server state
- React hooks for local state
- No global state library needed

### Code Organization
- Barrel exports for clean imports
- Consistent file naming
- Logical folder structure

### Accessibility
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- High contrast colors

## 🔐 Security

### API Calls
- CORS configured on backend
- No sensitive data in frontend
- Environment variables for configuration

### Content Security
- No inline scripts
- Trusted external sources only (YouTube, CartoDB)

## 📈 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] User authentication
- [ ] Customizable dashboards
- [ ] Export data functionality
- [ ] Mobile app version
- [ ] Advanced filtering options
- [ ] Historical data comparison
- [ ] Notification system

## 📝 License
Proprietary - GeoNews AI Platform

## 👥 Contributors
Built with ❤️ for war intelligence analysis
