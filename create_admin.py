"""
USIU-Africa Major Advisor — Admin Account Management Utility
Allows creating new admin accounts or promoting existing registered users to Admin.
Works with both local SQLite and Supabase PostgreSQL.
"""

import sys
import getpass
from app import app, db, User, validate_password

# Configure UTF-8 for console output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def list_users():
    """Display all registered users and their admin status."""
    with app.app_context():
        users = User.query.order_by(User.id).all()
        if not users:
            print("\n[INFO] No users found in database.")
            return []

        print("\n" + "=" * 65)
        print(f"{'ID':<5} {'Username':<22} {'Email':<30} {'Role'}")
        print("=" * 65)
        for u in users:
            role = "👑 ADMIN" if u.is_admin else "👤 Student"
            print(f"{u.id:<5} {u.username[:20]:<22} {u.email[:28]:<30} {role}")
        print("=" * 65 + "\n")
        return users


def promote_user(identifier):
    """Promote an existing user to Admin by email or username."""
    with app.app_context():
        user = User.query.filter(
            (User.email == identifier.strip().lower()) |
            (User.username == identifier.strip())
        ).first()

        if not user:
            print(f"\n[ERROR] User '{identifier}' not found in database.")
            return False

        if user.is_admin:
            print(f"\n[INFO] {user.username} ({user.email}) is ALREADY an Administrator.")
            return True

        user.is_admin = True
        db.session.commit()
        print(f"\n[SUCCESS] Successfully promoted '{user.username}' ({user.email}) to Administrator!")
        return True


def create_new_admin(username, email, password):
    """Create a new Admin account from scratch."""
    with app.app_context():
        email = email.strip().lower()
        username = username.strip()

        # Check duplicates
        if User.query.filter_by(email=email).first():
            print(f"\n[ERROR] An account with email '{email}' already exists.")
            return False

        if User.query.filter_by(username=username).first():
            print(f"\n[ERROR] Username '{username}' is already taken.")
            return False

        # Validate password strength
        pw_err = validate_password(password)
        if pw_err:
            print(f"\n[ERROR] Weak password: {pw_err}")
            return False

        new_admin = User(
            username=username,
            email=email,
            is_admin=True
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

        print(f"\n[SUCCESS] Administrator account '{username}' ({email}) created successfully!")
        return True


def interactive_menu():
    print("\n==================================================")
    print("  USIU-Africa Major Advisor — Admin Manager")
    print("==================================================")
    print("1. View all users & admin status")
    print("2. Promote an existing user to Admin")
    print("3. Create a brand new Admin account")
    print("4. Exit")
    print("==================================================")

    choice = input("Select an option (1-4): ").strip()

    if choice == "1":
        list_users()

    elif choice == "2":
        users = list_users()
        if not users:
            return
        identifier = input("Enter the Username or Email of the user to promote: ").strip()
        if identifier:
            promote_user(identifier)

    elif choice == "3":
        print("\n--- Create New Admin Account ---")
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email address: ").strip()
        password = getpass.getpass("Enter secure password (min 8 chars, 1 uppercase, 1 number, 1 symbol): ")
        confirm_pw = getpass.getpass("Confirm password: ")

        if password != confirm_pw:
            print("\n[ERROR] Passwords do not match. Aborting.")
            return

        create_new_admin(username, email, password)

    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("[ERROR] Invalid choice. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    # Support command line args for non-interactive use:
    # python create_admin.py --promote <email_or_username>
    # python create_admin.py --list
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_users()
        elif sys.argv[1] == "--promote" and len(sys.argv) > 2:
            promote_user(sys.argv[2])
        else:
            print("Usage:")
            print("  python create_admin.py                (Interactive menu)")
            print("  python create_admin.py --list         (List users)")
            print("  python create_admin.py --promote <email_or_username>")
    else:
        interactive_menu()
