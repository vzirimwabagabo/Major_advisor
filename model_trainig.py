import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# 1. Define the Exact USIU-Africa Programs
programs = [
    # Chandaria School of Business
    'Global Leadership and Governance', 'Accounting', 'Finance', 
    'Hotel and Restaurant Management', 'International Business Administration',
    # School of Humanities and Social Sciences
    'International Relations', 'Criminal Justice Studies', 'Psychology',
    # School of Science and Technology
    'Applied Computer Technology', 'Information Systems & Technology', 
    'Artificial Intelligence (AI) & Robotics', 'Data Science and Analytics', 
    'Software Engineering',
    # School of Pharmacy and Health Sciences
    'Pharmacy', 'Nursing',
    # School of Communication, Cinematic and Creative Arts
    'Animation', 'Film Production and Directing', 'Journalism'
]

data_size = 5000
np.random.seed(42)

# 2. Synthetic Data Generation (KCSE Subjects)
data = {
    # Group I: Compulsory
    'Math_Points': np.random.randint(4, 13, data_size),
    'English_Points': np.random.randint(4, 13, data_size),
    'Kiswahili_Points': np.random.randint(4, 13, data_size),
    
    # Group II: Sciences
    'Biology_Points': np.random.randint(0, 13, data_size), # 0 if not taken
    'Physics_Points': np.random.randint(0, 13, data_size),
    'Chemistry_Points': np.random.randint(0, 13, data_size),
    
    # Group III: Humanities
    'Humanities_Points': np.random.randint(4, 13, data_size),
    
    # Group IV/V: Technical & Business (e.g., Computer Studies, Business Studies)
    'Tech_Business_Points': np.random.randint(0, 13, data_size),
    
    # Interest Code (0-4 mapped to Schools)
    'Interest_Code': np.random.randint(0, 5, data_size)
}

df = pd.DataFrame(data)

# 3. Recommendation Logic (Simulating Admission Criteria)
def determine_major(row):
    interest = row['Interest_Code']
    
    # --- School of Science and Technology (Interest 0) ---
    if interest == 0:
        # High Math & Physics -> Engineering/AI
        if row['Math_Points'] >= 11 and row['Physics_Points'] >= 11:
            return 'Artificial Intelligence (AI) & Robotics'
        elif row['Math_Points'] >= 10 and row['Physics_Points'] >= 10:
            return 'Software Engineering'
        # Moderate Math/Tech -> Applied Tech
        elif row['Math_Points'] >= 8 and row['Tech_Business_Points'] >= 10: 
            return 'Applied Computer Technology'
        # Data focus
        elif row['Math_Points'] >= 9:
            return 'Data Science and Analytics'
        else:
            return 'Information Systems & Technology'

    # --- School of Pharmacy and Health Sciences (Interest 1) ---
    elif interest == 1:
        bio = row['Biology_Points']
        chem = row['Chemistry_Points']
        # High Science scores -> Pharmacy
        if bio >= 11 and chem >= 11:
            return 'Pharmacy'
        # Moderate Science -> Nursing
        elif bio >= 9 and chem >= 9:
            return 'Nursing'
        else:
            return 'Nursing' # Default for health interest

    # --- Chandaria School of Business (Interest 2) ---
    elif interest == 2:
        math = row['Math_Points']
        bus = row['Tech_Business_Points'] # Business Studies grade
        eng = row['English_Points']
        
        # Strong Math/Business -> Accounting/Finance
        if math >= 11 and bus >= 10:
            return 'Accounting'
        elif math >= 10 and bus >= 9:
            return 'Finance'
        # Leadership/Governance focus (Strong Humanities/English)
        elif eng >= 10 and row['Humanities_Points'] >= 10:
            return 'Global Leadership and Governance'
        # Service industry
        elif bus >= 8:
            return 'Hotel and Restaurant Management'
        else:
            return 'International Business Administration'

    # --- School of Humanities (Interest 3) ---
    elif interest == 3:
        eng = row['English_Points']
        hum = row['Humanities_Points']
        
        if eng >= 10 and hum >= 10:
            return 'International Relations'
        elif hum >= 9:
            return 'Criminal Justice Studies'
        else:
            return 'Psychology'

    # --- School of Communication (Interest 4) ---
    elif interest == 4:
        eng = row['English_Points']
        tech = row['Tech_Business_Points'] # Art & Design might be here
        
        if tech >= 10 and eng >= 8:
            return 'Animation'
        elif eng >= 10:
            return 'Journalism'
        else:
            return 'Film Production and Directing'

    return 'International Business Administration' # Fallback

df['Recommended_Major'] = df.apply(determine_major, axis=1)

# 4. Preprocessing
features = [
    'Math_Points', 'English_Points', 'Kiswahili_Points', 
    'Biology_Points', 'Physics_Points', 'Chemistry_Points', 
    'Humanities_Points', 'Tech_Business_Points', 'Interest_Code'
]
X = df[features]
y = df['Recommended_Major']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 5. Train
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Save
joblib.dump(model, 'major_recommendation_model.pkl')
joblib.dump(le, 'label_encoder.pkl')

print("Model trained successfully on USIU-Africa Programs.")
print(f"Classes: {le.classes_}")