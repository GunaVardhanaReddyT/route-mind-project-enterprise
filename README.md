# RouteMind
## Adaptive Route Optimization for the Supply Chain

## What we're trying to do

1. Build a system with multiple microservices.
2. Use AI for optimized route selection wherever required.

## Microservices

### 1. ai-service

Handles all AI-related services.

All AI service code is contained within this microservice to keep AI functionality separate and modular.

### 2. auth-service

- JWT-based authentication using Python-JOSE
- Password hashing with bcrypt via Passlib
- User data stored in PostgreSQL
- Login endpoint returns JWT tokens
- Token expiration: 30 minutes (configurable)

### 3. routing-service

Handles route optimization.

Features:

- Takes vehicles and delivery stops as input
- Uses Google OR-Tools (free, open-source solver)
- Solves the Vehicle Routing Problem (VRP)
- Returns optimized routes that minimize distance

#### Indian Constraints

- COD Limit: ₹50,000 per vehicle  
  Enforced using OR-Tools capacity dimension.

- Zone Timing: Trucks restricted to 8-10 PM  
  Class ready, not fully enforced yet.

- Odd-Even: Delhi vehicle plate rules  
  Class ready, not fully enforced yet.

#### Dynamic Re-planning

- Handles new pickup requests during an active route.
- Handles failed deliveries.
- Re-solves routes in less than 30 seconds.
- Shows route changes for supervisor approval.

### AI Explanations

- Uses AWS Bedrock with the Kimi K2.5 model.
- Generates human-readable explanations for supervisors.
- Routing works completely without AI explanations.
- Cost: ~$0.001 per explanation.
