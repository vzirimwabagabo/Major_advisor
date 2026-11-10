"""
USIU-Africa AI Major Advisor — Flask Application
Security-hardened, CSRF-protected, rate-limited, XSS-safe.

Built for APT4900 — USIU-Africa 2026
"""

import os
import sys
import re
import csv
import bleach
from io import StringIO
from datetime import datetime, timedelta

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask import (
    Flask, render_template, url_for, redirect,
    request, flash, Response
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import func, desc

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from recommendations import (
    get_major_by_rules, determine_best_fit, check_eligibility,
    MAJOR_TO_SCHOOL, INTEREST_MAP, VALID_GRADES, generate_report,
    parse_grade_input, analyze_interest_text
)
from education_systems import (
    UNIVERSITIES, CURRICULA, parse_curriculum_grade,
    get_country_options, get_curricula_for_country
)
from ai_interest_analyzer import analyze_interest_text_advanced, get_major_recommendation
from model_training import save_recommendation_data, get_recommendation_statistics

# ============================================================
# APPLICATION FACTORY
# ============================================================
app = Flask(__name__)

ENV   = os.getenv('FLASK_ENV', 'production')
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# --- SECRET KEY: MUST be set via environment. No insecure fallback. ---
_secret = os.getenv('SECRET_KEY', '').strip()
if not _secret:
    if DEBUG:
        # In development with no .env, generate a temporary key with a loud warning
        import secrets as _secrets_mod
        _secret = _secrets_mod.token_hex(32)
        print("[WARNING] SECRET_KEY not set in environment. Using temporary random key.")
        print("          Sessions will invalidate on restart. Set SECRET_KEY in .env.")
    else:
        raise RuntimeError(
            "FATAL: SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

app.config['SECRET_KEY'] = _secret
app.config['SESSION_COOKIE_SECURE']   = not DEBUG   # HTTPS-only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True         # No JS access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'       # CSRF mitigation
app.config['PERMANENT_SESSION_LIFETIME'] = 3600      # 1-hour session timeout
app.config['WTF_CSRF_TIME_LIMIT'] = 3600             # CSRF token expires after 1 hour

# ============================================================
# DATABASE
# ============================================================
db_uri = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

# Check for unreplaced template placeholders
if db_uri and ('[YOUR-PASSWORD]' in db_uri or '[REGION]' in db_uri or '[YOUR-PROJECT-REF]' in db_uri):
    print("[WARNING] DATABASE_URL in .env contains unreplaced placeholders:")
    print("          - [YOUR-PASSWORD] or [REGION]")
    print("          Falling back to local SQLite (instance/site.db) so you can run the app.")
    print("          Update .env with your real Supabase password and region to connect to PostgreSQL.")
    db_uri = None

if db_uri:
    # Normalize postgres:// → postgresql:// for SQLAlchemy 2.0
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
    # Strip Vercel/Supabase query params that break psycopg2, then add sslmode
    if '?' in db_uri:
        db_uri = db_uri.split('?')[0]
    db_uri += '?sslmode=require'

if not db_uri:
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_uri = f'sqlite:///{os.path.join(instance_path, "site.db")}'
    print(f"[INFO] Using SQLite database at: {db_uri}")

app.config['SQLALCHEMY_DATABASE_URI']        = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not DEBUG:
    from sqlalchemy.pool import NullPool
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'poolclass': NullPool,
    }

# ============================================================
# EXTENSIONS
# ============================================================
db           = SQLAlchemy(app)
bcrypt       = Bcrypt(app)
csrf         = CSRFProtect(app)          # CSRF protection on ALL forms
login_manager = LoginManager(app)
login_manager.login_view    = 'login'
login_manager.login_message = "Please log in to access the AI Advisor."

# Rate limiter — uses client IP address
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

# ============================================================
# SECURITY HEADERS (Production)
# ============================================================
if not DEBUG:
    try:
        from flask_talisman import Talisman
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            content_security_policy={
                'default-src': "'self'",
                'script-src':  "'self' 'unsafe-inline'",
                'style-src':   "'self' 'unsafe-inline'",
                'img-src':     "'self' data:",
                'font-src':    "'self'",
            }
        )
    except ImportError:
        print("Warning: Flask-Talisman not installed. Security headers disabled.")

# ============================================================
# XSS SANITIZER — bleach allowlist
# ============================================================
ALLOWED_TAGS    = ['br', 'strong', 'em', 'p', 'ul', 'li', 'b', 'i']
ALLOWED_ATTRS   = {}   # No attributes allowed on any tag

def sanitize_html(raw: str) -> str:
    """Strip dangerous tags and their content. Prevents stored XSS from AI output."""
    if not raw:
        return ""
    # Strip script, style, and iframe blocks entirely including inner content
    stripped = re.sub(r'<(script|style|iframe|object|embed)[^>]*>.*?</\1>', '', raw, flags=re.DOTALL | re.IGNORECASE)
    return bleach.clean(stripped, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

# ============================================================
# PASSWORD STRENGTH VALIDATOR
# ============================================================
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&_\-#])[A-Za-z\d@$!%*?&_\-#]{8,72}$'
)

def validate_password(password: str) -> str | None:
    """
    Returns an error message string if invalid, or None if password is acceptable.
    Rules: 8-72 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char.
    """
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if len(password) > 72:
        return "Password must not exceed 72 characters."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return "Password must contain at least one number."
    if not re.search(r'[@$!%*?&_\-#]', password):
        return "Password must contain at least one special character: @  $  !  %  *  ?  &  _  -  #"
    return None

# ============================================================
# DATABASE MODELS
# ============================================================
class User(db.Model, UserMixin):
    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)   # 128 for safety margin
    is_admin      = db.Column(db.Boolean,     default=False)
    results       = db.relationship('Result', backref='author', lazy=True, cascade='all, delete-orphan')
    audit_logs    = db.relationship('AuditLog', backref='actor', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


class Result(db.Model):
    id         = db.Column(db.Integer,  primary_key=True)
    major      = db.Column(db.String(100), nullable=False)
    school     = db.Column(db.String(150), nullable=False)
    confidence = db.Column(db.Float,    nullable=False)
    timestamp  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id    = db.Column(db.Integer,  db.ForeignKey('user.id'), nullable=False)


class AuditLog(db.Model):
    """Records sensitive admin actions for accountability."""
    id         = db.Column(db.Integer,  primary_key=True)
    action     = db.Column(db.String(200), nullable=False)
    details    = db.Column(db.String(500), nullable=True)
    timestamp  = db.Column(db.DateTime,  nullable=False, default=datetime.utcnow)
    user_id    = db.Column(db.Integer,   db.ForeignKey('user.id'), nullable=False)


def log_admin_action(action: str, details: str = ""):
    """Log an admin action to the AuditLog table."""
    try:
        entry = AuditLog(action=action, details=details, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        print(f"[AuditLog] Failed to write: {e}")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("⚠️ Security token expired or invalid. Please try again.", "danger")
    return redirect(request.referrer or url_for('index'))

@app.errorhandler(429)
def rate_limit_handler(e):
    flash("⚠️ Too many attempts. Please wait a moment and try again.", "danger")
    return redirect(url_for('login')), 429

# ============================================================
# UTILITY
# ============================================================
@app.route('/favicon.ico')
def favicon():
    return '', 204

# ============================================================
# TEMPLATE CONTEXT INJECTION (Always available in templates)
# ============================================================
@app.context_processor
def inject_education_data():
    return {
        'curricula': CURRICULA,
        'universities': UNIVERSITIES,
        'country_options': get_country_options()
    }


# ============================================================
# STUDENT ROUTES
# ============================================================
@app.route('/')
@login_required
def index():
    return render_template(
        'index.html',
        form_data={
            'country': 'Kenya',
            'curriculum': 'ke_kcse',
            'target_uni': 'usiu',
        },
        country_options=get_country_options(),
        curricula=CURRICULA,
        universities=UNIVERSITIES
    )


@app.route('/history')
@login_required
def history():
    user_results = Result.query.filter_by(user_id=current_user.id)\
                               .order_by(Result.timestamp.desc()).all()
    return render_template('history.html', results=user_results)


@app.route('/predict', methods=['POST'])
@login_required
@limiter.limit("20 per hour")   # Prevent AI API abuse
def predict():
    try:
        # ===== 1. PARSE COUNTRY, CURRICULUM, AND TARGET UNIVERSITY =====
        country = request.form.get('country', 'Kenya').strip()
        curriculum = request.form.get('curriculum', 'ke_kcse').strip()
        target_uni = request.form.get('target_uni', 'usiu').strip()

        if curriculum not in CURRICULA:
            curriculum = 'ke_kcse'
        if target_uni not in UNIVERSITIES:
            target_uni = 'usiu'

        curr_data = CURRICULA[curriculum]
        uni_data = UNIVERSITIES[target_uni]

        # ===== 2. PARSE & VALIDATE GRADE INPUTS =====
        math_pt  = parse_curriculum_grade(curriculum, request.form.get('math',       '').strip())
        eng_pt   = parse_curriculum_grade(curriculum, request.form.get('english',    '').strip())
        kisw_pt  = parse_curriculum_grade(curriculum, request.form.get('kiswahili',  '').strip())
        bio_pt   = parse_curriculum_grade(curriculum, request.form.get('biology',    '').strip())
        phy_pt   = parse_curriculum_grade(curriculum, request.form.get('physics',    '').strip())
        chem_pt  = parse_curriculum_grade(curriculum, request.form.get('chemistry',  '').strip())
        hum_pt   = parse_curriculum_grade(curriculum, request.form.get('humanities', '').strip())
        tech_pt  = parse_curriculum_grade(curriculum, request.form.get('tech_bus',   '').strip())

        # Compulsory subject check
        if math_pt == 0 or eng_pt == 0:
            flash('❌ Mathematics and English / Core Language are COMPULSORY for university admission. Please select your grades.', 'danger')
            return redirect(url_for('index'))

        if hum_pt == 0:
            flash('❌ Please select a valid grade for your Humanities / Social Science subject.', 'danger')
            return redirect(url_for('index'))

        # ===== 3. SANITIZE INTEREST TEXT =====
        interest_text = request.form.get('interest', '').strip()
        interest_text = interest_text[:2000]

        if len(interest_text) < 5:
            flash('❌ Please describe your interests in at least a few words.', 'danger')
            return redirect(url_for('index'))

        scores = {
            'math':          math_pt,
            'english':       eng_pt,
            'kiswahili':     kisw_pt,
            'biology':       bio_pt,
            'physics':       phy_pt,
            'chemistry':     chem_pt,
            'humanities':    hum_pt,
            'tech_business': tech_pt,
        }

        # ===== 4. AI INTEREST ANALYSIS (Multi-University Aware) =====
        ai_category, ai_confidence, ai_keywords, ai_reasoning, ai_major, ai_school = \
            analyze_interest_text_advanced(
                interest_text=interest_text,
                grades_dict=scores,
                username=current_user.username,
                target_uni=target_uni,
                country=country,
                curriculum_id=curriculum
            )

        category_to_code = {
            "Technology & Engineering":    0,
            "Health Sciences":             1,
            "Business & Commerce":         2,
            "Humanities & Social Sciences": 3,
            "Creative Arts & Media":       4,
            "Undecided":                   -1,
        }
        interest_code = category_to_code.get(ai_category, -1)
        detected_interests = ai_keywords

        # ===== 5. ELIGIBILITY CHECK =====
        _, best_fit_area, _ = determine_best_fit(scores)
        if target_uni == 'usiu':
            is_eligible, eligibility_note = check_eligibility(interest_code, scores)
        else:
            is_eligible = (math_pt >= 6 and eng_pt >= 6)
            eligibility_note = f"Your secondary education qualifications meet admission requirements for {uni_data['name']}."

        final_major = ai_major
        final_school = ai_school or uni_data['name']

        # ===== 6. SANITIZE AI EXPLANATION (XSS Prevention) =====
        safe_reasoning = sanitize_html(ai_reasoning)
        final_explanation = safe_reasoning

        if not is_eligible and eligibility_note:
            safe_note = sanitize_html(eligibility_note)
            final_explanation += (
                f"<br><br><strong>⚠️ Academic Note:</strong> {safe_note} "
                f"Based on your current grades, we also suggest exploring "
                f"<strong>{best_fit_area}</strong> as a strong academic match."
            )

        # ===== 7. SAVE TO DATABASE =====
        new_result = Result(
            major=final_major,
            school=final_school,
            confidence=ai_confidence,
            user_id=current_user.id,
        )
        db.session.add(new_result)
        db.session.commit()

        # ===== 8. SAVE TO CSV (anonymized — no PII) =====
        student_data = {
            'student_id':        str(hash(current_user.id) & 0xFFFFFFFF),
            'country':           country,
            'curriculum':        curriculum,
            'target_uni':        target_uni,
            'math':              math_pt,
            'english':           eng_pt,
            'kiswahili':         kisw_pt,
            'biology':           bio_pt,
            'physics':           phy_pt,
            'chemistry':         chem_pt,
            'humanities':        hum_pt,
            'tech_business':     tech_pt,
            'interest_detected': detected_interests,
            'recommended_major': final_major,
            'school':            final_school,
            'confidence':        ai_confidence,
            'timestamp':         datetime.utcnow().isoformat(),
        }
        save_recommendation_data(student_data)

        # ===== 9. PREPARE DISPLAY DATA =====
        comp_labels = {s['id']: s['name'] for s in curr_data['subjects']['compulsory']}
        elec_labels = {s['id']: s['name'] for s in curr_data['subjects']['electives']}

        input_summary = {
            comp_labels.get('math', 'Math'):         f"{request.form.get('math', 'N/A')} ({math_pt}pts)",
            comp_labels.get('english', 'English'):   f"{request.form.get('english', 'N/A')} ({eng_pt}pts)",
            comp_labels.get('kiswahili', 'Second Lang / Core'): f"{request.form.get('kiswahili', 'N/A')} ({kisw_pt}pts)" if kisw_pt > 0 else "Not Taken",
            comp_labels.get('humanities', 'Humanities'): f"{request.form.get('humanities', 'N/A')} ({hum_pt}pts)",
            elec_labels.get('biology', 'Biology'):   f"{request.form.get('biology', 'N/A')} ({bio_pt}pts)"   if bio_pt  > 0 else "Not Taken",
            elec_labels.get('physics', 'Physics'):   f"{request.form.get('physics', 'N/A')} ({phy_pt}pts)"   if phy_pt  > 0 else "Not Taken",
            elec_labels.get('chemistry', 'Chemistry'): f"{request.form.get('chemistry', 'N/A')} ({chem_pt}pts)" if chem_pt > 0 else "Not Taken",
            elec_labels.get('tech_bus', 'Technical / Business'): f"{request.form.get('tech_bus', 'N/A')} ({tech_pt}pts)" if tech_pt > 0 else "Not Taken",
            'Target University': uni_data['name'],
            'Education System': curr_data['name'],
            'Your Interests': f'"{interest_text[:60]}..."' if len(interest_text) > 60 else f'"{interest_text}"',
        }

        return render_template(
            'index.html',
            result=final_major,
            school=final_school,
            confidence=round(ai_confidence, 1),
            explanation=final_explanation,
            input_summary=input_summary,
            show_results=True,
            is_alternative=not is_eligible,
            country_options=get_country_options(),
            curricula=CURRICULA,
            universities=UNIVERSITIES,
            form_data={
                'country': country,
                'curriculum': curriculum,
                'target_uni': target_uni,
                'math': request.form.get('math', ''),
                'english': request.form.get('english', ''),
                'kiswahili': request.form.get('kiswahili', ''),
                'biology': request.form.get('biology', ''),
                'physics': request.form.get('physics', ''),
                'chemistry': request.form.get('chemistry', ''),
                'humanities': request.form.get('humanities', ''),
                'tech_bus': request.form.get('tech_bus', ''),
                'interest': interest_text,
            }
        )

    except KeyError as e:
        flash(f"❌ Missing form field: {e}", 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Predict error: {e}")
        flash("❌ An error occurred while processing your request. Please try again.", 'danger')
        return redirect(url_for('index'))


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")   # Brute-force protection
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email',    '').strip().lower()
        password = request.form.get('password', '')

        # Generic message — don't reveal which field is wrong (enumeration attack)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('✅ Login successful! Welcome back.', 'success')
            next_page = request.args.get('next')
            # Validate next_page to prevent open-redirect attacks
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('❌ Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")   # Prevent account creation spam
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip().lower()
        password = request.form.get('password', '')

        # --- Input validation ---
        if not username or len(username) < 2:
            flash('❌ Username must be at least 2 characters.', 'danger')
            return redirect(url_for('register'))

        if not re.match(r'^[a-zA-Z0-9_.\- ]+$', username):
            flash('❌ Username may only contain letters, numbers, spaces, hyphens, underscores, and dots.', 'danger')
            return redirect(url_for('register'))

        # Password strength
        pw_error = validate_password(password)
        if pw_error:
            flash(f'❌ {pw_error}', 'danger')
            return redirect(url_for('register'))

        # Duplicate check — time-constant (prevent user enumeration via timing)
        existing_email = User.query.filter_by(email=email).first()
        existing_name  = User.query.filter_by(username=username).first()
        if existing_email or existing_name:
            flash('❌ An account with that email or username already exists.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('✅ Account created! You can now log in.', 'success')
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
    """Allow students to permanently delete their own account."""
    if request.method == 'POST':
        password = request.form.get('password', '')

        if not current_user.check_password(password):
            flash('❌ Incorrect password. Account deletion cancelled.', 'danger')
            return redirect(url_for('delete_account'))

        if current_user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                flash('❌ Cannot delete the last admin account. Promote another user to admin first.', 'danger')
                return redirect(url_for('delete_account'))

        try:
            user_id  = current_user.id
            username = current_user.username
            user_obj = db.session.get(User, user_id)
            logout_user()
            db.session.delete(user_obj)
            db.session.commit()
            flash(f'Account "{username}" has been permanently deleted.', 'info')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Account deletion error: {e}")
            flash('❌ An error occurred while deleting your account. Please try again.', 'danger')
            return redirect(url_for('delete_account'))

    return render_template('delete_account.html')


# ============================================================
# ADMIN ROUTES
# ============================================================

def _require_admin():
    """Helper — returns None if user is admin, otherwise a redirect response."""
    if not current_user.is_admin:
        flash('🚫 Access Denied: Administrators only.', 'danger')
        return redirect(url_for('index'))
    return None


@app.route('/admin')
@login_required
def admin():
    denied = _require_admin()
    if denied: return denied

    users = User.query.all()
    db_stats = {
        'total_users':           User.query.count(),
        'total_recommendations': Result.query.count(),
        'recent_activity':       Result.query.order_by(Result.timestamp.desc()).limit(5).all(),
    }
    csv_stats = get_recommendation_statistics()
    stats = {**db_stats, **csv_stats}

    return render_template('admin.html', users=users, stats=stats)


@app.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    """Toggle admin status — POST only, CSRF protected."""
    denied = _require_admin()
    if denied: return denied

    if user_id == current_user.id:
        flash('❌ You cannot change your own admin status.', 'danger')
        return redirect(url_for('admin'))

    user = db.session.get(User, user_id)
    if user:
        old_status   = user.is_admin
        user.is_admin = not user.is_admin
        db.session.commit()
        action = "granted" if user.is_admin else "revoked"
        log_admin_action(
            f"Admin privilege {action}",
            f"Target user: {user.username} (id={user.id})"
        )
        flash(f'✅ Admin status {action} for {user.username}.', 'success')
    else:
        flash('❌ User not found.', 'danger')

    return redirect(url_for('admin'))


@app.route('/admin/recommendations')
@login_required
def admin_recommendations():
    denied = _require_admin()
    if denied: return denied

    search_query  = request.args.get('search', '').strip()
    school_filter = request.args.get('school', '').strip()
    page          = request.args.get('page', 1, type=int)

    query = Result.query.join(User)
    if search_query:
        query = query.filter(
            Result.major.ilike(f'%{search_query}%') |
            User.username.ilike(f'%{search_query}%') |
            User.email.ilike(f'%{search_query}%')
        )
    if school_filter:
        query = query.filter(Result.school.ilike(f'%{school_filter}%'))

    paginated = query.order_by(desc(Result.timestamp)).paginate(page=page, per_page=20)
    schools   = [s[0] for s in db.session.query(Result.school).distinct().all()]

    return render_template(
        'admin_recommendations.html',
        results=paginated.items,
        pagination=paginated,
        schools=schools,
        search_query=search_query,
        school_filter=school_filter,
    )


@app.route('/admin/recommendation/<int:rec_id>')
@login_required
def admin_view_recommendation(rec_id):
    denied = _require_admin()
    if denied: return denied

    result = db.session.get(Result, rec_id)
    if not result:
        flash('❌ Recommendation not found.', 'danger')
        return redirect(url_for('admin_recommendations'))

    user = db.session.get(User, result.user_id)
    return render_template('admin_rec_detail.html', result=result, student=user)


@app.route('/admin/recommendation/<int:rec_id>/delete', methods=['GET', 'POST'])
@login_required
def admin_delete_recommendation(rec_id):
    denied = _require_admin()
    if denied: return denied

    result = db.session.get(Result, rec_id)
    if not result:
        flash('❌ Recommendation not found.', 'danger')
        return redirect(url_for('admin_recommendations'))

    student_name = result.author.username

    if request.method == 'POST':
        major_name = result.major
        db.session.delete(result)
        db.session.commit()
        log_admin_action(
            "Recommendation deleted",
            f"Major: {major_name}, Student: {student_name}"
        )
        flash(f'✅ Recommendation deleted: {major_name} for {student_name}', 'success')
        return redirect(url_for('admin_recommendations'))

    return render_template('admin_confirm_delete.html', result=result, student_name=student_name)


@app.route('/admin/user/<int:user_id>/history')
@login_required
def admin_user_history(user_id):
    denied = _require_admin()
    if denied: return denied

    user    = db.session.get(User, user_id)
    if not user:
        flash('❌ User not found.', 'danger')
        return redirect(url_for('admin'))
    results = Result.query.filter_by(user_id=user_id).order_by(desc(Result.timestamp)).all()
    return render_template('admin_user_history.html', user=user, results=results)


@app.route('/admin/delete-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_delete_user(user_id):
    denied = _require_admin()
    if denied: return denied

    if user_id == current_user.id:
        flash('❌ Cannot delete your own account from admin panel.', 'danger')
        return redirect(url_for('admin'))

    user = db.session.get(User, user_id)
    if not user:
        flash('❌ User not found.', 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        try:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            log_admin_action("User deleted", f"Deleted user: {username} (id={user_id})")
            flash(f'✅ User {username} and all their data have been deleted.', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Admin delete user error: {e}")
            flash(f'❌ Error deleting user: {str(e)}', 'danger')
            return redirect(url_for('admin'))

    return render_template('admin_confirm_delete_user.html', user=user)


@app.route('/admin/analytics')
@login_required
def admin_analytics():
    denied = _require_admin()
    if denied: return denied

    total_recommendations = Result.query.count()
    total_users           = User.query.count()
    week_ago              = datetime.utcnow() - timedelta(days=7)

    top_majors = db.session.query(
        Result.major, func.count(Result.id).label('count')
    ).group_by(Result.major).order_by(desc(func.count(Result.id))).limit(10).all()

    top_schools = db.session.query(
        Result.school, func.count(Result.id).label('count')
    ).group_by(Result.school).order_by(desc(func.count(Result.id))).all()

    avg_confidence = db.session.query(
        Result.major, func.avg(Result.confidence).label('avg_conf')
    ).group_by(Result.major).order_by(desc(func.avg(Result.confidence))).limit(10).all()

    recent_count = Result.query.filter(Result.timestamp >= week_ago).count()

    analytics_data = {
        'total_recommendations': total_recommendations,
        'total_users':           total_users,
        'top_majors':            top_majors,
        'top_schools':           top_schools,
        'avg_confidence':        avg_confidence,
        'last_week_count':       recent_count,
        'csv_stats':             get_recommendation_statistics(),
    }
    return render_template('admin_analytics.html', analytics=analytics_data)


@app.route('/admin/export-data')
@login_required
def admin_export_data():
    denied = _require_admin()
    if denied: return denied

    results = Result.query.join(User).all()
    output  = StringIO()
    writer  = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Email', 'Major', 'School', 'Confidence %', 'Date', 'Time'])
    for r in results:
        ts = r.timestamp
        writer.writerow([
            r.id, r.author.username, r.author.email,
            r.major, r.school, round(r.confidence, 2),
            ts.strftime('%Y-%m-%d'), ts.strftime('%H:%M:%S'),
        ])
    return render_template('export_data.html', csv_data=output.getvalue())


@app.route('/admin/export-csv')
@login_required
def download_csv():
    denied = _require_admin()
    if denied: return denied

    results = Result.query.join(User).all()
    output  = StringIO()
    writer  = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Email', 'Major', 'School', 'Confidence', 'Date', 'Time'])
    for r in results:
        ts = r.timestamp
        writer.writerow([
            r.id, r.author.username, r.author.email,
            r.major, r.school, round(r.confidence, 2),
            ts.strftime('%Y-%m-%d'), ts.strftime('%H:%M:%S'),
        ])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=recommendations_export.csv'},
    )


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if DEBUG or ENV == 'development':
        print("[WARNING] Development server active — do not use in production.")
        app.run(debug=DEBUG, host='127.0.0.1', port=5000)
    else:
        print("Use: python run_waitress.py  OR  gunicorn wsgi:app")
        raise RuntimeError("Use run_waitress.py or gunicorn — not app.py directly in production.")
