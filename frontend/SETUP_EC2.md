# EC2 Frontend Setup - Complete Guide

## Quick Deploy (Automated)

```bash
# SSH to EC2
ssh ubuntu@<your-ec2-ip>

# Go to project directory
cd ~/route-mind-project-enterprise

# Make script executable
chmod +x frontend/EC2_DEPLOY.sh

# Run deployment script
./frontend/EC2_DEPLOY.sh
```

That's it! The script will:
1. Install Node.js 20
2. Install dependencies
3. Build production bundle
4. Start frontend with PM2 (production process manager)

## Manual Setup (Step by Step)

### 1. Install Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version  # Should show v20.x
```

### 2. Install Dependencies

```bash
cd ~/route-mind-project-enterprise/frontend
npm install
```

### 3. Build for Production

```bash
npm run build
```

This creates optimized files in `dist/` directory.

### 4. Start Frontend

#### Option A: Development Mode (for testing)

```bash
npm run dev -- --host --port 3000
```

#### Option B: Production Mode (recommended)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start with PM2
pm2 start npm --name "routemind-frontend" -- run preview -- --host --port 3000

# Save PM2 config
pm2 save

# Setup auto-restart on reboot
pm2 startup
```

### 5. Configure AWS Security Group

**CRITICAL: Open port 3000**

1. Go to AWS Console > EC2 > Security Groups
2. Select your instance's security group
3. Click "Edit inbound rules"
4. Click "Add rule"
   - Type: Custom TCP
   - Port range: 3000
   - Source: 0.0.0.0/0 (or your IP for security)
5. Click "Save rules"

### 6. Access Frontend

```
http://<your-ec2-public-ip>:3000
```

## Login Credentials

### Demo Mode
Click "Demo Login" button - no authentication needed

### Backend Authentication
If auth-service is running:
- Email: demo@example.com
- Password: demo123

## PM2 Commands

```bash
# View all processes
pm2 list

# View logs
pm2 logs routemind-frontend

# Restart frontend
pm2 restart routemind-frontend

# Stop frontend
pm2 stop routemind-frontend

# Delete process
pm2 delete routemind-frontend

# Monitor resources
pm2 monit
```

## Update Frontend (After Code Changes)

```bash
# Pull latest code
cd ~/route-mind-project-enterprise
git pull

# Rebuild
cd frontend
npm run build

# Restart PM2
pm2 restart routemind-frontend
```

## Troubleshooting

### Port 3000 Already in Use

```bash
# Find process using port 3000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>

# Or use different port
pm2 delete routemind-frontend
pm2 start npm --name "routemind-frontend" -- run preview -- --host --port 3001
```

### Cannot Connect to Backend

Check backend is accessible:

```bash
curl http://localhost:8002/api/v1/metrics
```

If that works but frontend can't connect, update `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8002',
    changeOrigin: true,
  }
}
```

### Build Fails

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules dist package-lock.json
npm install
npm run build
```

### PM2 Not Starting

```bash
# Check logs
pm2 logs routemind-frontend --lines 50

# Try manual start
cd ~/route-mind-project-enterprise/frontend
npm run preview -- --host --port 3000
```

### Login Not Working

1. **Use Demo Mode**: Click "Demo Login" button
2. **Check auth-service**: `curl http://localhost:8001/docs`
3. **Create demo user** (if needed):

```bash
# Connect to database
docker-compose exec -T db psql -U routemind -d routemind_db

# Create demo user (inside psql)
INSERT INTO users (email, hashed_password, is_active) 
VALUES ('demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeVXa3bXxE5i', true);
```

Password hash above is for: `demo123`

## Environment Variables

Create `.env.production` if needed:

```env
VITE_API_BASE_URL=http://localhost:8002
VITE_AUTH_BASE_URL=http://localhost:8001
```

Then rebuild:

```bash
npm run build
pm2 restart routemind-frontend
```

## Nginx Reverse Proxy (Optional, for production)

If you want to use port 80 instead of 3000:

```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Configure
sudo nano /etc/nginx/sites-available/routemind
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name <your-ec2-ip>;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/routemind /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Then open port 80 in Security Group instead of 3000.

## Verification Checklist

- [ ] Node.js 20+ installed
- [ ] Dependencies installed (node_modules exists)
- [ ] Build completed (dist/ folder exists)
- [ ] Frontend running (PM2 list shows "online")
- [ ] Port 3000 open in Security Group
- [ ] Can access http://<ec2-ip>:3000
- [ ] Login page loads
- [ ] Demo login works
- [ ] Dashboard shows data
- [ ] Routes page works
- [ ] Map displays correctly

## Performance Tips

1. **Enable gzip compression** (Nginx does this automatically)
2. **Use PM2 cluster mode** for multiple instances:
   ```bash
   pm2 delete routemind-frontend
   pm2 start npm --name "routemind-frontend" -i max -- run preview -- --host --port 3000
   ```
3. **Monitor with PM2**:
   ```bash
   pm2 monit
   ```

## Success Metrics

Once deployed successfully:
- Frontend loads in <2 seconds
- Login works (demo or real)
- Dashboard displays metrics
- Routes page shows map
- Dark mode toggle works
- Demo mode toggle works
- No console errors

---

**Your frontend is now production-ready on EC2!** 🚀
