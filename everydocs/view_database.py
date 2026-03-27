#!/usr/bin/env python3
"""
Database Viewer for USIU Major Advisor
Shows contents of site.db SQLite database
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    """View all data in the SQLite database"""

    # Database path
    db_path = os.path.join('instance', 'site.db')

    if not os.path.exists(db_path):
        print("❌ Database not found!")
        print(f"Expected location: {db_path}")
        print("Run the Flask app first to create the database.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("🔍 USIU Major Advisor Database Contents")
        print("=" * 50)

        # Show Users table
        print("\n👥 USERS TABLE:")
        print("-" * 30)
        cursor.execute("SELECT id, username, email, is_admin FROM user")
        users = cursor.fetchall()

        if users:
            print(f"{'ID':<3} {'Username':<15} {'Email':<25} {'Admin':<6}")
            print("-" * 50)
            for user in users:
                admin_status = "✅" if user[3] else "❌"
                print(f"{user[0]:<3} {user[1]:<15} {user[2]:<25} {admin_status:<6}")
        else:
            print("No users found.")

        # Show Results table
        print("\n📊 RECOMMENDATIONS TABLE:")
        print("-" * 30)
        cursor.execute("""
            SELECT r.id, u.username, r.major, r.school, r.confidence, r.timestamp
            FROM result r
            JOIN user u ON r.user_id = u.id
            ORDER BY r.timestamp DESC
        """)
        results = cursor.fetchall()

        if results:
            print(f"{'ID':<3} {'User':<15} {'Major':<30} {'School':<20} {'Conf%':<5} {'Date':<12}")
            print("-" * 85)
            for result in results:
                confidence = f"{result[4]:.1f}"
                timestamp = datetime.fromisoformat(result[5]).strftime('%Y-%m-%d')
                print(f"{result[0]:<3} {result[1]:<15} {result[2]:<30} {result[3]:<20} {confidence:<5} {timestamp:<12}")
        else:
            print("No recommendations found.")

        # Show statistics
        print("\n📈 DATABASE STATISTICS:")
        print("-" * 25)

        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM result")
        result_count = cursor.fetchone()[0]

        print(f"Total Users: {user_count}")
        print(f"Total Recommendations: {result_count}")

        if result_count > 0:
            cursor.execute("SELECT AVG(confidence) FROM result")
            avg_conf = cursor.fetchone()[0]
            print(".1f")

            cursor.execute("SELECT major, COUNT(*) as count FROM result GROUP BY major ORDER BY count DESC LIMIT 5")
            top_majors = cursor.fetchall()
            print("\n🏆 TOP 5 MAJORS:")
            for major, count in top_majors:
                print(f"  • {major}: {count} recommendations")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database()