import os
import sys
from waitress import serve
from app import app, db

# Configure utf-8 encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if __name__ == "__main__":
    # Ensure database schema is initialized
    with app.app_context():
        db.create_all()
        print("[OK] Database tables verified/created.")

    port = int(os.environ.get("PORT", 8080))
    print(f"[START] Starting USIU-Africa Major Advisor on http://localhost:{port}")
    serve(app, host="0.0.0.0", port=port, threads=4)
