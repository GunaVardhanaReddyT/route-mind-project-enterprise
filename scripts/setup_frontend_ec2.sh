#!/bin/bash

echo "=== RouteMind Frontend Setup for EC2 ==="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js already installed: $(node --version)"
fi

echo ""
echo "=== Installing Frontend Dependencies ==="
cd ~/route-mind-project-enterprise/frontend
npm install

echo ""
echo "=== Frontend Setup Complete ==="
echo ""
echo "To start the frontend:"
echo "  cd ~/route-mind-project-enterprise/frontend"
echo "  npm run dev"
echo ""
echo "Access at: http://<your-ec2-ip>:3000"
echo ""
echo "IMPORTANT: Open port 3000 in AWS Security Group!"
echo "  1. Go to EC2 > Security Groups"
echo "  2. Select your instance's security group"
echo "  3. Add Inbound Rule: Custom TCP, Port 3000, Source 0.0.0.0/0"
echo ""
