# Frontend Deployment Guide

## EC2 Setup

### 1. Install Node.js

```bash
# Run setup script
cd ~/route-mind-project-enterprise
chmod +x scripts/setup_frontend_ec2.sh
./scripts/setup_frontend_ec2.sh
```

Or manually:

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should be v20.x
npm --version
```

### 2. Install Dependencies

```bash
cd ~/route-mind-project-enterprise/frontend
npm install
```

### 3. Configure Security Group

Open port 3000 in AWS Security Group:

1. Go to EC2 Console > Security Groups
2. Select your instance's security group
3. Add Inbound Rule:
   - Type: Custom TCP
   - Port: 3000
   - Source: 0.0.0.0/0 (or your IP)

### 4. Start Development Server

```bash
npm run dev
```

Access at: `http://<your-ec2-public-ip>:3000`

### 5. Production Build (Optional)

```bash
npm run build
npm run preview
```

## API Configuration

Frontend proxies API requests to backend:

- Development: `/api` -> `http://localhost:8002/api`
- Production: Update `vite.config.ts` with production backend URL

## Environment Variables

Create `.env` if needed:

```env
VITE_API_BASE_URL=http://localhost:8002
```

## Troubleshooting

### Port 3000 already in use

```bash
# Find and kill process
sudo lsof -i :3000
sudo kill -9 <PID>
```

### Cannot connect to backend

Check backend is running:

```bash
curl http://localhost:8002/api/v1/metrics
```

### Build fails

Clear cache and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Demo Mode

Toggle "Demo Mode" in header to use mock data without backend.

Perfect for:
- Frontend development without backend
- Presentations when backend is unreachable
- UI testing
