from flask import Flask, render_template, url_for, redirect, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from recommendations import (
    get_major_by_rules, determine_best_fit, check_eligibility,
    MAJOR_TO_SCHOOL, INTEREST_MAP, VALID_GRADES, generate_report,
    parse_grade_input, analyze_interest_text
)
from ai_interest_analyzer import analyze_interest_text_advanced, get_major_recommendation
from model_training import save_recommendation_data, get_recommendation_statistics
from datetime import datetime
from sqlalchemy import func, desc
import os
import csv
from io import StringIO

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed - using system env vars

# --- App Configuration ---
app = Flask(__name__)

# Load environment-based configuration
ENV = os.getenv('FLASK_ENV', 'production')
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Security configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'usiu_africa_secret_key_2024')
app.config['SESSION_COOKIE_SECURE'] = not DEBUG  # Only send cool over HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript from accessing the session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# Database configuration
db_uri = os.getenv('DATABASE_URL')
if not db_uri:
    # Use SQLite for development/testing
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_uri = f'sqlite:///{os.path.join(instance_path, "site.db")}'

# Handle SQLAlchemy 3.x PostgreSQL URI format
if db_uri and db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,  # Recycle connections every 5 minutes
    'pool_pre_ping': True,  # Test connections before using them
}

# --- Initialize Extensions ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access the AI Advisor."

# --- Security Headers (Production) ---
if not DEBUG:
    try:
        from flask_talisman import Talisman
        Talisman(app, 
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy={
                    'default-src': "'self'",
                    'script-src': "'self' 'unsafe-inline'",  # Allow inline for Flask templates
                    'style-src': "'self' 'unsafe-inline'",
                    'img-src': "'self' data:",
                    'font-src': "'self'",
                })
    except ImportError:
        print("Warning: Flask-Talisman not installed. Security headers disabled.")
        print("Install it with: pip install Flask-Talisman")

# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    results = db.relationship('Result', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- Routes ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/history')
@login_required
def history():
    user_results = Result.query.filter_by(user_id=current_user.id).order_by(Result.timestamp.desc()).all()
    return render_template('history.html', results=user_results)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    # Get statistics from both database and CSV data
    db_stats = {
        'total_users': User.query.count(),
        'total_recommendations': Result.query.count(),
        'recent_activity': Result.query.order_by(Result.timestamp.desc()).limit(5).all()
    }
    
    csv_stats = get_recommendation_statistics()
    
    stats = {**db_stats, **csv_stats}
    
    return render_template('admin.html', users=users, stats=stats)

@app.route('/toggle_admin/<int:user_id>')
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('Access Denied.', 'danger')
        return redirect(url_for('index'))
    
    user = db.session.get(User, user_id)
    if user:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status updated for {user.username}.', 'success')
    return redirect(url_for('admin'))

# ===== ENHANCED ADMIN ROUTES =====

@app.route('/admin/recommendations')
@login_required
def admin_recommendations():
    """View all student recommendations with search/filter."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    search_query = request.args.get('search', '').strip()
    school_filter = request.args.get('school', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Result.query
    
    # Apply filters
    if search_query:
        query = query.filter(
            (Result.major.ilike(f'%{search_query}%')) |
            (User.username.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        ).join(User)
    else:
        query = query.join(User)
    
    if school_filter:
        query = query.filter(Result.school.ilike(f'%{school_filter}%'))
    
    # Paginate results (20 per page)
    paginated = query.order_by(desc(Result.timestamp)).paginate(page=page, per_page=20)
    
    # Get unique schools for filter dropdown
    schools = db.session.query(Result.school).distinct().all()
    schools = [s[0] for s in schools]
    
    return render_template('admin_recommendations.html', 
                         results=paginated.items,
                         pagination=paginated,
                         schools=schools,
                         search_query=search_query,
                         school_filter=school_filter)

@app.route('/admin/recommendation/<int:rec_id>')
@login_required
def admin_view_recommendation(rec_id):
    """View full details of a specific recommendation."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    result = Result.query.get_or_404(rec_id)
    user = User.query.get(result.user_id)
    
    return render_template('admin_rec_detail.html', result=result, student=user)

@app.route('/admin/recommendation/<int:rec_id>/delete', methods=['GET', 'POST'])
@login_required
def admin_delete_recommendation(rec_id):
    """Delete a recommendation record."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    result = Result.query.get_or_404(rec_id)
    student_name = result.author.username
    
    if request.method == 'POST':
        db.session.delete(result)
        db.session.commit()
        flash(f'✓ Recommendation deleted: {result.major} for {student_name}', 'success')
        return redirect(url_for('admin_recommendations'))
    
    return render_template('admin_confirm_delete.html', result=result, student_name=student_name)

@app.route('/admin/user/<int:user_id>/history')
@login_required
def admin_user_history(user_id):
    """View all recommendations for a specific user."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    results = Result.query.filter_by(user_id=user_id).order_by(desc(Result.timestamp)).all()
    
    return render_template('admin_user_history.html', user=user, results=results)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete a user and all their recommendations."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    if user_id == current_user.id:
        flash('❌ Cannot delete your own account.', 'danger')
        return redirect(url_for('admin'))
    
    user = User.query.get_or_404(user_id)
    username = user.username
    
    # Delete all recommendations for this user
    Result.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    
    flash(f'✓ User {username} and all their data have been deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    """View analytics and insights."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    # Get analytics data
    total_recommendations = Result.query.count()
    total_users = User.query.count()
    
    # Top recommended majors
    top_majors = db.session.query(
        Result.major, 
        func.count(Result.id).label('count')
    ).group_by(Result.major).order_by(desc(func.count(Result.id))).limit(10).all()
    
    # Top schools
    top_schools = db.session.query(
        Result.school,
        func.count(Result.id).label('count')
    ).group_by(Result.school).order_by(desc(func.count(Result.id))).all()
    
    # Average confidence by major
    avg_confidence = db.session.query(
        Result.major,
        func.avg(Result.confidence).label('avg_conf')
    ).group_by(Result.major).order_by(desc(func.avg(Result.confidence))).limit(10).all()
    
    # Recommendations by date (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = Result.query.filter(Result.timestamp >= week_ago).count()
    
    analytics_data = {
        'total_recommendations': total_recommendations,
        'total_users': total_users,
        'top_majors': top_majors,
        'top_schools': top_schools,
        'avg_confidence': avg_confidence,
        'last_week_count': recent_count,
        'csv_stats': get_recommendation_statistics()
    }
    
    return render_template('admin_analytics.html', analytics=analytics_data)

@app.route('/admin/export-data')
@login_required
def admin_export_data():
    """Export all recommendations to CSV."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    results = Result.query.join(User).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Recommendation ID', 'Student Username', 'Student Email', 'Major Recommended',
        'School', 'Confidence %', 'Timestamp', 'Date (YYYY-MM-DD)', 'Time'
    ])
    
    # Write data
    for result in results:
        timestamp = result.timestamp
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H:%M:%S')
        writer.writerow([
            result.id,
            result.author.username,
            result.author.email,
            result.major,
            result.school,
            round(result.confidence, 2),
            timestamp.isoformat(),
            date_str,
            time_str
        ])
    
    # Create response
    mem = StringIO()
    mem.write(output.getvalue())
    mem.seek(0)
    
    return render_template('export_data.html', csv_data=output.getvalue())

@app.route('/admin/export-csv')
@login_required
def download_csv():
    """Download recommendations as CSV file."""
    if not current_user.is_admin:
        flash('Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    
    results = Result.query.join(User).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Username', 'Email', 'Major', 'School', 'Confidence', 'Date', 'Time'
    ])
    
    # Write data
    for result in results:
        timestamp = result.timestamp
        writer.writerow([
            result.id,
            result.author.username,
            result.author.email,
            result.major,
            result.school,
            round(result.confidence, 2),
            timestamp.strftime('%Y-%m-%d'),
            timestamp.strftime('%H:%M:%S')
        ])
    
    response_output = output.getvalue()
    output.close()
    
    # Create response with headers for download
    from flask import Response
    return Response(
        response_output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=recommendations_export.csv'}
    )

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # ===== 1. CAPTURE AND VALIDATE INPUTS =====
        # Parse flexible grade inputs
        math_pt = parse_grade_input(request.form.get('math', '').strip())
        eng_pt = parse_grade_input(request.form.get('english', '').strip())
        kisw_pt = parse_grade_input(request.form.get('kiswahili', '').strip())
        bio_pt = parse_grade_input(request.form.get('biology', '').strip()) if request.form.get('biology', '').strip() else 0
        phy_pt = parse_grade_input(request.form.get('physics', '').strip()) if request.form.get('physics', '').strip() else 0
        chem_pt = parse_grade_input(request.form.get('chemistry', '').strip()) if request.form.get('chemistry', '').strip() else 0
        hum_pt = parse_grade_input(request.form.get('humanities', '').strip())
        tech_pt = parse_grade_input(request.form.get('tech_bus', '').strip()) if request.form.get('tech_bus', '').strip() else 0
        
        # Analyze natural language interest input using AI analyzer
        interest_text = request.form.get('interest', '').strip()
        
        # First try advanced AI analysis
        ai_category, ai_confidence, ai_keywords, ai_reasoning = analyze_interest_text_advanced(interest_text, scores)
        
        # Map AI category to legacy code format for compatibility
        category_to_code = {
            "Technology & Engineering": 0,
            "Health Sciences": 1,
            "Business & Commerce": 2,
            "Humanities & Social Sciences": 3,
            "Creative Arts & Media": 4,
            "Undecided": -1
        }
        
        interest_code = category_to_code.get(ai_category, -1)
        detected_interests = ai_keywords

        # ===== 2. VALIDATE COMPULSORY SUBJECTS =====
        if math_pt == 0 or eng_pt == 0 or kisw_pt == 0:
            flash('❌ Group I subjects (Math, English, Kiswahili) are COMPULSORY in KCSE. Please enter valid grades.', 'danger')
            return redirect(url_for('index'))
        
        if hum_pt == 0:
            flash('❌ Please enter a valid grade for your Humanities subject.', 'danger')
            return redirect(url_for('index'))

        # ===== 3. PREPARE SCORES DICTIONARY =====
        scores = {
            'math': math_pt,
            'english': eng_pt,
            'kiswahili': kisw_pt,
            'biology': bio_pt,
            'physics': phy_pt,
            'chemistry': chem_pt,
            'humanities': hum_pt,
            'tech_business': tech_pt
        }

        # ===== 4. DETERMINE INTEREST AND ELIGIBILITY =====
        if interest_code == -1:  # Undecided/unclear interests
            # For undecided: calculate best fit
            interest_code_alt, best_fit, field_scores = determine_best_fit(scores)
            final_interest_code = interest_code_alt
            is_eligible = True
            guidance_msg = ""
            undecided_mode = True
            alternative_msg = f"Based on your description, we analyzed your interests and academic strengths. Your best fit appears to be in <strong>{best_fit}</strong>."
        else:
            # For decided students: check eligibility
            is_eligible, guidance_msg = check_eligibility(interest_code, scores)
            undecided_mode = False
            alternative_msg = ""

        # ===== 5. PIVOT LOGIC: If not eligible, find best alternative =====
        final_interest_code = interest_code
        if not is_eligible:
            # Student doesn't meet requirements for their choice
            # Find what they're best suited for instead
            interest_code_alt, best_fit_area, _ = determine_best_fit(scores)
            final_interest_code = interest_code_alt
            alternative_msg = (f"<strong>Guidance Note:</strong> {guidance_msg}<br><br>"
                              f"<strong>Don't be discouraged!</strong> Everyone has different strengths. "
                              f"Based on your actual scores, you show excellent potential in "
                              f"<strong>{best_fit_area}</strong>. This path offers fantastic opportunities!")

        # ===== 6. GET RECOMMENDATION USING RULES =====
        major, explanation, confidence = get_major_by_rules(scores, final_interest_code)
        school = MAJOR_TO_SCHOOL.get(major, "USIU-Africa")

        # ===== 7. SAVE TO DATABASE (History) =====
        new_result = Result(
            major=major,
            school=school,
            confidence=confidence,
            user_id=current_user.id
        )
        db.session.add(new_result)
        db.session.commit()

        # ===== 8. SAVE TO CSV FOR DATA COLLECTION =====
        student_data = {
            'username': current_user.username,
            'email': current_user.email,
            'math': math_pt,
            'english': eng_pt,
            'kiswahili': kisw_pt,
            'biology': bio_pt,
            'physics': phy_pt,
            'chemistry': chem_pt,
            'humanities': hum_pt,
            'tech_business': tech_pt,
            'interest_raw': interest_text,  # Store raw interest text
            'interest_detected': detected_interests,  # Store detected interests
            'recommended_major': major,
            'school': school,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
        save_recommendation_data(student_data)

        # ===== 9. PREPARE DISPLAY DATA =====
        input_summary = {
            'Math': f"{request.form.get('math', 'N/A')} ({math_pt}pts)",
            'English': f"{request.form.get('english', 'N/A')} ({eng_pt}pts)",
            'Kiswahili': f"{request.form.get('kiswahili', 'N/A')} ({kisw_pt}pts)",
            'Biology': f"{request.form.get('biology', 'N/A')} ({bio_pt}pts)" if bio_pt > 0 else "Not Taken",
            'Physics': f"{request.form.get('physics', 'N/A')} ({phy_pt}pts)" if phy_pt > 0 else "Not Taken",
            'Chemistry': f"{request.form.get('chemistry', 'N/A')} ({chem_pt}pts)" if chem_pt > 0 else "Not Taken",
            'Humanities': f"{request.form.get('humanities', 'N/A')} ({hum_pt}pts)",
            'Tech/Business': f"{request.form.get('tech_bus', 'N/A')} ({tech_pt}pts)" if tech_pt > 0 else "Not Taken",
            'Your Interests': f'"{interest_text[:50]}..."' if len(interest_text) > 50 else f'"{interest_text}"'
        }

        # Combine explanations
        full_explanation = alternative_msg if alternative_msg else explanation

        return render_template('index.html',
                             result=major,
                             school=school,
                             confidence=round(confidence, 1),
                             explanation=full_explanation,
                             input_summary=input_summary,
                             show_results=True,
                             is_alternative=not is_eligible)

    except KeyError as e:
        flash(f"❌ Missing form field: {e}", 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"❌ Error processing recommendation: {str(e)}", 'danger')
        return redirect(url_for('index'))

# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user_email = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(username=username).first()
        
        if user_email or user_name:
            flash('Email or Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Allow users to delete their own account"""
    if request.method == 'POST':
        # Verify password before deletion
        password = request.form.get('password', '')

        if not current_user.check_password(password):
            flash('Incorrect password. Account deletion cancelled.', 'danger')
            return redirect(url_for('delete_account'))

        # Prevent admin from deleting their own account if they're the only admin
        if current_user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                flash('Cannot delete the last admin account. Please promote another user to admin first.', 'danger')
                return redirect(url_for('delete_account'))

        try:
            # Get user ID before logout
            user_id = current_user.id
            username = current_user.username

            # Delete all user's recommendations first (due to foreign key constraint)
            Result.query.filter_by(user_id=user_id).delete()

            # Delete the user
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()

            # Log out the user
            logout_user()

            flash(f'Account "{username}" has been permanently deleted.', 'info')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting your account. Please try again.', 'danger')
            return redirect(url_for('delete_account'))

    # GET request - show confirmation form
    return render_template('delete_account.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Only use development server if explicitly enabled
    if DEBUG or ENV == 'development':
        print(f"Starting Flask development server (debug={DEBUG})")
        print("WARNING: This is a development server. Do not use it in a production deployment.")
        print("Use a production WSGI server instead (e.g., gunicorn).")
        app.run(debug=DEBUG, host='127.0.0.1', port=5000)
    else:
        print("ERROR: This should not run directly in production.")
        print("Use Gunicorn or another WSGI server:")
        print("  gunicorn wsgi:app")
        raise RuntimeError("Development app.py entry point should not be used in production")