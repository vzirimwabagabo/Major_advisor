# PostgreSQL Database Setup for Vercel

Your app now uses a **proper PostgreSQL database** instead of CSV files! 

## Why PostgreSQL?

✅ **Scalable** - Handle thousands of users
✅ **Reliable** - ACID compliance, data integrity
✅ **Performant** - Optimized queries
✅ **Production-ready** - Industry standard
✅ **Free with Vercel** - Included with your hosting!

---

## Quick Setup (5 minutes)

### Step 1: Add Vercel Postgres to Your Project

1. Go to: **https://vercel.com/dashboard**
2. Select your project → **Storage** tab
3. Click **"Create Database"** → Select **Postgres**
4. Choose **Free tier** (Supports development/student projects)
5. Vercel automatically creates `POSTGRES_URL_NON_POOLING` environment variable ✅

### Step 2: Update Your Environment Variables

**Locally (.env file - for development):**
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
# Leave DATABASE_URL blank for SQLite locally
# DATABASE_URL=  (uses SQLite by default)
```

**On Vercel (automatic):**
- Vercel sets `POSTGRES_URL_NON_POOLING` automatically ✅
- Your app uses it automatically ✅

### Step 3: Deploy to Vercel

```bash
git add migrate_to_db.py requirements.txt
git commit -m "Add PostgreSQL support and migration script"
git push origin main
```

Vercel will auto-redeploy!

### Step 4: Migrate Data (First Time Only)

After deployment, your data from CSV will be stored in the **database** going forward:

**Local migration (optional):**
```bash
python migrate_to_db.py
```

**Production migration:**
- Run via Vercel's environment variables
- Or contact support to execute

---

## How It Works

### Before (CSV-based - ❌ Old)
```
User Input → Save to CSV → Read from CSV
```

### After (Database-based - ✅ New)
```
User Input → SQLAlchemy ORM → PostgreSQL Database
            ↓
         Automatically stored
```

---

## Database Tables

Your PostgreSQL database now has:

### `user` table
```
id          | Integer (Primary Key)
username    | String (Unique)
email       | String (Unique)
password_hash | String
is_admin    | Boolean
```

### `result` table
```
id          | Integer (Primary Key)
major       | String
school      | String
confidence  | Float
timestamp   | DateTime
user_id     | Integer (Foreign Key → user.id)
```

---

## Data Migration

### Option A: Automatic (Recommended)

The app **automatically saves to database** for all NEW recommendations after deployment!

### Option B: Manual Migration from CSV

```bash
# Run migration script to move existing CSV data to database
python migrate_to_db.py
```

This will:
- ✅ Read all data from `student_recommendation_data.csv`
- ✅ Read all data from `data/recommendations.json`
- ✅ Import into PostgreSQL database
- ✅ Show summary of migrated records

---

## Verification

### Check Database is Working

1. **On Vercel Dashboard:**
   - Go to Storage → Postgres
   - Click **"Browse"** tab
   - You should see `user` and `result` tables ✅

2. **Test the App:**
   - Create a new user account
   - Get a recommendation
   - Check app: **Admin → Analytics**
   - Should show recommendations in the database ✅

---

## Production Environment Variables

On Vercel, these are automatically set:
- `POSTGRES_URL_NON_POOLING` - Connection string
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- `SECRET_KEY` (set manually in dashboard)

---

## Connection String Format

Your PostgreSQL URL looks like:
```
postgresql://user:password@host:5432/database_name
```

Vercel automatically provides this as `POSTGRES_URL_NON_POOLING`

---

## File Changes Made

✅ `migrate_to_db.py` - Data migration script
✅ `requirements.txt` - Added psycopg2 (PostgreSQL driver)
✅ `app.py` - Already configured for PostgreSQL via DATABASE_URL
✅ `.env.example` - Updated with database info

---

## Troubleshooting

### "Cannot connect to database"
- Verify Postgres addon is created in Vercel dashboard
- Check that POSTGRES_URL_NON_POOLING environment variable exists
- Redeploy after adding the database

### "No such table: user"
- Run migration: `python migrate_to_db.py`
- Or the app's first request will auto-create tables

### "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### SQLite still being used
- Check that `DATABASE_URL` environment variable is set
- If not set, app defaults to SQLite (good for development!)

---

## Performance Tips

✅ **Vercel Postgres Free Tier includes:**
- 256 MB storage
- Up to 60 connections
- Automated backups

**For scaling:**
- Upgrade to Pro tier if you outgrow free tier
- Or migrate to dedicated PostgreSQL hosting (AWS RDS, Railway, etc.)

---

## Next Steps

1. ✅ Add Vercel Postgres to your project
2. ✅ Deploy with `git push`
3. ✅ Verify database works
4. ⏳ (Optional) Run migration: `python migrate_to_db.py`

**Your database-driven system is ready!** 🚀
