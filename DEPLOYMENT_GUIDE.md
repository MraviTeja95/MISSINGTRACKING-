# 🚀 Deployment Guide

## Overview
This guide covers deploying TraceNet to various platforms:
- **Local Development**: Windows/Linux/Mac
- **Docker**: Containerized deployment
- **AWS**: Cloud deployment (EC2 + RDS)
- **Linux Server**: Self-hosted deployment

---

## Prerequisites

### System Requirements
- **Python**: 3.9 or 3.11
- **Node.js**: 14+ (for frontend asset compilation, optional)
- **Database**: MySQL 8.0+ or SQLite
- **Disk Space**: 2GB minimum
- **RAM**: 2GB minimum

### Tools Required
```bash
# Windows / macOS
- Git
- Python
- pip (Python package manager)
- Virtual Environment (venv)

# Linux
- git, python3, python3-pip, python3-venv
- MySQL server (if not using managed service)
```

---

## 1. Local Development Deployment

### 1.1 Windows Deployment

#### Step 1: Clone Repository
```powershell
# Navigate to desired directory
cd C:\Users\YourUsername\Desktop

# Clone repository
git clone https://github.com/yourusername/missing_tracker.git
cd missing_tracker
```

#### Step 2: Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If permission denied:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

#### Step 3: Install Dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```powershell
# Create .env file in project root
New-Item -Path .env -ItemType File

# Edit .env file and add:
```

**.env file content:**
```
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here-change-in-production
SQLALCHEMY_DATABASE_URI=sqlite:///missing_tracker.db

# Firebase Configuration (if using)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_email@firebase.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
```

#### Step 5: Initialize Database
```powershell
# Ensure database is created
python -c "from app import create_app; app = create_app(); print('Database initialized')"
```

#### Step 6: Run Application
```powershell
# Method 1: Direct execution
python app.py

# Method 2: Using Flask CLI
flask run

# Method 3: Using provided script
.\run_demo.ps1  # For SQLite demo mode
```

**Access**: `http://localhost:5000`

---

### 1.2 Linux/macOS Deployment

#### Step 1: Clone and Setup
```bash
# Clone repository
git clone https://github.com/yourusername/missing_tracker.git
cd missing_tracker

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
# Update pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 3: Environment Configuration
```bash
# Create .env file
touch .env
nano .env  # Edit configuration
```

#### Step 4: Run Application
```bash
# Using Flask
flask run --host=0.0.0.0 --port=5000

# Or direct execution
python app.py
```

---

## 2. Docker Deployment

### 2.1 Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads && chmod 777 static/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/')"

# Run Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:create_app()"]
```

### 2.2 Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # MySQL Database Service
  mysql:
    image: mysql:8.0
    container_name: tracenet-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: tracenet_db
      MYSQL_USER: tracenet_user
      MYSQL_PASSWORD: tracenet_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 5s
      retries: 5
    networks:
      - tracenet_network

  # Flask Web Service
  web:
    build: .
    container_name: tracenet-web
    environment:
      FLASK_ENV: production
      SQLALCHEMY_DATABASE_URI: mysql+pymysql://tracenet_user:tracenet_password@mysql:3306/tracenet_db
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
    ports:
      - "5000:5000"
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./static/uploads:/app/static/uploads
    restart: unless-stopped
    networks:
      - tracenet_network

volumes:
  mysql_data:

networks:
  tracenet_network:
    driver: bridge
```

### 2.3 Deploy with Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Access application
# http://localhost:5000
```

---

## 3. AWS Deployment

### 3.1 Architecture
```
┌─────────────────┐
│  CloudFront     │ (CDN)
│  (Optional)     │
└────────┬────────┘
         │
┌────────▼──────────────┐
│   Application Load    │
│   Balancer (ALB)      │
└────────┬──────────────┘
         │
┌────────▼──────────────────────────────────┐
│  EC2 Auto Scaling Group                   │
│  ├─ Instance 1: Flask App (t3.medium)     │
│  ├─ Instance 2: Flask App (t3.medium)     │
│  └─ Instance 3: Flask App (t3.medium)     │
└────────┬──────────────────────────────────┘
         │
    ┌────▼────┬──────────────┐
    │          │              │
┌───▼──┐  ┌───▼────┐  ┌─────▼────┐
│ RDS  │  │ ElastiC│  │ S3 Bucket │
│MySQL │  │ Cache  │  │ (Uploads) │
└──────┘  └────────┘  └───────────┘
```

### 3.2 Step-by-Step AWS Deployment

#### Step 1: Prepare Application for AWS

1. **Update requirements.txt** - Add production dependencies:
```txt
# Existing requirements plus:
gunicorn==20.1.0          # WSGI server
pymysql==1.0.2            # MySQL driver
python-dotenv==0.19.0     # Environment management
```

2. **Create .env.production** (store in AWS Secrets Manager):
```
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:pass@rds-endpoint:3306/tracenet_db
SECRET_KEY=very-secure-random-key-min-32-chars
DEBUG=False
```

#### Step 2: Create RDS MySQL Database

```bash
# Via AWS Console:
1. Services > RDS > Create Database
2. Engine: MySQL 8.0
3. Instance class: db.t3.micro (free tier) or db.t3.small (production)
4. Storage: 20GB (General Purpose SSD)
5. Networking: VPC, security group allowing port 3306
6. Initial Database: tracenet_db
7. Master username: admin
8. Password: (secure password)
```

**Store endpoint**: `tracenet.xxxxx.us-east-1.rds.amazonaws.com:3306`

#### Step 3: Create EC2 Instance

```bash
# Launch EC2 Instance
1. EC2 Dashboard > Launch Instance
2. AMI: Ubuntu 20.04 LTS (ami-xxxxxxxx)
3. Instance Type: t3.medium (2 vCPU, 4 GB RAM)
4. Network: VPC, Subnet, Security Group
5. Storage: 30 GB (gp2)
6. Security Group Rules:
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - SSH (22): Your IP only
   - Custom TCP 5000: ALB security group
```

#### Step 4: Deploy on EC2

SSH into instance:
```bash
ssh -i your-key.pem ubuntu@ec2-instance-ip
```

Setup application:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git \
  mysql-client build-essential libopencv-dev

# Clone repository
git clone https://github.com/yourusername/missing_tracker.git
cd missing_tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from AWS Secrets Manager
# (Store sensitive data in AWS Secrets Manager)
```

#### Step 5: Configure Gunicorn

Create `/etc/systemd/system/tracenet.service`:
```ini
[Unit]
Description=TraceNet Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/missing_tracker
ExecStart=/home/ubuntu/missing_tracker/venv/bin/gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile /var/log/tracenet/access.log \
  --error-logfile /var/log/tracenet/error.log \
  'app:create_app()'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start tracenet
sudo systemctl enable tracenet
sudo systemctl status tracenet
```

#### Step 6: Configure Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/tracenet`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files caching
    location /static/ {
        alias /home/ubuntu/missing_tracker/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/tracenet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 7: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

#### Step 8: Create Load Balancer (ALB)

```bash
# Via AWS Console:
1. EC2 > Load Balancers > Create Load Balancer
2. Type: Application Load Balancer
3. Scheme: Internet-facing
4. Listeners: HTTP (80), HTTPS (443)
5. Target Group: Port 5000, Protocol: HTTP
6. Health Check: /
7. Register EC2 instances
```

---

## 4. Linux Server Deployment (Self-Hosted)

### 4.1 Ubuntu 20.04 Server

```bash
# 1. Initial Server Setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git

# 2. Install Python 3.11
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 3. Create application user
sudo useradd -m -s /bin/bash tracenet
sudo usermod -aG sudo tracenet
sudo -u tracenet mkdir /home/tracenet/app
cd /home/tracenet/app

# 4. Clone and setup
sudo -u tracenet git clone https://github.com/yourusername/missing_tracker.git .
sudo -u tracenet python3.11 -m venv venv
sudo -u tracenet source venv/bin/activate && pip install -r requirements.txt

# 5. Create data directory
sudo -u tracenet mkdir -p static/uploads
sudo chmod 755 static/uploads

# 6. Configure environment
sudo -u tracenet nano .env
# Add configuration here

# 7. Setup systemd service (see AWS section for service file)
# 8. Setup nginx (see AWS section for nginx config)
# 9. Start application
sudo systemctl start tracenet
sudo systemctl status tracenet
```

---

## 5. Monitoring & Maintenance

### 5.1 Application Monitoring

```bash
# Check application logs
sudo journalctl -u tracenet -f

# Monitor system resources
top
free -h
df -h

# Check database
mysql -h localhost -u root -p
> SHOW DATABASES;
> USE tracenet_db;
> SHOW TABLES;
```

### 5.2 Backup Strategy

```bash
# Database backup
mysqldump -h localhost -u root -p tracenet_db > /backups/tracenet_$(date +%Y%m%d).sql

# Uploads backup
tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz static/uploads/

# Automated daily backup (crontab)
0 2 * * * /home/ubuntu/backup.sh
```

### 5.3 Security Hardening

```bash
# 1. Firewall rules
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 2. Fail2Ban for SSH protection
sudo apt install -y fail2ban
sudo systemctl enable fail2ban

# 3. Regular updates
sudo apt update && sudo apt upgrade -y

# 4. Log rotation
sudo nano /etc/logrotate.d/tracenet
```

---

## 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| **Database connection fails** | Check SQLALCHEMY_DATABASE_URI, verify RDS/MySQL is running |
| **Port 5000 already in use** | `lsof -i :5000` then kill process or use different port |
| **Permission denied on uploads** | `sudo chmod 777 static/uploads/` |
| **SSL certificate errors** | Run `certbot renew` or generate new certificate |
| **Nginx 502 Bad Gateway** | Check Gunicorn is running: `systemctl status tracenet` |
| **High memory usage** | Increase worker count or use supervisor for process management |

---

## Performance Optimization

```python
# config.py additions
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}

# Static file compression
COMPRESS_ALGORITHM = 'gzip'
COMPRESS_LEVEL = 6

# Caching
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://localhost:6379/0"
```

---

