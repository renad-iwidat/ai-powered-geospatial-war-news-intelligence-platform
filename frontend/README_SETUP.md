# GeoNews AI Frontend Setup

## Prerequisites
- Node.js 20+ installed
- Backend API running on http://localhost:8000
- Mapbox account (for map functionality)

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
Create `.env.local` file with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

To get a Mapbox token:
- Go to https://account.mapbox.com/
- Sign up or log in
- Go to "Access tokens"
- Create a new token or copy the default public token

## Running the Application

### Development Mode
```bash
npm run dev
```
The app will be available at http://localhost:3000

### Production Build
```bash
npm run build
npm start
```

## Features

### Dashboard Layout
- **News Sidebar** (Left): Latest 30 news articles with real-time updates
- **Interactive Map** (Top Right): Event locations with markers and popups
- **Analytics Section** (Bottom Left): Statistics, charts, and country data
- **Predictions Section** (Bottom Right): Placeholder for future AI predictions

### Language Support
- English (default): http://localhost:3000/en
- Arabic (RTL): http://localhost:3000/ar
- Switch languages using the button in the header

### API Integration
All data is fetched from the FastAPI backend:
- `/api/v1/news-articles` - Latest news
- `/api/v1/geographic-locations` - Event locations
- `/api/v1/analytics/overview` - Statistics overview
- `/api/v1/analytics/by-country` - Country statistics
- `/api/v1/analytics/by-date` - Timeline data

### Auto-Refresh
News data refreshes automatically every 60 seconds.

## Project Structure
```
frontend/
├── app/
│   ├── [locale]/          # Locale-based routing
│   │   ├── layout.tsx     # Layout with i18n
│   │   └── page.tsx       # Main dashboard
│   ├── globals.css        # Global styles with RTL support
│   └── layout.tsx         # Root layout
├── components/
│   ├── dashboard/         # Dashboard components
│   │   ├── news-sidebar.tsx
│   │   ├── map-section.tsx
│   │   ├── analytics-section.tsx
│   │   ├── predictions-section.tsx
│   │   └── language-switcher.tsx
│   └── ui/                # shadcn/ui components
├── lib/
│   ├── api-client.ts      # Axios configuration
│   ├── api-services.ts    # API service functions
│   └── utils.ts           # Utility functions
├── messages/              # i18n translations
│   ├── ar.json
│   └── en.json
├── types/
│   └── index.ts           # TypeScript types
└── i18n/
    └── request.ts         # i18n configuration
```

## Technologies Used
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Mapbox GL JS** - Interactive maps
- **Recharts** - Data visualization
- **React Query** - Data fetching and caching
- **next-intl** - Internationalization
- **Axios** - HTTP client

## Troubleshooting

### Map not showing
- Check if NEXT_PUBLIC_MAPBOX_TOKEN is set correctly
- Verify the token is valid at https://account.mapbox.com/

### API connection errors
- Ensure backend is running on http://localhost:8000
- Check NEXT_PUBLIC_API_URL in .env.local
- Verify CORS is enabled in backend

### Build errors
- Clear .next folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 20+)
