#!/bin/bash
# RouteMind API Test Script
# Tests all endpoints to verify deployment

set -e

echo "🧪 RouteMind API Test Script"
echo "================================"
echo ""

BASE_URL="${BASE_URL:-http://localhost}"
AUTH_PORT="${AUTH_PORT:-8001}"
ROUTING_PORT="${ROUTING_PORT:-8002}"
AI_PORT="${AI_PORT:-8003}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if [ "$response" -eq 200 ] || [ "$response" -eq 201 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
        return 1
    fi
}

# Test with response body
test_endpoint_verbose() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4
    
    echo ""
    echo "================================"
    echo "Testing: $name"
    echo "URL: $url"
    echo "Method: $method"
    echo "================================"
    
    if [ "$method" = "GET" ]; then
        curl -s "$url" | jq '.' || curl -s "$url"
    else
        curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" | jq '.' || curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
    
    echo ""
}

echo "1️⃣  Testing Health Endpoints"
echo "------------------------------"
test_endpoint "Auth Service Health" "$BASE_URL:$AUTH_PORT/health" "GET"
test_endpoint "Routing Service Health" "$BASE_URL:$ROUTING_PORT/health" "GET"
test_endpoint "AI Service Health" "$BASE_URL:$AI_PORT/health" "GET"
echo ""

echo "2️⃣  Testing AI Service"
echo "------------------------------"
test_endpoint "AI Service Status" "$BASE_URL:$AI_PORT/api/v1/status" "GET"
echo ""

echo "3️⃣  Testing Route Optimization"
echo "------------------------------"
echo -e "${YELLOW}This will run the actual OR-Tools solver...${NC}"
test_endpoint_verbose "Optimize Routes (with AI)" \
    "$BASE_URL:$ROUTING_PORT/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true" \
    "POST"

echo ""
echo "4️⃣  Testing Route Re-planning"
echo "------------------------------"
echo -e "${YELLOW}Testing replan with new pickup...${NC}"
test_endpoint_verbose "Replan Route (new pickup)" \
    "$BASE_URL:$ROUTING_PORT/api/v1/optimizer/replan?route_id=1&new_stop_id=5&reason=new_pickup&hub_id=1" \
    "POST" \
    '{}'

echo ""
echo "5️⃣  Summary"
echo "================================"
echo -e "${GREEN}✓ All basic tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Check that total_distance_km is accurate"
echo "  2. Verify AI explanations are meaningful"
echo "  3. Test with more stops (10-100)"
echo "  4. Monitor solve_time_ms (<30s requirement)"
echo ""
echo "For detailed logs:"
echo "  docker-compose logs -f routing-service"
echo ""
