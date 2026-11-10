"""
Rule-based major recommendation system for USIU-Africa.
Based on KCSE performance and student interests.

ALIGNED TO REAL USIU-AFRICA PROGRAMS (2025/2026 Catalog).
"""

# ==================== VALID KCSE GRADES ====================
VALID_GRADES = {
    'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
    'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3,
    'D-': 2, 'E': 1, 'NOT TAKEN': 0
}

# ==================== REAL USIU-AFRICA PROGRAMS (Single Source of Truth) ====================
# This is the ONLY place programs should be defined. All other modules import from here.
PROGRAMS = {
    'School of Science and Technology': [
        'Applied Computer Technology',
        'Information Systems & Technology',
        'Artificial Intelligence (AI) & Robotics',
        'Data Science and Analytics',
        'Software Engineering',
    ],
    'Chandaria School of Business': [
        'Global Leadership and Governance',
        'Accounting',
        'Finance',
        'Hotel and Restaurant Management',
        'International Business Administration',
    ],
    'School of Humanities and Social Sciences': [
        'International Relations',
        'Criminal Justice Studies',
        'Psychology',
    ],
    'School of Pharmacy and Health Sciences': [
        'Pharmacy',
        'Nursing',
    ],
    'School of Communication, Cinematic and Creative Arts': [
        'Animation',
        'Film Production and Directing',
        'Journalism',
    ],
}

# Build reverse lookup: major → school
MAJOR_TO_SCHOOL = {}
for school, majors in PROGRAMS.items():
    for major in majors:
        MAJOR_TO_SCHOOL[major] = school

# ==================== INTEREST MAP ====================
INTEREST_MAP = {
    'Technology & Engineering': 0,
    'Health Sciences': 1,
    'Business & Commerce': 2,
    'Humanities & Social Sciences': 3,
    'Creative Arts & Media': 4,
    'Undecided': -1
}

# ==================== FLEXIBLE GRADE PARSING ====================
def parse_grade_input(grade_text):
    """
    Parse flexible grade input from user text.
    Accepts various formats: A, a, A-, a-, B+, etc.
    Returns integer points (0-12).
    """
    if not grade_text or grade_text.upper() in ['NOT TAKEN', 'N/A', 'NONE', '']:
        return 0

    grade = grade_text.strip().upper()

    grade_map = {
        'A': 12, 'A-': 11, 'A MINUS': 11,
        'B+': 10, 'B PLUS': 10, 'B': 9, 'B-': 8, 'B MINUS': 8,
        'C+': 7, 'C PLUS': 7, 'C': 6, 'C-': 5, 'C MINUS': 5,
        'D+': 4, 'D PLUS': 4, 'D': 3, 'D-': 2, 'D MINUS': 2,
        'E': 1
    }

    return grade_map.get(grade, 0)


# ==================== NATURAL LANGUAGE INTEREST ANALYSIS (Fallback) ====================
def analyze_interest_text(interest_text):
    """
    Keyword-based interest analysis (offline fallback only).
    Returns: (interest_code, detected_interests_list)
    """
    if not interest_text or len(interest_text.strip()) < 3:
        return -1, ["unclear"]

    text = interest_text.lower().strip()

    interest_keywords = {
        0: {  # Technology & Engineering
            'technology', 'tech', 'computer', 'programming', 'coding', 'software', 'engineering',
            'it', 'ai', 'artificial intelligence', 'robotics', 'data', 'analytics', 'web', 'app',
            'mobile', 'game', 'gaming', 'cybersecurity', 'network', 'database', 'algorithm',
            'machine learning', 'automation', 'innovation', 'digital', 'electronics', 'hardware'
        },
        1: {  # Health Sciences
            'health', 'medical', 'doctor', 'nurse', 'pharmacy', 'medicine', 'hospital', 'patient',
            'healthcare', 'biology', 'anatomy', 'physiology', 'disease', 'treatment',
            'wellness', 'nutrition', 'pharmaceutical', 'therapy', 'surgery', 'clinic', 'care',
            'help people', 'healing', 'life science', 'biomedical'
        },
        2: {  # Business & Commerce
            'business', 'commerce', 'finance', 'accounting', 'marketing', 'management', 'entrepreneur',
            'startup', 'corporate', 'economy', 'trade', 'investment', 'banking', 'sales', 'leadership',
            'strategy', 'consulting', 'economics', 'profit', 'money', 'wealth', 'enterprise',
            'hotel', 'hospitality', 'governance'
        },
        3: {  # Humanities & Social Sciences
            'humanities', 'social science', 'psychology', 'sociology', 'history', 'politics', 'government',
            'international relations', 'law', 'justice', 'criminal', 'education', 'teaching', 'research',
            'society', 'culture', 'anthropology', 'philosophy', 'ethics', 'human behavior', 'community',
            'development', 'policy', 'diplomacy', 'understanding people'
        },
        4: {  # Creative Arts & Media
            'art', 'creative', 'design', 'media', 'film', 'animation', 'journalism', 'communication',
            'photography', 'music', 'theater', 'acting', 'writing', 'literature', 'graphic design',
            'advertising', 'broadcasting', 'entertainment', 'storytelling', 'visual', 'performance',
            'cinema', 'production', 'editing', 'content creation'
        }
    }

    undecided_keywords = {'not sure', 'undecided', 'unclear', 'confused', "don't know", 'unsure'}
    if any(keyword in text for keyword in undecided_keywords):
        return -1, ["undecided"]

    scores = {}
    detected_keywords = []

    for interest_code, keywords in interest_keywords.items():
        matches = [kw for kw in keywords if kw in text]
        scores[interest_code] = len(matches)
        if matches:
            detected_keywords.extend(matches[:3])

    if scores:
        best_interest = max(scores.items(), key=lambda x: x[1])
        if best_interest[1] > 0:
            return best_interest[0], list(set(detected_keywords))

    return -1, ["unclear interests"]


# ==================== RECOMMENDATION LOGIC ====================

def get_major_by_rules(scores, interest_code, interest_text=""):
    """
    Recommend a USIU-Africa major based on KCSE scores and interest.
    Enforces real USIU admission criteria.

    Args:
        scores: dict with subject points (0-12 each)
        interest_code: int (0-4) representing interest area
        interest_text: student's raw interest statement (for sub-interest nudging)

    Returns:
        tuple: (major_name, explanation, confidence_level)
    """
    math  = scores.get('math', 0)
    eng   = scores.get('english', 0)
    kisw  = scores.get('kiswahili', 0)
    bio   = scores.get('biology', 0)
    phy   = scores.get('physics', 0)
    chem  = scores.get('chemistry', 0)
    hum   = scores.get('humanities', 0)
    tech  = scores.get('tech_business', 0)

    text_lower = interest_text.lower()

    # ===== SCHOOL OF SCIENCE AND TECHNOLOGY (Interest 0) =====
    if interest_code == 0:
        is_ai   = any(kw in text_lower for kw in ['ai', 'robot', 'intelligence', 'automation', 'future'])
        is_data = any(kw in text_lower for kw in ['data', 'analytics', 'statistic', 'insight', 'analysis'])
        is_it   = any(kw in text_lower for kw in ['system', 'support', 'it ', 'network', 'database', 'infrastructure'])

        if math >= 11 and phy >= 11 and (is_ai or not (is_it or is_data)):
            return ('Artificial Intelligence (AI) & Robotics',
                    f"Outstanding STEM foundation (Math: {math}pts, Physics: {phy}pts). "
                    f"Your strengths perfectly align with the complex demands of AI and Robotics.",
                    95)
        elif math >= 10 and not is_it and not is_data:
            return ('Software Engineering',
                    f"Strong mathematical foundation (Math: {math}pts). "
                    f"Your analytical profile is ideal for designing and building robust software systems.",
                    90)
        elif math >= 9 and (is_data or tech >= 8):
            return ('Data Science and Analytics',
                    f"Your Math strength ({math}pts) combined with analytical interests "
                    f"positions you well for data-driven decision-making roles.",
                    85)
        elif is_it or math < 9:
            return ('Information Systems & Technology',
                    f"Your technology interest combined with your academic profile makes "
                    f"Information Systems an excellent fit — bridging IT and business needs.",
                    80)
        else:
            return ('Applied Computer Technology',
                    f"A versatile technology degree that covers programming, networks, and IT support. "
                    f"Excellent entry point into Kenya's growing tech industry.",
                    78)

    # ===== SCHOOL OF PHARMACY AND HEALTH SCIENCES (Interest 1) =====
    elif interest_code == 1:
        # Pharmacy: Requires strong Bio AND Chem (B grade minimum at USIU)
        if bio >= 9 and chem >= 9:
            return ('Pharmacy',
                    f"Strong scientific foundation (Biology: {bio}pts, Chemistry: {chem}pts). "
                    f"You have the precision and science depth needed for pharmaceutical practice.",
                    93)
        # Nursing: Requires Biology C+ minimum
        elif bio >= 7:
            return ('Nursing',
                    f"Your Biology grade ({bio}pts) meets Nursing requirements. "
                    f"Nursing offers meaningful, impactful patient care with strong career prospects in Kenya and globally.",
                    85)
        else:
            return ('Nursing',
                    f"Your passion for healthcare is your strongest asset. "
                    f"Nursing opens doors to patient care, community health, and healthcare leadership.",
                    72)

    # ===== CHANDARIA SCHOOL OF BUSINESS (Interest 2) =====
    elif interest_code == 2:
        is_hotel = any(kw in text_lower for kw in ['hotel', 'hospitality', 'restaurant', 'tourism', 'chef'])
        is_finance = any(kw in text_lower for kw in ['finance', 'investment', 'banking', 'money', 'accounting'])
        is_leadership = any(kw in text_lower for kw in ['lead', 'govern', 'manage', 'policy', 'government'])

        if math >= 11 and tech >= 10 and is_finance:
            return ('Accounting',
                    f"Exceptional numerical skills (Math: {math}pts, Business: {tech}pts). "
                    f"Accounting suits your systematic, detail-oriented analytical strength.",
                    92)
        elif math >= 10 and is_finance:
            return ('Finance',
                    f"Strong quantitative skills (Math: {math}pts) combined with financial interests "
                    f"make Finance a natural fit for investment and corporate banking careers.",
                    88)
        elif is_leadership and (eng >= 10 or hum >= 10):
            return ('Global Leadership and Governance',
                    f"Excellent communication (English: {eng}pts) and strategic thinking ability. "
                    f"Leadership and Governance prepares you for executive and public sector roles.",
                    85)
        elif is_hotel:
            return ('Hotel and Restaurant Management',
                    f"Your interest in hospitality aligns perfectly with this program. "
                    f"Kenya's growing tourism industry creates strong career opportunities.",
                    82)
        elif tech >= 8:
            return ('International Business Administration',
                    f"Strong business foundation (Tech/Business: {tech}pts). "
                    f"IBA provides broad exposure to international commerce and management.",
                    78)
        else:
            return ('International Business Administration',
                    f"A broad business interest with solid academic profile. "
                    f"IBA offers diverse pathways into entrepreneurship, management, and trade.",
                    70)

    # ===== SCHOOL OF HUMANITIES AND SOCIAL SCIENCES (Interest 3) =====
    elif interest_code == 3:
        is_law = any(kw in text_lower for kw in ['law', 'justice', 'criminal', 'police', 'legal', 'court'])
        is_psych = any(kw in text_lower for kw in ['psychology', 'mental', 'behavior', 'counsel', 'therapy', 'mind'])
        is_intl = any(kw in text_lower for kw in ['international', 'diplomacy', 'relations', 'global', 'policy', 'foreign'])

        if eng >= 10 and hum >= 10 and is_intl:
            return ('International Relations',
                    f"Excellent language skills (English: {eng}pts) and humanities foundation ({hum}pts). "
                    f"IR prepares you for diplomacy, NGO work, and global policy roles.",
                    90)
        elif is_law or hum >= 9:
            return ('Criminal Justice Studies',
                    f"Your interest in justice and law, backed by a strong humanities foundation ({hum}pts), "
                    f"makes Criminal Justice Studies an excellent fit.",
                    82)
        elif is_psych:
            return ('Psychology',
                    f"Your interest in understanding human behavior makes Psychology ideal. "
                    f"Psychology is applicable across counseling, HR, education, and research.",
                    80)
        else:
            return ('Psychology',
                    f"Your interest in people and society is at the core of Psychology. "
                    f"This degree provides foundational skills used across many professions.",
                    75)

    # ===== SCHOOL OF COMMUNICATION, CINEMATIC AND CREATIVE ARTS (Interest 4) =====
    elif interest_code == 4:
        is_film     = any(kw in text_lower for kw in ['film', 'movie', 'cinema', 'direct', 'video', 'production'])
        is_animate  = any(kw in text_lower for kw in ['animation', 'animate', 'cartoon', '3d', 'design', 'graphic'])
        is_journal  = any(kw in text_lower for kw in ['journalism', 'news', 'report', 'write', 'broadcast', 'media'])

        if is_animate and (tech >= 8 or math >= 8):
            return ('Animation',
                    f"Technical aptitude (Math/Tech: {max(math, tech)}pts) combined with creative passion. "
                    f"Animation is a rapidly growing field in Africa's digital media industry.",
                    87)
        elif is_journal or eng >= 10:
            return ('Journalism',
                    f"Strong English skills ({eng}pts) and communication interest. "
                    f"Journalism prepares you to shape public narrative in Kenya and beyond.",
                    85)
        elif is_film:
            return ('Film Production and Directing',
                    f"Your passion for storytelling through film is your compass. "
                    f"This program covers production, directing, and digital media creation.",
                    82)
        else:
            return ('Film Production and Directing',
                    f"Creative expression through visual media. "
                    f"Film Production opens doors to Kenya's growing entertainment industry.",
                    75)

    # ===== UNDECIDED / EXPLORATORY STUDENTS (Interest -1) =====
    if interest_code == -1 or interest_code is None:
        best_code, best_field, _ = determine_best_fit(scores)
        major, explanation, conf = get_major_by_rules(scores, best_code, interest_text)
        return (
            major,
            f"Because you are exploring your options, we analyzed your complete academic results across all KCSE subjects. "
            f"Your strongest competitive advantage is in {best_field}. {explanation}",
            max(conf, 85)
        )

    # Fallback
    return ('International Business Administration',
            "Based on your overall academic profile, a business foundation offers flexibility "
            "across many career paths at USIU-Africa.",
            75)


def determine_best_fit(scores):
    """
    For undecided students: calculates which USIU school best matches their academic strengths.

    Returns:
        tuple: (best_interest_code, field_name, calculated_scores_dict)
    """
    math = scores.get('math', 0)
    eng  = scores.get('english', 0)
    kisw = scores.get('kiswahili', 0)
    bio  = scores.get('biology', 0)
    phy  = scores.get('physics', 0)
    chem = scores.get('chemistry', 0)
    hum  = scores.get('humanities', 0)
    tech = scores.get('tech_business', 0)

    def _avg(values):
        """Average only subjects actually taken (score > 0)."""
        taken = [v for v in values if v > 0]
        return sum(taken) / len(taken) if taken else 0

    field_scores = {
        'Technology & Engineering':    _avg([math, phy, tech]),
        'Health Sciences':             _avg([bio, chem, math]),
        'Business & Commerce':         _avg([math, tech, eng]),
        'Humanities & Social Sciences': _avg([eng, kisw, hum]),
        'Creative Arts & Media':       _avg([eng, tech, hum]),
    }

    best_field = max(field_scores, key=field_scores.get)
    best_code  = INTEREST_MAP.get(best_field, 0)

    return best_code, best_field, field_scores


def check_eligibility(interest_code, scores):
    """
    Checks if student meets USIU-Africa minimum eligibility for their chosen field.
    Rules aligned to official USIU-Africa 2025/2026 admission criteria.

    Returns:
        tuple: (is_eligible: bool, guidance_message: str)
    """
    math = scores.get('math', 0)
    eng  = scores.get('english', 0)
    bio  = scores.get('biology', 0)
    chem = scores.get('chemistry', 0)
    phy  = scores.get('physics', 0)

    # --- Compulsory subjects (all USIU programs) ---
    if math == 0 or eng == 0:
        return False, "KCSE Mathematics and English are compulsory for ALL USIU-Africa programs."

    # --- Field-specific minimums ---
    if interest_code == 0:  # Technology & Engineering
        if math < 7:
            return False, "Technology programs at USIU require a minimum of C+ (7pts) in Mathematics."
        if phy > 0 and phy < 7:
            return False, "If you took Physics, a minimum of C+ (7pts) is required for Technology programs."

    elif interest_code == 1:  # Health Sciences
        # Pharmacy: needs Bio B (9pts) + Chem B (9pts)
        # Nursing:  needs Bio C+ (7pts); Chem recommended but not mandatory
        if bio == 0:
            return False, "Health Sciences programs require Biology. Please enter your Biology grade."
        if bio < 7:
            return False, "Health Sciences programs at USIU require a minimum of C+ (7pts) in Biology."
        # Only flag Chem if it was taken and is below C
        if chem > 0 and chem < 6:
            return False, "If you took Chemistry, a minimum of C (6pts) is required for Health Sciences programs."

    elif interest_code == 2:  # Business & Commerce
        if math < 6:
            return False, "Business programs at USIU require a minimum of C (6pts) in Mathematics."

    elif interest_code == 3:  # Humanities & Social Sciences
        if eng < 6:
            return False, "Humanities programs at USIU require a minimum of C (6pts) in English."

    elif interest_code == 4:  # Creative Arts & Media
        if eng < 5:
            return False, "Creative Arts programs at USIU require a minimum of C- (5pts) in English."

    return True, "Your grades meet the minimum requirements for this field at USIU-Africa."


def generate_report(major, school, scores, confidence, explanation, is_alternative=False):
    """Generates a structured recommendation report dict."""
    return {
        'major': major,
        'school': school,
        'confidence': confidence,
        'explanation': explanation,
        'is_alternative': is_alternative,
        'scores_summary': {
            'Math':         f"{scores.get('math', 0)}pts",
            'English':      f"{scores.get('english', 0)}pts",
            'Kiswahili':    f"{scores.get('kiswahili', 0)}pts",
            'Biology':      f"{scores.get('biology', 0)}pts"      if scores.get('biology', 0) > 0 else "Not taken",
            'Physics':      f"{scores.get('physics', 0)}pts"      if scores.get('physics', 0) > 0 else "Not taken",
            'Chemistry':    f"{scores.get('chemistry', 0)}pts"    if scores.get('chemistry', 0) > 0 else "Not taken",
            'Humanities':   f"{scores.get('humanities', 0)}pts",
            'Tech/Business': f"{scores.get('tech_business', 0)}pts" if scores.get('tech_business', 0) > 0 else "Not taken",
        }
    }
