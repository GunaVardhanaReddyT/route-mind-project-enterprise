# RouteMind Dashboard

Professional React + TypeScript dashboard for route optimization platform.

## Setup

```bash
npm install
npm run dev
```

Frontend runs on http://localhost:3000

## Features

- Dashboard with real-time metrics
- Interactive map with route visualization (CartoDB Voyager tiles)
- Route optimization with AI explanations
- Replan simulation (traffic jam scenarios)
- Dark mode toggle
- Demo mode (mock data for presentations)
- Cache hit indicators
- Cost tracking (AI usage)

## Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Leaflet (maps)
- Axios (API client)
- Lucide React (icons)

## Design

Enterprise dashboard style inspired by Flipkart/Razorpay internal tools.

Color palette:
- Primary: #0f172a (Slate 900)
- Accent: #3b82f6 (Blue 500)
- Success: #10b981 (Emerald 500)
- Warning: #f59e0b (Amber 500)

## API Endpoints

- GET /api/v1/metrics - System metrics
- POST /api/v1/optimizer/optimize - Optimize routes
- POST /api/v1/optimizer/replan - Replan route
- GET /api/v1/cost-analysis - Cost analysis
