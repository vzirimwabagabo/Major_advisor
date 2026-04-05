from waitress import serve
from app import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting Waitress production server on http://0.0.0.0:{port}")
    serve(app, host="0.0.0.0", port=port, threads=4)
