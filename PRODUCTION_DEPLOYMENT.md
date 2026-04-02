# Production Deployment Guide

## Overview
This application is now configured for production deployment. This guide covers the essential steps to deploy securely.

## Key Changes for Production

### 1. **WSGI Server Integration**
- ✅ Created `wsgi.py` - the production entry point
- ✅ Removed `debug=True` from Flask app
- ✅ Added environment-based configuration

**Never use the development server (`python app.py`) in production**

### 2. **Security Configuration**
- ✅ Session cookies are now HTTPS-only in production
- ✅ Session cookies are HTTP-only (prevents JavaScript access)
- ✅ CSRF protection enabled via SameSite cookies
- ✅ Security headers implemented via Flask-Talisman
- ✅ Secret key should be changed via environment variables

### 3. **Environment Configuration**
Environment variables are now properly supported. Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Then edit `.env` with your production values:
- `SECRET_KEY` - Change this to a secure random value
- `DATABASE_URL` - Your production database
- `FLASK_ENV` - Set to "production"
- `FLASK_DEBUG` - Set to "False"

## Deployment Options

### Option A: Vercel (Recommended - Easy)

#### Prerequisites
- Vercel account (free tier works)
- PostgreSQL database (Vercel, AWS RDS, Railway, etc.)
- Git repository

#### Steps
1. **Set up PostgreSQL Database**
   - Create a PostgreSQL database on Vercel Postgres, Railway, Supabase, or AWS RDS
   - Get your DATABASE_URL

2. **Add Environment Variables to Vercel**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=<generate-random-secret-key>
   DATABASE_URL=<your-postgresql-url>
   ```

3. **Deploy**
   ```bash
   npm i -g vercel
   vercel
   ```

### Option B: Heroku

#### Prerequisites
- Heroku account
- PostgreSQL add-on

#### Steps
1. **Create Procfile** (should look like this):
   ```
   web: gunicorn wsgi:app
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   git push heroku main
   ```

### Option C: Local/VPS with Gunicorn

#### Installation
```bash
pip install -r requirements-prod.txt
```

#### Launch (Basic)
```bash
gunicorn wsgi:app
```

#### Launch (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - wsgi:app
```

- `-w 4` - 4 worker processes
- `-b 0.0.0.0:8000` - Bind to all interfaces on port 8000
- `--access-logfile -` - Log to stdout

#### With Systemd (Linux)
Create `/etc/systemd/system/advisor-app.service`:
```ini
[Unit]
Description=AI Advisor Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable advisor-app
sudo systemctl start advisor-app
```

#### With Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Setup

### Local Development (SQLite)
SQLite is used by default if `DATABASE_URL` is not set.

### Production (PostgreSQL)

#### Create Database
```bash
createdb advisor_db
```

#### Connect Flask App
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/advisor_db"
```

#### Initialize Tables
The app automatically creates tables on first run:
```python
with app.app_context():
    db.create_all()
```

## SSL/HTTPS Setup

### Self-Signed Certificate (Testing Only)
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Gunicorn with SSL
```bash
gunicorn -w 4 --certfile=cert.pem --keyfile=key.pem -b 0.0.0.0:443 wsgi:app
```

### Production SSL (Let's Encrypt + Nginx)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

## Monitoring & Logging

### View Logs
```bash
# Systemd
sudo journalctl -u advisor-app.service -f

# Direct output
# Already configured - see Gunicorn launch command
```

### Error Tracking (Optional - Sentry)
1. Sign up at https://sentry.io
2. Create a project for Python
3. Add to environment:
```bash
export SENTRY_DSN="https://your-key@sentry.io/project-id"
```

## Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use PostgreSQL for production (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Set secure database password
- [ ] Use environment variables, not hardcoded secrets
- [ ] Keep dependencies updated
- [ ] Set up regular backups
- [ ] Monitor error logs
- [ ] Use a reverse proxy (Nginx/Apache)
- [ ] Configure firewall
- [ ] Enable CSRF protection (already enabled)
- [ ] Use HTTPS-only cookies (already enabled)

## Running Tests

```bash
flask shell
>>> db.create_all()
>>> # Test queries here
```

## Troubleshooting

### "Production WSGI server" Warning Still Showing
This means you're still using `python app.py`. Use one of the deployment options above instead.

### Database Connection Errors
- Check DATABASE_URL is correct
- Verify database is running
- Check firewall/security groups
- Try: `psql $DATABASE_URL` to test connection

### 502/503 Errors
- Check Gunicorn is running: `ps aux | grep gunicorn`
- Check logs for errors
- Increase worker count: `gunicorn -w 8 wsgi:app`

## Contact & Support
For issues, check the project documentation or create an issue in the repository.
