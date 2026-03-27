"""
Rule-based major recommendation system for USIU-Africa
Based on KCSE performance and student interests
"""

# ==================== VALID KCSE GRADES ====================
VALID_GRADES = {
    'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
    'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 
    'D-': 2, 'E': 1, 'NOT TAKEN': 0
}

# ==================== FLEXIBLE GRADE PARSING ====================
def parse_grade_input(grade_text):
    """
    Parse flexible grade input from user text
    Accepts various formats: A, a, A-, a-, B+, etc.
    """
    if not grade_text or grade_text.upper() in ['NOT TAKEN', 'N/A', 'NONE', '']:
        return 0
    
    # Clean and normalize the input
    grade = grade_text.strip().upper()
    
    # Handle common variations
    grade_map = {
        'A': 12, 'A-': 11, 'A MINUS': 11,
        'B+': 10, 'B PLUS': 10, 'B': 9, 'B-': 8, 'B MINUS': 8,
        'C+': 7, 'C PLUS': 7, 'C': 6, 'C-': 5, 'C MINUS': 5,
        'D+': 4, 'D PLUS': 4, 'D': 3, 'D-': 2, 'D MINUS': 2,
        'E': 1
    }
    
    return grade_map.get(grade, 0)  # Return 0 if grade not recognized

# ==================== NATURAL LANGUAGE INTEREST ANALYSIS ====================
def analyze_interest_text(interest_text):
    """
    Analyze natural language interest description and map to interest categories
    Returns: (interest_code, detected_interests_list)
    """
    if not interest_text or len(interest_text.strip()) < 3:
        return -1, ["unclear"]
    
    text = interest_text.lower().strip()
    
    # Define keyword mappings for each interest category
    interest_keywords = {
        0: {  # Technology & Engineering
            'technology', 'tech', 'computer', 'programming', 'coding', 'software', 'engineering', 
            'it', 'ai', 'artificial intelligence', 'robotics', 'data', 'analytics', 'web', 'app',
            'mobile', 'game', 'gaming', 'cybersecurity', 'network', 'database', 'algorithm',
            'machine learning', 'automation', 'innovation', 'digital', 'electronics', 'hardware'
        },
        1: {  # Health Sciences
            'health', 'medical', 'doctor', 'nurse', 'pharmacy', 'medicine', 'hospital', 'patient',
            'healthcare', 'biology', 'chemistry', 'anatomy', 'physiology', 'disease', 'treatment',
            'wellness', 'nutrition', 'pharmaceutical', 'therapy', 'surgery', 'clinic', 'care',
            'help people', 'healing', 'life science', 'biomedical'
        },
        2: {  # Business & Commerce
            'business', 'commerce', 'finance', 'accounting', 'marketing', 'management', 'entrepreneur',
            'startup', 'corporate', 'economy', 'trade', 'investment', 'banking', 'sales', 'leadership',
            'strategy', 'consulting', 'economics', 'commerce', 'profit', 'money', 'wealth', 'enterprise'
        },
        3: {  # Humanities & Social Sciences
            'humanities', 'social science', 'psychology', 'sociology', 'history', 'politics', 'government',
            'international relations', 'law', 'justice', 'education', 'teaching', 'research', 'society',
            'culture', 'anthropology', 'philosophy', 'ethics', 'human behavior', 'social', 'community',
            'development', 'policy', 'diplomacy', 'understanding people', 'society'
        },
        4: {  # Creative Arts & Media
            'art', 'creative', 'design', 'media', 'film', 'animation', 'journalism', 'communication',
            'photography', 'music', 'theater', 'acting', 'writing', 'literature', 'graphic design',
            'advertising', 'broadcasting', 'entertainment', 'storytelling', 'visual', 'performance',
            'cinema', 'production', 'editing', 'content creation'
        }
    }
    
    # Check for undecided/unclear keywords
    undecided_keywords = {'not sure', 'undecided', 'unclear', 'confused', 'don\'t know', 'unsure', 'confusing'}
    if any(keyword in text for keyword in undecided_keywords):
        return -1, ["undecided"]
    
    # Count matches for each interest category
    scores = {}
    detected_keywords = []
    
    for interest_code, keywords in interest_keywords.items():
        matches = [kw for kw in keywords if kw in text]
        scores[interest_code] = len(matches)
        if matches:
            detected_keywords.extend(matches[:3])  # Limit to top 3 matches per category
    
    # Find the highest scoring interest
    if scores:
        best_interest = max(scores.items(), key=lambda x: x[1])
        if best_interest[1] > 0:  # At least one match
            return best_interest[0], list(set(detected_keywords))  # Remove duplicates
    
    # If no clear matches, return undecided
    return -1, ["unclear interests"]

# ==================== PROGRAMS BY SCHOOL ====================
PROGRAMS = {
    'Chandaria School of Business': [
        'Global Leadership and Governance', 'Accounting', 'Finance', 
        'Hotel and Restaurant Management', 'International Business Administration'
    ],
    'School of Humanities and Social Sciences': [
        'International Relations', 'Criminal Justice Studies', 'Psychology'
    ],
    'School of Science and Technology': [
        'Applied Computer Technology', 'Information Systems & Technology', 
        'Artificial Intelligence (AI) & Robotics', 'Data Science and Analytics', 
        'Software Engineering'
    ],
    'School of Pharmacy and Health Sciences': [
        'Pharmacy', 'Nursing'
    ],
    'School of Communication, Cinematic and Creative Arts': [
        'Animation', 'Film Production and Directing', 'Journalism'
    ]
}

MAJOR_TO_SCHOOL = {}
for school, majors in PROGRAMS.items():
    for major in majors:
        MAJOR_TO_SCHOOL[major] = school

# ==================== INTEREST MAPPING ====================
INTEREST_MAP = {
    'Technology & Engineering': 0,
    'Health Sciences': 1,
    'Business & Commerce': 2,
    'Humanities & Social Sciences': 3,
    'Creative Arts & Media': 4,
    'Undecided': -1
}

# ==================== RECOMMENDATION LOGIC ====================

def get_major_by_rules(scores, interest_code):
    """
    Recommend a major based on KCSE scores and interest.
    Aligns with USIU admission criteria and student strengths.
    
    Args:
        scores: dict with 'math', 'english', 'kiswahili', 'biology', 'physics', 
                'chemistry', 'humanities', 'tech_business' (all as points 0-12)
        interest_code: int (0-4) representing interest area
    
    Returns:
        tuple: (major_name, explanation, confidence_level)
    """
    math = scores.get('math', 0)
    eng = scores.get('english', 0)
    kisw = scores.get('kiswahili', 0)
    bio = scores.get('biology', 0)
    phy = scores.get('physics', 0)
    chem = scores.get('chemistry', 0)
    hum = scores.get('humanities', 0)
    tech = scores.get('tech_business', 0)
    
    # ===== SCHOOL OF SCIENCE AND TECHNOLOGY (Interest 0) =====
    if interest_code == 0:
        # High Math & Physics -> AI/Robotics
        if math >= 11 and phy >= 11:
            return ('Artificial Intelligence (AI) & Robotics', 
                   f"Outstanding STEM foundation (Math: {math}pts, Physics: {phy}pts). "
                   f"You have the analytical skills for advanced technology roles.",
                   95)
        # High Math & Physics -> Software Engineering
        elif math >= 10 and phy >= 10:
            return ('Software Engineering',
                   f"Strong Math ({math}pts) and Physics ({phy}pts) skills indicate excellent "
                   f"programming and system design potential.",
                   90)
        # Data Science path
        elif math >= 9 and tech >= 8:
            return ('Data Science and Analytics',
                   f"Your Math strength ({math}pts) combined with technical knowledge "
                   f"positions you well for data-driven roles.",
                   85)
        # Applied Tech
        elif math >= 8 and tech >= 8:
            return ('Applied Computer Technology',
                   f"Solid technical foundation ({math}pts Math, {tech}pts Tech). "
                   f"Perfect for hands-on technology applications.",
                   80)
        # Default for tech interest
        else:
            return ('Information Systems & Technology',
                   f"Your interest in technology combined with available scores "
                   f"suggests IT systems management as a practical fit.",
                   70)
    
    # ===== SCHOOL OF PHARMACY AND HEALTH SCIENCES (Interest 1) =====
    elif interest_code == 1:
        # High Science -> Pharmacy
        if bio >= 11 and chem >= 11:
            return ('Pharmacy',
                   f"Excellent scientific foundation (Biology: {bio}pts, Chemistry: {chem}pts). "
                   f"You have the precision needed for pharmaceutical practice.",
                   95)
        # Moderate-High Science -> Nursing
        elif bio >= 9 and chem >= 9:
            return ('Nursing',
                   f"Strong Biology ({bio}pts) and Chemistry ({chem}pts) scores show readiness "
                   f"for healthcare. Nursing offers meaningful patient care.",
                   85)
        # Lower science but interested in health
        else:
            return ('Nursing',
                   f"Your interest in health sciences is valuable. Nursing offers diverse "
                   f"opportunities in patient care and healthcare management.",
                   75)
    
    # ===== CHANDARIA SCHOOL OF BUSINESS (Interest 2) =====
    elif interest_code == 2:
        # High Math & Business -> Accounting
        if math >= 11 and tech >= 10:
            return ('Accounting',
                   f"Exceptional numerical skills (Math: {math}pts, Business: {tech}pts). "
                   f"Accounting suits systematic thinkers like you.",
                   92)
        # Strong Math & Business -> Finance
        elif math >= 10 and tech >= 9:
            return ('Finance',
                   f"Strong quantitative skills (Math: {math}pts) with business acumen "
                   f"({tech}pts). Finance leverages both strengths.",
                   88)
        # Leadership focus
        elif eng >= 10 and hum >= 10:
            return ('Global Leadership and Governance',
                   f"Excellent communication (English: {eng}pts) and humanities scores "
                   f"({hum}pts) ideal for visionary leadership roles.",
                   85)
        # Business focus
        elif tech >= 8:
            return ('Hotel and Restaurant Management',
                   f"Strong business foundation. Hotel Management combines hospitality "
                   f"with entrepreneurial skills.",
                   75)
        # Default
        else:
            return ('International Business Administration',
                   f"Broad business interest with balanced academic profile. "
                   f"IBA offers diverse business career paths.",
                   70)
    
    # ===== SCHOOL OF HUMANITIES AND SOCIAL SCIENCES (Interest 3) =====
    elif interest_code == 3:
        # High English & Humanities -> International Relations
        if eng >= 10 and hum >= 10:
            return ('International Relations',
                   f"Excellent language and analytical skills (English: {eng}pts, Humanities: {hum}pts). "
                   f"IR requires deep understanding of cultures and politics.",
                   90)
        # Strong Humanities -> Criminal Justice
        elif hum >= 9:
            return ('Criminal Justice Studies',
                   f"Strong humanities foundation ({hum}pts) indicates analytical thinking needed "
                   f"for justice and legal systems work.",
                   80)
        # Default
        else:
            return ('Psychology',
                   f"Your interest in understanding people makes Psychology ideal. "
                   f"Psychology is foundational across many fields.",
                   75)
    
    # ===== SCHOOL OF COMMUNICATION (Interest 4) =====
    elif interest_code == 4:
        # Strong tech & English -> Animation
        if tech >= 10 and eng >= 8:
            return ('Animation',
                   f"Technical ({tech}pts) and creative skills blend perfectly for Animation. "
                   f"Growing field with high demand.",
                   85)
        # Strong English -> Journalism
        elif eng >= 10:
            return ('Journalism',
                   f"Exceptional English skills ({eng}pts) and communication ability "
                   f"essential for impactful journalism.",
                   88)
        # Default
        else:
            return ('Film Production and Directing',
                   f"Creative expression combined with technical production skills. "
                   f"Film opens doors to media and entertainment industries.",
                   75)
    
    # Fallback if no interest specified
    return ('International Business Administration',
           "Based on your overall academic profile, a business foundation offers flexibility.",
           65)


def determine_best_fit(scores):
    """
    For undecided students, calculates which field best matches their strengths.
    
    Args:
        scores: dict with all KCSE subject scores
    
    Returns:
        tuple: (best_interest_code, field_name, calculated_scores_dict)
    """
    math = scores.get('math', 0)
    eng = scores.get('english', 0)
    kisw = scores.get('kiswahili', 0)
    bio = scores.get('biology', 0)
    phy = scores.get('physics', 0)
    chem = scores.get('chemistry', 0)
    hum = scores.get('humanities', 0)
    tech = scores.get('tech_business', 0)
    
    field_scores = {
        'Technology & Engineering': (math + phy + tech) / 3 if (math + phy + tech) > 0 else 0,
        'Health Sciences': (bio + chem + math) / 3 if (bio + chem + math) > 0 else 0,
        'Business & Commerce': (math + tech + eng) / 3 if (math + tech + eng) > 0 else 0,
        'Humanities & Social Sciences': (eng + kisw + hum) / 3 if (eng + kisw + hum) > 0 else 0,
        'Creative Arts & Media': (eng + tech + hum) / 3 if (eng + tech + hum) > 0 else 0
    }
    
    best_field = max(field_scores, key=field_scores.get)
    best_code = INTEREST_MAP.get(best_field, 0)
    
    return best_code, best_field, field_scores


def check_eligibility(interest_code, scores):
    """
    Checks if student meets minimum eligibility for chosen field.
    
    Args:
        interest_code: int (0-4)
        scores: dict with all KCSE subject scores
    
    Returns:
        tuple: (is_eligible, guidance_message)
    """
    math = scores.get('math', 0)
    bio = scores.get('biology', 0)
    chem = scores.get('chemistry', 0)
    phy = scores.get('physics', 0)
    
    # Compulsory subjects check
    if scores.get('math', 0) == 0 or scores.get('english', 0) == 0:
        return False, "You must provide Math and English scores (compulsory in KCSE)."
    
    # Interest-specific minimums
    if interest_code == 0:  # Technology
        if math < 7:
            return False, "Technology fields require at least C+ (7pts) in Mathematics."
        if phy > 0 and phy < 7:
            return False, "Physics is recommended for Technology; if taken, requires C+ (7pts)."
    
    elif interest_code == 1:  # Health
        if bio < 7 or chem < 7:
            return False, "Health Sciences require minimum C+ (7pts) in both Biology and Chemistry."
    
    elif interest_code == 2:  # Business
        if math < 6:
            return False, "Business programs require minimum C (6pts) in Mathematics."
    
    # Humanities and Creative haven't strict minimums
    
    return True, "Your grades meet the requirements for this field."


def generate_report(major, school, scores, confidence, explanation, is_alternative=False):
    """
    Generates a comprehensive recommendation report for the student.
    """
    report = {
        'major': major,
        'school': school,
        'confidence': confidence,
        'explanation': explanation,
        'is_alternative': is_alternative,
        'scores_summary': {
            'Math': f"{scores.get('math', 0)}pts",
            'English': f"{scores.get('english', 0)}pts",
            'Kiswahili': f"{scores.get('kiswahili', 0)}pts",
            'Biology': f"{scores.get('biology', 0)}pts" if scores.get('biology', 0) > 0 else "Not taken",
            'Physics': f"{scores.get('physics', 0)}pts" if scores.get('physics', 0) > 0 else "Not taken",
            'Chemistry': f"{scores.get('chemistry', 0)}pts" if scores.get('chemistry', 0) > 0 else "Not taken",
            'Humanities': f"{scores.get('humanities', 0)}pts",
            'Tech/Business': f"{scores.get('tech_business', 0)}pts" if scores.get('tech_business', 0) > 0 else "Not taken",
        }
    }
    return report
