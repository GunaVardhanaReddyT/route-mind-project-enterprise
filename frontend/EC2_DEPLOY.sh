#!/bin/bash

echo "========================================="
echo "RouteMind Frontend - EC2 Deployment"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on EC2
if [ ! -f /home/ubuntu/.bashrc ]; then
    echo -e "${RED}Error: This script should run on EC2 Ubuntu instance${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Installing Node.js 20...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo -e "${GREEN}✓ Node.js installed: $(node --version)${NC}"
else
    echo -e "${GREEN}✓ Node.js already installed: $(node --version)${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
cd ~/route-mind-project-enterprise/frontend
npm install

echo ""
echo -e "${BLUE}Step 3: Building production bundle...${NC}"
npm run build

echo ""
echo -e "${BLUE}Step 4: Installing PM2 (process manager)...${NC}"
if ! command -v pm2 &> /dev/null; then
    sudo npm install -g pm2
    echo -e "${GREEN}✓ PM2 installed${NC}"
else
    echo -e "${GREEN}✓ PM2 already installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Starting frontend with PM2...${NC}"
pm2 delete routemind-frontend 2>/dev/null || true
pm2 start npm --name "routemind-frontend" -- run preview -- --host --port 3000
pm2 save
pm2 startup

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Frontend deployed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Access your frontend at:"
echo -e "${BLUE}http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000${NC}"
echo ""
echo "PM2 Commands:"
echo "  pm2 list                  # List processes"
echo "  pm2 logs routemind-frontend  # View logs"
echo "  pm2 restart routemind-frontend  # Restart"
echo "  pm2 stop routemind-frontend     # Stop"
echo ""
echo -e "${RED}IMPORTANT: Open port 3000 in Security Group!${NC}"
echo "1. Go to EC2 Console > Security Groups"
echo "2. Select your instance's security group"
echo "3. Add Inbound Rule: Custom TCP, Port 3000, Source 0.0.0.0/0"
echo ""
