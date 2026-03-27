#!/bin/bash

# 🚀 USIU Major Advisor - Automated Deployment Script
# Run this on a fresh Ubuntu 22.04 LTS server

set -e  # Exit on any error

echo "🚀 Starting USIU Major Advisor Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - EDIT THESE VALUES
DOMAIN="your-domain.com"
ADMIN_EMAIL="admin@usiu.ac.ke"
ADMIN_PASSWORD="secure_admin_password_2026"
DB_PASSWORD="secure_db_password_2026"
SECRET_KEY="your-very-secure-secret-key-change-this-2026"

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib curl git ufw

# Install Certbot for SSL
echo -e "${YELLOW}📦 Installing Certbot for SSL...${NC}"
sudo apt install snapd -y
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Setup PostgreSQL
echo -e "${YELLOW}🗄️ Setting up PostgreSQL database...${NC}"
sudo -u postgres psql -c "CREATE DATABASE usiu_advisor;" || true
sudo -u postgres psql -c "CREATE USER advisor_user WITH PASSWORD '$DB_PASSWORD';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE usiu_advisor TO advisor_user;" || true

# Create application directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
sudo mkdir -p /var/www/usiu-advisor
sudo chown -R $USER:$USER /var/www/usiu-advisor
cd /var/www/usiu-advisor

# Clone repository (replace with your actual repo)
echo -e "${YELLOW}📥 Cloning application repository...${NC}"
git clone https://github.com/vzirimwabagabo/Major_advisor.git .
cd "secured site"

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-dotenv

# Create .env file
echo -e "${YELLOW}⚙️ Creating environment configuration...${NC}"
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://advisor_user:$DB_PASSWORD@localhost/usiu_advisor
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF

# Update app.py for production database
echo -e "${YELLOW}🗄️ Updating database configuration...${NC}"
sed -i "s|'sqlite:///site.db'|'postgresql://advisor_user:$DB_PASSWORD@localhost/usiu_advisor'|g" app.py

# Create database tables and admin user
echo -e "${YELLOW}👤 Creating database and admin user...${NC}"
python3 -c "
from app import app, db, User
import os
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://advisor_user:$DB_PASSWORD@localhost/usiu_advisor'
with app.app_context():
    db.create_all()
    # Check if admin exists
    admin = User.query.filter_by(email='$ADMIN_EMAIL').first()
    if not admin:
        admin = User(username='admin', email='$ADMIN_EMAIL', is_admin=True)
        admin.set_password('$ADMIN_PASSWORD')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created')
    else:
        print('✅ Admin user already exists')
"

# Create Gunicorn configuration
echo -e "${YELLOW}⚙️ Creating Gunicorn configuration...${NC}"
cat > gunicorn.conf.py << EOF
bind = '127.0.0.1:8000'
workers = 3
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
EOF

# Create systemd service
echo -e "${YELLOW}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/usiu-advisor.service > /dev/null << EOF
[Unit]
Description=USIU Major Advisor Flask App
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/usiu-advisor/secured site
Environment=PATH=/var/www/usiu-advisor/secured site/venv/bin
Environment=FLASK_ENV=production
ExecStart=/var/www/usiu-advisor/secured site/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Set proper permissions
echo -e "${YELLOW}🔒 Setting proper permissions...${NC}"
sudo chown -R www-data:www-data /var/www/usiu-advisor
sudo chmod -R 755 /var/www/usiu-advisor

# Create Nginx configuration
echo -e "${YELLOW}🌐 Creating Nginx configuration...${NC}"
sudo tee /etc/nginx/sites-available/usiu-advisor > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static {
        alias /var/www/usiu-advisor/secured site/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Enable Nginx site
echo -e "${YELLOW}🌐 Enabling Nginx site...${NC}"
sudo ln -sf /etc/nginx/sites-available/usiu-advisor /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${YELLOW}🌐 Testing Nginx configuration...${NC}"
sudo nginx -t

# Configure firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force reload

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable usiu-advisor
sudo systemctl start usiu-advisor
sudo systemctl enable nginx
sudo systemctl start nginx

# Get SSL certificate (optional - requires domain pointing to server)
echo -e "${YELLOW}🔒 Attempting to get SSL certificate...${NC}"
if curl -s --head "http://$DOMAIN" | grep "200 OK" > /dev/null; then
    echo -e "${GREEN}✅ Domain is pointing to this server, getting SSL certificate...${NC}"
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $ADMIN_EMAIL || true
else
    echo -e "${YELLOW}⚠️ Domain not yet pointing to server. Run SSL setup manually after DNS is configured:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

# Final verification
echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo ""
echo -e "${GREEN}📊 Deployment Summary:${NC}"
echo "🌐 Domain: http://$DOMAIN"
echo "👤 Admin Email: $ADMIN_EMAIL"
echo "🔑 Admin Password: $ADMIN_PASSWORD"
echo "🗄️ Database: PostgreSQL (usiu_advisor)"
echo ""
echo -e "${YELLOW}🔍 Verification Commands:${NC}"
echo "sudo systemctl status usiu-advisor"
echo "sudo systemctl status nginx"
echo "curl -I http://localhost"
echo ""
echo -e "${GREEN}✅ USIU Major Advisor is now live!${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Point your domain DNS to this server's IP"
echo "2. Run SSL certificate setup if not done automatically"
echo "3. Test the application at https://$DOMAIN"
echo "4. Configure monitoring and backups"
echo "5. Set up automated updates"</content>
<parameter name="filePath">c:\Users\PC\OneDrive - United States International University (USIU)\Desktop\USIU-NOTES\USIU-NOTES 2026\APT4900\secured site\secured site\deploy.sh