from app import app, db, User
with app.app_context():
    user = User.query.filter_by(email='test_ai@example.com').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print("User test_ai@example.com promoted to admin")
    else:
        print("User not found")
