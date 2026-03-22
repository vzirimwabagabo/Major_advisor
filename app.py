from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import joblib
import numpy as np
from datetime import datetime

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'usiu_africa_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access the AI Advisor."

# --- AI Model Loading ---
model = joblib.load('major_recommendation_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

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

# --- Mappings ---
grade_mapping = {
    'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
    'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'E': 1,
    'NOT TAKEN': 0
}

interest_mapping = {
    'Technology & Engineering': 0,
    'Health Sciences': 1,
    'Business & Commerce': 2,
    'Humanities & Social Sciences': 3,
    'Creative Arts & Media': 4
}

school_map = {
    'Global Leadership and Governance': 'Chandaria School of Business',
    'Accounting': 'Chandaria School of Business', 'Finance': 'Chandaria School of Business',
    'Hotel and Restaurant Management': 'Chandaria School of Business',
    'International Business Administration': 'Chandaria School of Business',
    'International Relations': 'School of Humanities and Social Sciences',
    'Criminal Justice Studies': 'School of Humanities and Social Sciences',
    'Psychology': 'School of Humanities and Social Sciences',
    'Applied Computer Technology': 'School of Science and Technology',
    'Information Systems & Technology': 'School of Science and Technology',
    'Artificial Intelligence (AI) & Robotics': 'School of Science and Technology',
    'Data Science and Analytics': 'School of Science and Technology',
    'Software Engineering': 'School of Science and Technology',
    'Pharmacy': 'School of Pharmacy and Health Sciences',
    'Nursing': 'School of Pharmacy and Health Sciences',
    'Animation': 'School of Communication, Cinematic and Creative Arts',
    'Film Production and Directing': 'School of Communication, Cinematic and Creative Arts',
    'Journalism': 'School of Communication, Cinematic and Creative Arts'
}

# --- Helper Functions ---

def check_eligibility(interest_code, math, eng, bio, phy, chem):
    """Strict eligibility check for specific schools."""
    if interest_code == 1: # Health
        if bio < 7 or chem < 7:
            return False, "Health Sciences require at least a C+ in Biology and Chemistry."
    elif interest_code == 0: # Tech
        if math < 7:
            return False, "Technology and Engineering fields require at least a C+ in Mathematics."
        if phy < 7 and phy > 0:
             return False, "Engineering fields require at least a C+ in Physics."
    elif interest_code == 2: # Business
        if math < 6:
            return False, "Business programs require a minimum of C in Mathematics."
    return True, "Your grades meet the minimum requirements."

def generate_explanation(major, math, eng, bio, phy, chem, tech, hum):
    """Generates explanation for valid recommendations."""
    if major in ['Pharmacy', 'Nursing']:
        return f"Recommended because of strong Science background (Biology: {bio}pts, Chemistry: {chem}pts)."
    elif major in ['Artificial Intelligence (AI) & Robotics', 'Software Engineering']:
        return f"Recommended because of excellent STEM scores (Math: {math}pts, Physics: {phy}pts)."
    elif major in ['Accounting', 'Finance']:
        return f"Recommended because of strong numerical skills (Math: {math}pts) and Business background."
    elif major in ['International Relations', 'Journalism']:
        return f"Recommended because of strong language and humanities skills (English: {eng}pts)."
    else:
        return "Recommended based on a balanced academic profile matching general program requirements."

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
    stats = {
        'total_users': User.query.count(),
        'total_recommendations': Result.query.count(),
        'recent_activity': Result.query.order_by(Result.timestamp.desc()).limit(5).all()
    }
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

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # 1. Capture Inputs
        math_pt = grade_mapping.get(request.form['math'].upper(), 0)
        eng_pt = grade_mapping.get(request.form['english'].upper(), 0)
        kisw_pt = grade_mapping.get(request.form['kiswahili'].upper(), 0)
        bio_pt = grade_mapping.get(request.form.get('biology', 'NOT TAKEN').upper(), 0)
        phy_pt = grade_mapping.get(request.form.get('physics', 'NOT TAKEN').upper(), 0)
        chem_pt = grade_mapping.get(request.form.get('chemistry', 'NOT TAKEN').upper(), 0)
        hum_pt = grade_mapping.get(request.form['humanities'].upper(), 0)
        tech_pt = grade_mapping.get(request.form.get('tech_bus', 'NOT TAKEN').upper(), 0)
        interest_str = request.form['interest']

        if 0 in [math_pt, eng_pt, kisw_pt]:
            flash('Group I subjects are compulsory.', 'danger')
            return redirect(url_for('index'))

        # --- LOGIC FOR UNDECIDED ---
        if interest_str == 'Undecided':
            scores = {
                'Technology': (math_pt + phy_pt + tech_pt) / 3,
                'Health': (bio_pt + chem_pt + math_pt) / 3,
                'Business': (math_pt + tech_pt + eng_pt) / 3,
                'Humanities': (eng_pt + kisw_pt + hum_pt) / 3,
                'Creative': (eng_pt + tech_pt + hum_pt) / 3
            }
            best_fit = max(scores, key=scores.get)
            if best_fit == 'Technology': interest_code = 0
            elif best_fit == 'Health': interest_code = 1
            elif best_fit == 'Business': interest_code = 2
            elif best_fit == 'Humanities': interest_code = 3
            else: interest_code = 4
            undecided_mode = True
            is_eligible = True
            guidance_msg = ""
            
        else:
            # --- LOGIC FOR DECIDED STUDENTS ---
            interest_code = interest_mapping.get(interest_str, 0)
            undecided_mode = False
            is_eligible, guidance_msg = check_eligibility(interest_code, math_pt, eng_pt, bio_pt, phy_pt, chem_pt)

        # --- PIVOT LOGIC (If Strict Check Fails) ---
        final_interest_code = interest_code
        
        if not is_eligible:
            scores = {
                'Technology': (math_pt + phy_pt + tech_pt) / 3,
                'Health': (bio_pt + chem_pt + math_pt) / 3,
                'Business': (math_pt + tech_pt + eng_pt) / 3,
                'Humanities': (eng_pt + kisw_pt + hum_pt) / 3,
                'Creative': (eng_pt + tech_pt + hum_pt) / 3
            }
            best_fit_area = max(scores, key=scores.get)
            
            if best_fit_area == 'Technology': final_interest_code = 0
            elif best_fit_area == 'Health': final_interest_code = 1
            elif best_fit_area == 'Business': final_interest_code = 2
            elif best_fit_area == 'Humanities': final_interest_code = 3
            else: final_interest_code = 4

        # 2. Run Prediction
        features = np.array([[math_pt, eng_pt, kisw_pt, bio_pt, phy_pt, chem_pt, hum_pt, tech_pt, final_interest_code]])
        pred_encoded = model.predict(features)
        confidence = model.predict_proba(features).max() * 100
        major = label_encoder.inverse_transform(pred_encoded)[0]
        school = school_map.get(major, "USIU-Africa")
        
        # 3. Generate Explanation
        if undecided_mode:
            explanation = (f"Since you were Undecided, we analyzed your strengths. "
                           f"Your grades fit best in <strong>{best_fit}</strong>. Based on this, we recommend {major}.")
        elif not is_eligible:
            explanation = (f"<strong>Guidance Note:</strong> You selected <strong>{interest_str}</strong>, but unfortunately, {guidance_msg}<br><br>"
                           f"<strong>Please don't be discouraged.</strong> We all have different strengths. "
                           f"Based on your grades, you show great potential in <strong>{best_fit_area}</strong>. "
                           f"This path offers excellent opportunities, and we recommend <strong>{major}</strong>.")
        else:
            explanation = generate_explanation(major, math_pt, eng_pt, bio_pt, phy_pt, chem_pt, tech_pt, hum_pt)

        # 4. Save to History (FR7)
        new_result = Result(
            major=major, 
            school=school, 
            confidence=round(confidence, 2), 
            user_id=current_user.id
        )
        db.session.add(new_result)
        db.session.commit()

        # 5. Prepare Input Summary
        input_summary = {
            'Math': f"{request.form['math']} ({math_pt} pts)",
            'English': f"{request.form['english']} ({eng_pt} pts)",
            'Kiswahili': f"{request.form['kiswahili']} ({kisw_pt} pts)",
            'Biology': f"{request.form.get('biology', 'N/A')} ({bio_pt} pts)" if bio_pt > 0 else "Not Taken",
            'Physics': f"{request.form.get('physics', 'N/A')} ({phy_pt} pts)" if phy_pt > 0 else "Not Taken",
            'Chemistry': f"{request.form.get('chemistry', 'N/A')} ({chem_pt} pts)" if chem_pt > 0 else "Not Taken",
            'Humanity': f"{request.form['humanities']} ({hum_pt} pts)",
            'Tech/Business': f"{request.form.get('tech_bus', 'N/A')} ({tech_pt} pts)" if tech_pt > 0 else "Not Taken",
            'Interest': interest_str
        }

        return render_template('index.html', result=major, school=school, confidence=round(confidence, 2), explanation=explanation, input_summary=input_summary, show_results=True, is_alternative=not is_eligible)

    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)