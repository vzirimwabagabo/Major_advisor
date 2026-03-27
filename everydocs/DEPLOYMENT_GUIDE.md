# 🚀 USIU Major Advisor - Deployment Guide

## 📋 **Deployment Overview**

This guide covers deploying the USIU Major Advisor System from development to production.

---

## 🎯 **Current Status**

### **✅ Development Environment**
- **Framework:** Flask 2.3.3 (Python)
- **Database:** SQLite (file-based)
- **Server:** Flask development server
- **Status:** Fully functional locally

### **🎯 Production Targets**
- **Web Server:** Gunicorn + Nginx
- **Database:** PostgreSQL (recommended)
- **Hosting:** VPS/Cloud (AWS/DigitalOcean/Heroku)
- **Domain:** usiu-major-advisor.edu or similar

---

## 🏗️ **Deployment Options**

### **Option 1: Heroku (Easiest)**
**Best for:** Quick deployment, automatic scaling
```bash
# 1. Install Heroku CLI
# 2. Create Heroku app
heroku create usiu-major-advisor

# 3. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here

# 4. Deploy
git push heroku main
```

### **Option 2: DigitalOcean VPS (Recommended)**
**Best for:** Full control, cost-effective
```bash
# Ubuntu 22.04 LTS server
# 1GB RAM, 1 CPU, 25GB SSD minimum
```

### **Option 3: AWS EC2**
**Best for:** Enterprise, scalability
```bash
# t3.micro instance (free tier eligible)
# Ubuntu Server 22.04 LTS
```

---

## 📦 **Production Setup (DigitalOcean)**

### **Step 1: Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install PostgreSQL (optional, can use SQLite)
sudo apt install postgresql postgresql-contrib -y
```

### **Step 2: Application Setup**
```bash
# Create application directory
sudo mkdir -p /var/www/usiu-advisor
cd /var/www/usiu-advisor

# Clone your repository
git clone https://github.com/vzirimwabagabo/Major_advisor.git .
cd secured site

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # Production dependencies
```

### **Step 3: Database Setup**
```bash
# For PostgreSQL (recommended for production)
sudo -u postgres psql
CREATE DATABASE usiu_advisor;
CREATE USER advisor_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE usiu_advisor TO advisor_user;
\q

# Update app.py database URI
# Change: 'sqlite:///site.db'
# To: 'postgresql://advisor_user:secure_password_here@localhost/usiu_advisor'
```

### **Step 4: Environment Configuration**
```bash
# Create .env file
nano .env

# Add to .env:
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here-2026
DATABASE_URL=postgresql://advisor_user:secure_password_here@localhost/usiu_advisor
ADMIN_EMAIL=admin@usiu.ac.ke
ADMIN_PASSWORD=secure_admin_password_2026

# Load environment variables
pip install python-dotenv
```

### **Step 5: Create Admin User**
```bash
# Create admin user script
python3 -c "
from app import app, db, User
with app.app_context():
    db.create_all()
    admin = User(username='admin', email='admin@usiu.ac.ke', is_admin=True)
    admin.set_password('secure_admin_password_2026')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin user created')
"
```

### **Step 6: Gunicorn Setup**
```bash
# Create Gunicorn config
nano gunicorn.conf.py

# Add to gunicorn.conf.py:
bind = '127.0.0.1:8000'
workers = 3
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None
```

### **Step 7: Systemd Service**
```bash
# Create systemd service
sudo nano /etc/systemd/system/usiu-advisor.service

# Add to service file:
[Unit]
Description=USIU Major Advisor Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/usiu-advisor/secured site
Environment=PATH=/var/www/usiu-advisor/secured site/venv/bin
ExecStart=/var/www/usiu-advisor/secured site/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable usiu-advisor
sudo systemctl start usiu-advisor
sudo systemctl status usiu-advisor
```

### **Step 8: Nginx Configuration**
```bash
# Create Nginx site config
sudo nano /etc/nginx/sites-available/usiu-advisor

# Add to config:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/usiu-advisor/secured site/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/usiu-advisor /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 9: SSL Certificate (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install snapd -y
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### **Step 10: Firewall Setup**
```bash
# Configure UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

---

## 🔧 **Environment Variables**

### **Required for Production:**
```bash
# .env file
FLASK_ENV=production
SECRET_KEY=your-256-bit-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
ADMIN_EMAIL=admin@usiu.ac.ke
ADMIN_PASSWORD=secure_password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### **Optional Enhancements:**
```bash
# Analytics
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID

# File uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Session security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
```

---

## 📊 **Database Migration**

### **From SQLite to PostgreSQL:**
```python
# migration_script.py
from app import app, db
from flask_migrate import Migrate, upgrade
import os

# Set PostgreSQL URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Initialize Flask-Migrate
migrate = Migrate(app, db)

with app.app_context():
    # Create all tables
    db.create_all()

    # If using Flask-Migrate:
    # upgrade()

    print("✅ Database migrated to PostgreSQL")
```

---

## 🔒 **Security Checklist**

### **Pre-Deployment:**
- ✅ **Change default SECRET_KEY**
- ✅ **Use strong admin password**
- ✅ **Enable HTTPS/SSL**
- ✅ **Configure firewall**
- ✅ **Update all dependencies**

### **Post-Deployment:**
- ✅ **Test all user flows**
- ✅ **Verify admin access**
- ✅ **Check database connections**
- ✅ **Monitor error logs**
- ✅ **Set up backups**

### **Ongoing Security:**
- 🔄 **Regular updates** (OS, Python, packages)
- 🔄 **Monitor logs** for suspicious activity
- 🔄 **Backup database** daily
- 🔄 **SSL certificate renewal**
- 🔄 **Security audits**

---

## 📈 **Monitoring & Maintenance**

### **Log Management:**
```bash
# View application logs
sudo journalctl -u usiu-advisor -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Backup Strategy:**
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump usiu_advisor > /backups/usiu_advisor_$DATE.sql

# File backup
tar -czf /backups/app_$DATE.tar.gz /var/www/usiu-advisor
```

### **Performance Monitoring:**
```bash
# System resources
htop
df -h
free -h

# Application metrics
sudo systemctl status usiu-advisor
sudo netstat -tlnp | grep :8000
```

---

## 🚀 **Deployment Verification**

### **Test Checklist:**
- [ ] **Domain resolves** to server IP
- [ ] **SSL certificate** is valid
- [ ] **Homepage loads** at https://your-domain.com
- [ ] **User registration** works
- [ ] **Admin login** works
- [ ] **Major recommendations** generate correctly
- [ ] **Database** saves data properly
- [ ] **Email notifications** send (if configured)
- [ ] **Mobile responsive** design works
- [ ] **All links** function correctly

### **Load Testing:**
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test concurrent users
ab -n 1000 -c 10 https://your-domain.com/
```

---

## 🌐 **Domain & DNS Setup**

### **DNS Configuration:**
```
Type: A
Name: @
Value: YOUR_SERVER_IP

Type: CNAME
Name: www
Value: your-domain.com

Type: MX (optional)
Name: @
Value: mail.your-domain.com
```

### **Domain Registrar:**
- **Recommended:** Namecheap, GoDaddy, or Porkbun
- **Cost:** ~$12/year for .edu equivalent
- **SSL:** Free with Let's Encrypt

---

## 💰 **Cost Breakdown**

### **Monthly Costs:**
- **VPS (DigitalOcean):** $6-12/month (1-2GB RAM)
- **Domain:** $1-2/month
- **SSL:** Free
- **Email:** Free (Gmail) or $5/month (custom)
- **Backups:** $1-5/month (optional)

### **One-time Setup:**
- **Server setup:** 2-4 hours
- **Domain registration:** $12/year
- **SSL certificate:** Free

**Total first year cost: ~$100-200**

---

## 🔄 **Update Deployment**

### **Code Updates:**
```bash
# On server
cd /var/www/usiu-advisor
git pull origin main

# Restart services
sudo systemctl restart usiu-advisor
sudo systemctl restart nginx
```

### **Dependency Updates:**
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart usiu-advisor
```

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**App not starting:**
```bash
# Check logs
sudo journalctl -u usiu-advisor -n 50

# Check Python errors
cd /var/www/usiu-advisor/secured site
source venv/bin/activate
python -c "from app import app; print('Import successful')"
```

**Database connection failed:**
```bash
# Test PostgreSQL connection
sudo -u postgres psql -d usiu_advisor -c "SELECT version();"

# Check DATABASE_URL in .env
cat .env
```

**Nginx not serving:**
```bash
# Test config
sudo nginx -t

# Check status
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
```

**SSL issues:**
```bash
# Renew certificate
sudo certbot renew

# Check certificate
curl -I https://your-domain.com
```

---

## 📞 **Support & Maintenance**

### **Monitoring:**
- **Uptime:** Set up monitoring (UptimeRobot free tier)
- **Performance:** Monitor response times
- **Errors:** Set up error alerting
- **Backups:** Automated daily backups

### **Support:**
- **Documentation:** Keep deployment guide updated
- **Logs:** Regular log review
- **Updates:** Monthly security updates
- **Backup:** Test restore procedures quarterly

---

## 🎯 **Go-Live Checklist**

- [ ] **Domain purchased** and DNS configured
- [ ] **Server provisioned** and secured
- [ ] **Application deployed** and tested
- [ ] **SSL certificate** installed
- [ ] **Admin account** created
- [ ] **Database** populated with initial data
- [ ] **Backup system** configured
- [ ] **Monitoring** set up
- [ ] **Team trained** on maintenance
- [ ] **Go-live announcement** ready

---

## 🚀 **Launch Command**

```bash
# Final launch sequence
echo "🚀 Launching USIU Major Advisor System..."

# Start services
sudo systemctl start usiu-advisor
sudo systemctl start nginx

# Verify
curl -I https://your-domain.com

echo "✅ System live at https://your-domain.com"
echo "🎓 Ready to help USIU students choose their majors!"
```

---

*Deployment Guide - USIU Major Advisor System*  
*March 2026 - Production Ready* 🚀</content>
<parameter name="filePath">c:\Users\PC\OneDrive - United States International University (USIU)\Desktop\USIU-NOTES\USIU-NOTES 2026\APT4900\secured site\secured site\DEPLOYMENT_GUIDE.md