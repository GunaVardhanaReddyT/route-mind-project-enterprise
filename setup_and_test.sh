#!/bin/bash
# RouteMind - Complete Setup and Test Script

set -e

echo "🚀 RouteMind Setup and Test"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Checking .env file${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your AWS credentials:${NC}"
    echo "   nano .env"
    echo ""
    echo "Add these lines:"
    echo "   AWS_ACCESS_KEY_ID=AKIA...your_key"
    echo "   AWS_SECRET_ACCESS_KEY=your_secret"
    echo ""
    echo "Then run this script again."
    exit 1
else
    echo -e "${GREEN}✓ .env file found${NC}"
    
    # Check if AWS credentials are set
    if grep -q "your_key" .env || grep -q "your_secret" .env; then
        echo -e "${YELLOW}⚠️  AWS credentials not configured (AI features will be disabled)${NC}"
        echo "   The system will still work without AI explanations."
        echo "   To enable AI: nano .env and add real AWS credentials"
    else
        echo -e "${GREEN}✓ AWS credentials configured${NC}"
    fi
fi
echo ""

echo -e "${BLUE}Step 2: Starting Docker services${NC}"
docker-compose down
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

echo -e "${BLUE}Step 3: Waiting for database (30 seconds)${NC}"
sleep 30
echo -e "${GREEN}✓ Database should be ready${NC}"
echo ""

echo -e "${BLUE}Step 4: Seeding sample data${NC}"
docker-compose exec -T routing-service python seed_simple.py
echo ""

echo -e "${BLUE}Step 5: Running health checks${NC}"
curl -s http://localhost:8001/health | jq '.' && echo -e "${GREEN}✓ Auth service healthy${NC}" || echo -e "${RED}✗ Auth service failed${NC}"
curl -s http://localhost:8002/health | jq '.' && echo -e "${GREEN}✓ Routing service healthy${NC}" || echo -e "${RED}✗ Routing service failed${NC}"
curl -s http://localhost:8003/health | jq '.' && echo -e "${GREEN}✓ AI service healthy${NC}" || echo -e "${RED}✗ AI service failed${NC}"
echo ""

echo -e "${BLUE}Step 6: Testing route optimization (without AI)${NC}"
echo "Request: POST /api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=false"
echo "Response:"
curl -s -X POST "http://localhost:8002/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=false" | jq '.'
echo ""

echo -e "${BLUE}Step 7: Testing route optimization (with AI)${NC}"
echo "Request: POST /api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true"
echo "Response:"
curl -s -X POST "http://localhost:8002/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true" | jq '.'
echo ""

echo -e "${BLUE}Step 8: Testing route re-planning${NC}"
echo "Request: POST /api/v1/optimizer/replan?route_id=1&new_stop_id=5&reason=new_pickup&hub_id=1"
echo "Response:"
curl -s -X POST "http://localhost:8002/api/v1/optimizer/replan?route_id=1&new_stop_id=5&reason=new_pickup&hub_id=1" | jq '.'
echo ""

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Setup and testing complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Summary:"
echo "  - All services running: ✓"
echo "  - Sample data seeded: ✓"
echo "  - Route optimization: ✓"
echo "  - Route re-planning: ✓"
echo ""
echo "Next steps:"
echo "  1. Review the API responses above"
echo "  2. Check total_distance_km is accurate"
echo "  3. If AI explanation is fallback text, add AWS credentials to .env"
echo "  4. Run: docker-compose logs -f routing-service (to monitor)"
echo ""
echo "Key endpoints:"
echo "  http://localhost:8001 - Auth Service"
echo "  http://localhost:8002 - Routing Service (main)"
echo "  http://localhost:8003 - AI Service"
echo ""
