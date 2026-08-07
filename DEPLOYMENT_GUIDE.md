# RouteMind - Deployment Guide

## Option 1: Local Docker Deployment (Recommended for Testing)

### Prerequisites
- Docker Desktop or Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- Ports 8001, 8002, 8003, 5432, 6379 available

### Steps

1. **Clone Repository**
```bash
git clone <your-repo-url>
cd route-mind-project-enterprise
```

2. **Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials:
```env
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your_secret_key_here

POSTGRES_PASSWORD=change_this_secure_password
SECRET_KEY=change_this_jwt_secret_key
```

3. **Build Services**
```bash
docker-compose build
```

4. **Start Services**
```bash
docker-compose up -d
```

5. **Verify Services**
```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                  STATUS    PORTS
# auth-service          Up        0.0.0.0:8001->8000/tcp
# routing-service       Up        0.0.0.0:8002->8000/tcp
# ai-service           Up        0.0.0.0:8003->8000/tcp
# db                   Up        5432/tcp
# redis                Up        6379/tcp

# Test health endpoints
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

6. **Seed Sample Data**
```bash
# Wait 30 seconds for database initialization
sleep 30

# Install asyncpg in routing container
docker-compose exec routing-service pip install asyncpg

# Run seed script
docker-compose exec routing-service python scripts/seed_data.py
```

7. **Test Optimization**
```bash
curl -X POST "http://localhost:8002/api/v1/optimizer/optimize?hub_id=1&use_ai_explanation=true"
```

## Option 2: AWS EC2 Deployment

### Prerequisites
- AWS account
- EC2 key pair
- Security group with ports 22, 8001-8003 open

### Launch Instance

1. **Create EC2 Instance**
```
AMI: Ubuntu 22.04 LTS
Instance Type: t3.large (recommended) or t3.medium (minimum)
Storage: 30GB gp3
Security Group: Allow ports 22, 8001, 8002, 8003
```

2. **SSH into Instance**
```bash
ssh -i your-key.pem ubuntu@<ec2-public-ip>
```

3. **Install Docker**
```bash
# Run the provided installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker ubuntu
newgrp docker
```

4. **Clone and Deploy**
```bash
git clone <your-repo-url>
cd route-mind-project-enterprise

# Configure .env
nano .env
# (Add your AWS credentials and passwords)

# Build and start
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f
```

5. **Access Services**
```
http://<ec2-public-ip>:8001/health  # Auth Service
http://<ec2-public-ip>:8002/health  # Routing Service
http://<ec2-public-ip>:8003/health  # AI Service
```

### AWS EC2 Security Group Configuration

```
Inbound Rules:
- SSH (22): Your IP / 0.0.0.0/0
- Custom TCP (8001): 0.0.0.0/0
- Custom TCP (8002): 0.0.0.0/0
- Custom TCP (8003): 0.0.0.0/0

Outbound Rules:
- All traffic: 0.0.0.0/0
```

## Option 3: Production AWS Deployment (Advanced)

### Architecture
```
Internet → ALB → ECS Fargate (Services) → RDS PostgreSQL
                                         → ElastiCache Redis
```

### Services Needed
- **ECS Fargate**: Run containers
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **ALB**: Load balancer
- **ECR**: Container registry
- **IAM**: Bedrock access

### Steps

1. **Create RDS PostgreSQL**
```bash
# Via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier routemind-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username routemind \
  --master-user-password YourSecurePassword \
  --allocated-storage 20
```

2. **Create ElastiCache Redis**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id routemind-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

3. **Push Images to ECR**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name routemind/auth-service
aws ecr create-repository --repository-name routemind/routing-service
aws ecr create-repository --repository-name routemind/ai-service

# Build and push
docker build -t routemind/auth-service services/auth-service
docker tag routemind/auth-service:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/routemind/auth-service:latest
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/routemind/auth-service:latest

# Repeat for routing-service and ai-service
```

4. **Create ECS Cluster and Services**
- Use AWS Console or Terraform
- Configure environment variables from RDS/ElastiCache endpoints
- Set up ALB for routing
- Configure auto-scaling

## Troubleshooting

### Issue: Database Connection Failed

**Symptom**: Services fail to start with "connection refused" error

**Solution**:
```bash
# Check if database is ready
docker-compose logs db

# Wait for this line: "database system is ready to accept connections"

# Restart services
docker-compose restart routing-service auth-service
```

### Issue: Bedrock Access Denied

**Symptom**: AI explanations return empty or error

**Solution**:
1. Verify AWS credentials in `.env`
2. Check Bedrock model access in AWS Console
3. Ensure Kimi K2.5 is enabled in your region
```bash
aws bedrock list-foundation-models --region us-east-2 | grep kimi
```

### Issue: Port Already in Use

**Symptom**: "port is already allocated" error

**Solution**:
```bash
# Check what's using the port
sudo lsof -i :8002

# Kill the process or change port in docker-compose.yml
# Example: Change "8002:8000" to "8012:8000"
```

### Issue: Out of Memory

**Symptom**: Services crash or slow performance

**Solution**:
```bash
# Check Docker memory
docker stats

# Increase Docker Desktop memory (Preferences → Resources)
# Or use smaller instance on EC2 (reduce concurrent requests)
```

### Issue: Seed Data Script Fails

**Symptom**: "asyncpg not found" or connection error

**Solution**:
```bash
# Install asyncpg in the container
docker-compose exec routing-service pip install asyncpg

# Verify database is accepting connections
docker-compose exec db psql -U routemind -d routemind_db -c "\dt"

# Re-run seed script
docker-compose exec routing-service python scripts/seed_data.py
```

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f routing-service

# Last 100 lines
docker-compose logs --tail=100 routing-service
```

### Check Resource Usage
```bash
docker stats

# Output:
# CONTAINER         CPU %    MEM USAGE / LIMIT    MEM %
# routing-service   2.5%     350MB / 4GB         8.75%
# auth-service      0.5%     200MB / 4GB         5.0%
```

### Database Queries
```bash
# Connect to database
docker-compose exec db psql -U routemind -d routemind_db

# Check tables
\dt

# Count stops
SELECT COUNT(*) FROM stops;

# Count vehicles
SELECT COUNT(*) FROM vehicles;
```

## Backup and Restore

### Backup Database
```bash
docker-compose exec db pg_dump -U routemind routemind_db > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose exec -T db psql -U routemind -d routemind_db
```

## Performance Tuning

### For High Load
1. Increase PostgreSQL connections in `docker-compose.yml`:
```yaml
command: postgres -c max_connections=200
```

2. Enable Redis caching in routing service (ready to use)

3. Add more replicas:
```yaml
routing-service:
  deploy:
    replicas: 3
```

## Shutdown

### Graceful Shutdown
```bash
docker-compose down
```

### Complete Cleanup (removes data)
```bash
docker-compose down -v
```

## Next Steps After Deployment

1. ✅ Verify all health endpoints respond
2. ✅ Seed sample data
3. ✅ Test optimize endpoint
4. ✅ Test replan endpoint
5. ✅ Check AI explanations are working
6. ✅ Monitor logs for errors
7. ✅ Run load tests (optional)

## Support

For issues, check:
1. `docker-compose logs` for error messages
2. `BUGS_FIXED.md` for known issues
3. Service health endpoints
4. AWS Bedrock console for API issues

---

**Ready to deploy? Start with Option 1 (Local Docker) for testing!**
