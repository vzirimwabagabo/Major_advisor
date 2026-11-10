# 🐘 Supabase PostgreSQL Setup & Deployment Guide

This project supports **Supabase PostgreSQL** for robust, production-grade persistence.

---

## 🚀 Quick Setup with Supabase (3-Step Guide)

### Step 1: Create a Supabase Project
1. Go to **[supabase.com](https://supabase.com)** and sign in / sign up.
2. Click **New Project**.
3. Choose an organization, project name (e.g. `usiu-major-advisor`), database password, and preferred region (e.g., `eu-central-1` or closest to Nairobi).
4. Wait 1-2 minutes for Supabase to provision your PostgreSQL instance.

---

### Step 2: Retrieve Your Connection URI
1. In your Supabase Dashboard, go to **Project Settings** (gear icon) → **Database**.
2. Scroll to the **Connection string** section.
3. Select **URI** mode.
4. Copy the URI. It will look like:
   ```text
   postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```
   *(Note: Remember to replace `[YOUR-PASSWORD]` with the actual database password you chose in Step 1).*

---

### Step 3: Configure `.env`
Create a `.env` file in the root of the project:

```env
FLASK_ENV=development
FLASK_DEBUG=True

# Generate a strong 64-char key:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=paste_your_generated_secret_here

# Supabase PostgreSQL Connection String:
DATABASE_URL=postgresql://postgres.yourprojectref:yourpassword@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

# Google Gemini API key:
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🛡️ Automatic Schema Initialization
When you start the application with `python run_waitress.py`, the system automatically:
1. Connects to Supabase with SSL enforced (`sslmode=require`).
2. Cleans query strings that cause driver parameter incompatibilities.
3. Creates all three database tables automatically:
   - **`user`**: User accounts (username, email, bcrypt password hash with 128-byte safety, admin flag).
   - **`result`**: Student recommendations history with foreign key to user.
   - **`audit_log`**: Security audit log tracking administrative role changes and deletions.

---

## 🔒 Security Best Practices Implemented
- **SSL Required**: All PostgreSQL network connections require encrypted transit (`sslmode=require`).
- **Connection Pooling**: Serverless and multithreaded pool recycling prevents connection exhaustion.
- **CSRF Protection**: All POST endpoints are protected by Flask-WTF synchronized tokens.
- **Brute Force Defense**: Login and registration endpoints are protected with strict IP rate limiting.
- **XSS Sanitization**: All AI-generated advice is scrubbed with `bleach` to strip malicious scripts and event handlers.
- **Zero PII Logging**: Offline CSV training dataset replaces raw student emails with irreversible cryptographic hashes.
