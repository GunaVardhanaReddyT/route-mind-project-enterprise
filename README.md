# RouteMind
## Production-Ready Route Optimization Platform for Indian Logistics

Built for AI Build 2026 Hackathon by Team RouteMind.

## Overview

RouteMind is an enterprise-grade route optimization platform designed specifically for Indian last-mile logistics. It combines classical optimization (Google OR-Tools) with AI-powered explanations (AWS Bedrock) to deliver fast, cost-effective, and compliant routing solutions.

**Key Features:**
- Optimizes routes in <500ms (10 stops, 3 vehicles)
- 50x faster with Redis caching
- 20% better than naive greedy baseline
- 100x cheaper than pure LLM routing
- Professional React + TypeScript dashboard
- Real-time metrics and visualization

## Architecture

### Backend Microservices (Python + FastAPI)

1. **auth-service** (Port 8001)
   - JWT-based authentication
   - User management with PostgreSQL
   - Secure password hashing

2. **routing-service** (Port 8002)
   - Route optimization using OR-Tools
   - Redis caching for 50x speedup
   - Indian constraint enforcement (COD, zone timing, odd-even)
   - Dynamic re-planning
   - AI explanation integration

3. **ai-service** (Port 8003)
   - AWS Bedrock integration (Kimi K2.5)
   - Natural language explanations
   - Cost tracking ($0.001/route)

### Frontend (React + TypeScript + Vite)

- Professional dashboard UI (Flipkart/Razorpay style)
- Interactive maps with CartoDB Voyager tiles
- Real-time metrics and system health
- Dark mode support
- Demo mode for presentations

### Infrastructure

- PostgreSQL (database)
- Redis (caching)
- Docker + Docker Compose
- AWS EC2 deployment ready

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Solve Time (cold) | ~500ms |
| Solve Time (cached) | <100ms |
| Distance Saved vs Baseline | 20% |
| AI Cost per Route | $0.001 |
| Routes Optimized | 2-3 routes |
| Stops per Test | 10 stops |

## Indian Logistics Constraints

1. **COD Limit**: Maximum ₹50,000 cash per vehicle
   - Enforced via OR-Tools capacity dimension
   
2. **Zone Timing**: Truck restrictions 8-10 PM in urban zones
   - Time window constraints per stop

3. **Odd-Even Rule**: Delhi vehicle plate restrictions
   - License plate validation logic

4. **Dynamic Re-planning**: 
   - New pickup requests during active routes
   - Failed delivery handling
   - Real-time route adjustments

## Technology Stack

### Backend
- Python 3.11
- FastAPI (REST API framework)
- Google OR-Tools 9.9 (VRP solver)
- AWS Bedrock (AI explanations)
- PostgreSQL (data storage)
- Redis (caching layer)
- Pydantic (validation)

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Leaflet (maps)
- Axios (API client)
- Lucide React (icons)
- Recharts (charts)

### DevOps
- Docker + Docker Compose
- AWS EC2
- Git

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+ (for frontend)
- AWS Bedrock API key (optional, for AI)

### Backend Setup

```bash
# Clone repository
git clone <repo-url>
cd route-mind-project-enterprise

# Configure environment
cp .env.example .env
# Edit .env and add BEDROCK_API_KEY

# Start services
docker-compose up -d

# Seed database
python seed_simple.py

# Test backend
curl http://localhost:8002/api/v1/metrics
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

## API Endpoints

### Routing Service

- `POST /api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true`
  - Optimize routes for a hub
  - Returns routes, distance, solve time, AI explanation

- `POST /api/v1/optimizer/replan?route_id=1&new_stop_id=5&reason=traffic`
  - Dynamic re-planning
  - Handles traffic jams, new pickups, failed deliveries

- `GET /api/v1/metrics`
  - Performance metrics
  - Business impact (fuel savings, efficiency)
  - System health (CPU, memory)

- `GET /api/v1/cost-analysis`
  - AI cost tracking
  - Savings vs pure LLM approach

## Testing

See `COMPLETE_TEST_GUIDE.md` for full testing instructions.

Quick test:

```bash
# Optimize routes
curl -X POST "http://localhost:8002/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true"

# Test cache (run again)
curl -X POST "http://localhost:8002/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true"

# Check metrics
curl http://localhost:8002/api/v1/metrics
```

## Deployment (AWS EC2)

See `frontend/DEPLOYMENT.md` for detailed deployment guide.

Quick deployment:

```bash
# SSH to EC2
ssh ubuntu@<ec2-ip>

# Setup backend
git clone <repo>
cd route-mind-project-enterprise
docker-compose up -d
python seed_simple.py

# Setup frontend
./scripts/setup_frontend_ec2.sh
cd frontend && npm run dev
```

Open ports in Security Group:
- 8001 (auth-service)
- 8002 (routing-service)
- 8003 (ai-service)
- 3000 (frontend)

## Project Structure

```
route-mind-project-enterprise/
├── services/
│   ├── auth-service/          # Authentication service
│   ├── routing-service/       # Route optimization service
│   └── ai-service/            # AI explanation service
├── frontend/                  # React + TypeScript dashboard
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Dashboard, Routes, Settings
│   │   ├── lib/               # API client, utilities
│   │   └── context/           # React context
│   └── package.json
├── scripts/                   # Setup and seed scripts
├── docker-compose.yml         # Service orchestration
├── seed_simple.py            # Database seeding
└── README.md                 # This file
```

## Features

### Optimization Engine
- Vehicle Routing Problem (VRP) solver
- Capacity constraints (COD limits)
- Time windows (zone restrictions)
- Distance matrix optimization (vectorized NumPy)
- Adaptive search parameters

### Caching Strategy
- Redis-based result caching
- Cache key: hub_id + sorted stop IDs
- 50x performance improvement on cache hits
- Automatic cache invalidation

### AI Integration
- AWS Bedrock API (Kimi K2.5 model)
- Natural language route explanations
- Cost tracking per request
- Optional AI usage (optimization works without it)

### Frontend Dashboard
- Real-time metrics display
- Interactive route visualization
- Route selection and highlighting
- Traffic jam simulation
- Dark mode toggle
- Demo mode (mock data)
- Cache hit indicators

## Cost Analysis

| Approach | Cost per Route | Speed |
|----------|----------------|-------|
| Pure LLM | $0.10 | Slow |
| OR-Tools + LLM | $0.001 | Fast |
| Manual Planning | $35 | Very Slow |

**RouteMind is 100x cheaper than pure LLM routing.**

## Business Impact

Based on test data (10 stops, 3 vehicles):

- Distance Saved: 97km vs baseline
- Fuel Saved: ₹973 per optimization
- Efficiency Gain: 20% better than greedy
- Time to Solution: <500ms

## Datasets Used

1. **Amazon Last Mile Routing Challenge**
   - Real operational data
   - 6,000+ historical routes
   - Used for algorithm validation

2. **OpenStreetMap via OSRM**
   - Real road networks
   - Accurate distance calculations
   - Future integration planned

3. **OR-Tools VRP Benchmarks**
   - Standard test cases
   - Performance comparison

## Future Enhancements

- Real-time traffic integration (OSRM)
- Multi-day route planning
- Driver app integration
- Fleet optimization
- Predictive analytics
- Mobile dashboard

## Team

Team RouteMind - AI Build 2026

## License

MIT License
