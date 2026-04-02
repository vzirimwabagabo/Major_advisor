"""
Migrate data from CSV file and JSON file to PostgreSQL database.
Run this once to import existing data into the proper database.

Usage:
    python migrate_to_db.py
"""

import os
import csv
import json
import sys
from datetime import datetime
from app import app, db, User, Result

def migrate_csv_to_db():
    """Migrate recommendations from CSV to database."""
    csv_file = 'student_recommendation_data.csv'
    
    if not os.path.exists(csv_file):
        print(f"⚠️  CSV file not found: {csv_file}")
        return 0
    
    count = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Find or create user
                    username = row.get('username', 'unknown')
                    email = row.get('email', f"{username}@usiu.ac.ke")
                    
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        user = User(username=username, email=email)
                        user.set_password('default_password')  # Set a secure password
                        db.session.add(user)
                        db.session.flush()  # Get user ID
                    
                    # Create recommendation record
                    major = row.get('recommended_major', '')
                    school = row.get('school', '')
                    confidence = float(row.get('confidence', 0)) if row.get('confidence') else 0
                    timestamp_str = row.get('timestamp', '')
                    
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        timestamp = datetime.utcnow()
                    
                    # Check if record already exists
                    existing = Result.query.filter_by(
                        user_id=user.id,
                        major=major,
                        timestamp=timestamp
                    ).first()
                    
                    if not existing:
                        result = Result(
                            major=major,
                            school=school,
                            confidence=confidence,
                            timestamp=timestamp,
                            user_id=user.id
                        )
                        db.session.add(result)
                        count += 1
                except Exception as e:
                    print(f"❌ Error processing row: {e}")
                    continue
        
        db.session.commit()
        print(f"✅ Successfully migrated {count} records from CSV to database!")
        return count
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error during migration: {e}")
        return 0

def migrate_json_to_db():
    """Migrate recommendations from JSON file to database."""
    json_file = 'data/recommendations.json'
    
    if not os.path.exists(json_file):
        print(f"⚠️  JSON file not found: {json_file}")
        return 0
    
    count = 0
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        for record in records:
            try:
                user_id = record.get('user_id')
                if not user_id:
                    continue
                
                user = User.query.get(user_id)
                if not user:
                    continue
                
                # Check if record already exists
                existing = Result.query.filter_by(
                    user_id=user_id,
                    major=record.get('major')
                ).first()
                
                if not existing:
                    result = Result(
                        major=record.get('major', ''),
                        school=record.get('school', ''),
                        confidence=float(record.get('confidence', 0)) if record.get('confidence') else 0,
                        timestamp=datetime.fromisoformat(record.get('timestamp', datetime.utcnow().isoformat())),
                        user_id=user_id
                    )
                    db.session.add(result)
                    count += 1
            except Exception as e:
                print(f"❌ Error processing JSON record: {e}")
                continue
        
        db.session.commit()
        print(f"✅ Successfully migrated {count} records from JSON to database!")
        return count
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error during JSON migration: {e}")
        return 0

def main():
    """Run all migrations."""
    with app.app_context():
        # Create tables if they don't exist
        print("📦 Creating database tables...")
        db.create_all()
        print("✅ Database tables ready!")
        
        print("\n🔄 Starting migration...")
        csv_count = migrate_csv_to_db()
        json_count = migrate_json_to_db()
        
        total = csv_count + json_count
        print(f"\n✅ Migration complete! Total records imported: {total}")
        
        # Show summary
        print("\n📊 Database Summary:")
        print(f"  - Total users: {User.query.count()}")
        print(f"  - Total recommendations: {Result.query.count()}")

if __name__ == '__main__':
    main()
