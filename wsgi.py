"""
Production WSGI entry point for Gunicorn and other WSGI servers.

This file should be used to run the application in production environments.
Do NOT use this file for development - use app.py directly instead.

Example usage with Gunicorn:
    gunicorn wsgi:app
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

For Vercel deployment, this will be automatically used.
"""

import os
from app import app, db

# Ensure we're in production mode
os.environ.setdefault('FLASK_ENV', 'production')

if __name__ == '__main__':
    # This should not be called directly - WSGI servers will call app directly
    print("ERROR: Do not run wsgi.py directly!")
    print("Use a WSGI server like Gunicorn:")
    print("  gunicorn wsgi:app")
    raise RuntimeError("wsgi.py is for WSGI servers only")
