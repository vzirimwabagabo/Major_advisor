from app import app, db, User

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@usiu.ac.ke', is_admin=True)
        admin.set_password('admin123')  # Change this!
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin already exists")
exit()