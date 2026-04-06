"""
Advanced AI Interest Analyzer for USIU-Africa Major Recommendation System
Uses Google Gemini AI (Modern SDK) as primary analyzer for intelligent student interest analysis.

Priority:
1. Gemini AI (google-genai) - Primary, most capable
2. OpenAI GPT-4 - Optional legacy fallback
3. Enhanced keyword/semantic analysis - Offline fallback
"""

import os
from typing import Tuple, List, Dict
import json

# --- Optional: Gemini AI (Primary - Modern SDK) ---
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


# ==================== INTEREST TO MAJOR MAPPING ====================

# Type definition for the mapping
from typing import Any
FieldData = Dict[str, Any]

INTEREST_MAJOR_MAP: Dict[str, FieldData] = {
    "Technology & Engineering": {
        "majors": [
            "Applied Computer Technology",
            "Artificial Intelligence (AI) & Robotics",
            "Software Engineering",
            "Cybersecurity",
            "Data Science & Analytics",
            "Information Technology"
        ],
        "school": "School of Science and Technology",
        "base_confidence": 85,
        "human_interaction": 2
    },
    "Health Sciences": {
        "majors": [
            "Nursing",
            "Public Health",
            "Pharmaceutical Sciences",
            "Biomedical Sciences",
            "Health Management",
            "Clinical Medicine"
        ],
        "school": "School of Health Sciences",
        "base_confidence": 80,
        "human_interaction": 5
    },
    "Business & Commerce": {
        "majors": [
            "International Business Administration",
            "Accounting",
            "Finance",
            "Entrepreneurship",
            "Marketing Management",
            "Supply Chain Management"
        ],
        "school": "Chandaria School of Business",
        "base_confidence": 75,
        "human_interaction": 4
    },
    "Humanities & Social Sciences": {
        "majors": [
            "International Relations",
            "Political Science",
            "History & Archaeology",
            "Psychology",
            "Sociology",
            "Development Studies"
        ],
        "school": "School of Humanities and Social Sciences",
        "base_confidence": 75,
        "human_interaction": 5
    },
    "Creative Arts & Media": {
        "majors": [
            "Communication & Media Studies",
            "Graphic Design & Multimedia",
            "Film & Digital Production",
            "Journalism & Broadcasting",
            "Creative Writing",
            "Visual Arts"
        ],
        "school": "School of Humanities and Social Sciences",
        "base_confidence": 70,
        "human_interaction": 3
    }
}

# ==================== INTERACTION PREFERENCE DETECTION ====================

def detect_interaction_preference(text: str) -> Tuple[int, str]:
    """Detect student's preference for human interaction."""
    text = text.lower().strip()
    
    high_words = {
        'people', 'help', 'helping', 'communication', 'communicate', 'interact',
        'teamwork', 'team', 'collaboration', 'collaborate', 'social', 'community',
        'leadership', 'lead', 'leading', 'guide', 'mentor', 'coaching', 'client',
        'customer', 'service', 'presentation', 'counseling', 'advising', 'teaching',
        'networking', 'relationship', 'empathy', 'psychology', 'influence', 'inspire',
        'motivate', 'support'
    }

    low_words = {
        'alone', 'solitary', 'independent', 'solo', 'individual', 'data',
        'analysis', 'analytical', 'research', 'coding', 'programming', 'technical',
        'computer', 'algorithm', 'logical', 'debugging', 'automation', 'experiment',
        'laboratory', 'theory', 'structured', 'precise', 'accurate'
    }

    avoid_phrases = {
        'not good with people', 'avoid people', 'hate people',
        'people drain me', 'prefer alone', 'introvert', 'shy'
    }

    high_count = sum(1 for w in high_words if w in text.split() or f' {w} ' in f' {text} ')
    low_count = sum(1 for w in low_words if w in text.split() or f' {w} ' in f' {text} ')
    avoid_count = sum(1 for p in avoid_phrases if p in text)

    if avoid_count > 0:
        return -2, "Strongly prefers working independently"
    elif low_count > high_count + 1:
        return -1, "Prefers independent/analytical work"
    elif high_count > low_count + 1:
        return 2, "Very people-oriented, loves interaction"
    elif high_count > 0:
        return 1, "Enjoys some human interaction"
    else:
        return 0, "Flexible/no clear preference"


def adjust_confidence_for_interaction(base_confidence: float, interaction_score: int, category: str) -> Tuple[float, str]:
    """Adjust confidence based on alignment between student interaction preference and field."""
    # Defensive lookup
    field_data = INTEREST_MAJOR_MAP.get(category, {})
    category_interaction = int(field_data.get("human_interaction", 3))

    if interaction_score == 0:
        return float(base_confidence), "No interaction preference indicated"

    adjustment = 0
    reason = "Moderate alignment with your interaction preference"

    if interaction_score > 0:
        if category_interaction >= 4:
            adjustment, reason = 10, "Strong alignment: You're people-oriented and this field is collaborative"
        elif category_interaction <= 2:
            adjustment, reason = -5, "Consider: This field is more independent than collaborative"
    elif interaction_score < 0:
        if category_interaction <= 2:
            adjustment, reason = 8, "Great fit: This field offers independent work opportunities"
        elif category_interaction >= 4:
            adjustment, reason = -8, "Advisory: This field requires significant people interaction"

    final_confidence = max(30, min(99, int(base_confidence + adjustment)))
    return float(final_confidence), reason


def rank_majors_by_interaction(majors: List[str], category: str, interaction_score: int) -> List[str]:
    """Re-rank majors based on student's interaction preference."""
    major_interaction_levels = {
        "Applied Computer Technology": 2, "Artificial Intelligence (AI) & Robotics": 1,
        "Software Engineering": 2, "Cybersecurity": 1, "Data Science & Analytics": 1,
        "Information Technology": 2, "Nursing": 5, "Public Health": 4,
        "Pharmaceutical Sciences": 2, "Biomedical Sciences": 1, "Health Management": 4,
        "Clinical Medicine": 5, "International Business Administration": 5,
        "Accounting": 2, "Finance": 2, "Entrepreneurship": 4, "Marketing Management": 5,
        "Supply Chain Management": 3, "International Relations": 5, "Political Science": 4,
        "History & Archaeology": 2, "Psychology": 4, "Sociology": 4,
        "Development Studies": 5, "Communication & Media Studies": 5,
        "Graphic Design & Multimedia": 2, "Film & Digital Production": 3,
        "Journalism & Broadcasting": 4, "Creative Writing": 1, "Visual Arts": 1,
    }
    if interaction_score == 0: return majors
    scored = []
    for major in majors:
        level = major_interaction_levels.get(major, 3)
        score = level if interaction_score > 0 else (6 - level)
        scored.append((major, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored]


# ==================== GEMINI AI ANALYSIS (Modern SDK) ====================

def analyze_interest_with_gemini(interest_text: str, scores: Dict = None) -> Tuple[str | None, float, List[str], str, str]:
    """Use Gemini AI to analyze interests and recommend a field."""
    if not HAS_GEMINI: return None, 0, [], "", ""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key: return None, 0, [], "", ""

    try:
        client = genai.Client(api_key=api_key)
        grade_map = {12:'A', 11:'A-', 10:'B+', 9:'B', 8:'B-', 7:'C+', 6:'C', 5:'C-', 4:'D+', 3:'D', 2:'D-', 1:'E'}
        grade_context = ""
        if scores:
            grade_lines = [f"{k}: {grade_map.get(v, v)}" for k, v in scores.items() if v > 0]
            grade_context = f"\nStudent Grades: {', '.join(grade_lines)}"

        # Prepare major list for Gemini
        major_list = []
        for cat, data in INTEREST_MAJOR_MAP.items():
            for m in data['majors']:
                major_list.append(f"- {m} ({data['school']})")
        
        majors_text = "\n".join(major_list)

        prompt = f"""You are a professional Academic Advisor at USIU-Africa. 
Analysis Task: Recommend the MOST relevant MAJOR from the list below based on the student's INTEREST STATEMENT. 

Majors and Schools at USIU-Africa:
{majors_text}

Rules:
1. PRIORITIZE career goals over grades. If they say "manager", favor Business majors.
2. Provide a UNIQUE, warm, and professional explanation (2-3 sentences). 
3. Explicitly reference specific words from the student's interest statement in your reasoning.
4. Your response must be in English.

{grade_context}
Interest Statement: "{interest_text}"

Return ONLY JSON with these exact keys:
{{
  "category": "One of: Technology & Engineering, Health Sciences, Business & Commerce, Humanities & Social Sciences, Creative Arts & Media",
  "recommended_major": "The specific major name from the list provided",
  "confidence": 70-95,
  "reasoning": "A unique, personalized explanation connecting their interests and grades.",
  "key_interests": ["3-4 relevant keywords from their text"]
}}"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        result = json.loads(response.text)
        category = result.get("category", "").strip()
        
        # Validating category
        valid = list(INTEREST_MAJOR_MAP.keys())
        if category not in valid:
            for v in valid:
                if v.lower() in category.lower(): category = v; break
            else: return None, 0, [], "", ""

        return category, float(result.get("confidence", 70)), result.get("key_interests", []), result.get("reasoning", ""), result.get("recommended_major", "")
    except Exception as e:
        print(f"Gemini error: {e}")
        return None, 0, [], "", ""


# ==================== OFFLINE FALLBACK ====================

def _offline_analysis(text: str, grades: Dict, interaction_score: int, interaction_pref: str) -> Tuple[str, float, List[str], str]:
    """Very simple keyword fallback when AI is unavailable."""
    keywords = {
        "Technology & Engineering": ['tech', 'code', 'computer', 'software', 'ai'],
        "Health Sciences": ['doctor', 'nurse', 'medicine', 'health'],
        "Business & Commerce": ['business', 'finance', 'marketing', 'accounting'],
        "Humanities & Social Sciences": ['politics', 'social', 'history', 'law'],
        "Creative Arts & Media": ['film', 'design', 'art', 'media']
    }
    
    best_cat, best_count = "Undecided", 0
    found_kws = []
    text_lower = text.lower()
    
    for cat, kws in keywords.items():
        matches = [kw for kw in kws if kw in text_lower]
        if len(matches) > best_count:
            best_count = len(matches)
            best_cat = cat
            found_kws = matches

    conf = 60 if best_count > 0 else 30
    reasoning = generate_analytical_reasoning(best_cat, found_kws, grades, interaction_pref, conf)
    return best_cat, conf, found_kws, reasoning


def generate_analytical_reasoning(category, keywords, grades, interaction, confidence):
    parts = [f"📌 Interests: {', '.join(keywords) if keywords else category}"]
    if grades:
        subj = {'math':'Math'}
        if category == "Technology & Engineering": subj.update({'physics':'Physics'})
        elif category == "Business & Commerce": subj.update({'tech_business':'Business'})
        elif category == "Health Sciences": subj.update({'biology':'Bio', 'chemistry':'Chem'})
        
        grade_str = ", ".join([f"{v}: {grades.get(k)}" for k, v in subj.items() if grades.get(k)])
        if grade_str: parts.append(f"📊 Grades: {grade_str}")
    
    parts.append(f"🎯 Confidence: {confidence}%")
    return " | ".join(parts)


def analyze_interest_text_advanced(interest_text: str, grades_dict: Dict = None) -> Tuple[str, float, List[str], str, str]:
    """Main entry point: Attempts Gemini analysis, falls back to keywords."""
    interaction_score, interaction_pref = detect_interaction_preference(interest_text)
    
    # 1. Gemini AI (Primary)
    cat, conf, kws, reason, major = analyze_interest_with_gemini(interest_text, grades_dict)
    if cat:
        conf, note = adjust_confidence_for_interaction(conf, interaction_score, cat)
        final_statement = f"{reason} Furthermore, {note.lower()}." if note and "no interaction" not in note.lower() else reason
        return cat, conf, kws, final_statement, major

    # 2. Offline Fallback
    cat, conf, kws, reason = _offline_analysis(interest_text, grades_dict, interaction_score, interaction_pref)
    return cat, conf, kws, reason, ""


def get_major_recommendation(interest_category: str, confidence: float, grades_dict: Dict = None, interaction_score: int = 0) -> Dict:
    data = INTEREST_MAJOR_MAP.get(interest_category, INTEREST_MAJOR_MAP["Humanities & Social Sciences"])
    ranked = rank_majors_by_interaction(data["majors"], interest_category, interaction_score)
    
    final_conf = data["base_confidence"]
    if grades_dict:
        # FIX: Lowercase keys matching app.py
        rel = []
        if interest_category == "Technology & Engineering": rel = [grades_dict.get('math', 0), grades_dict.get('physics', 0)]
        elif interest_category == "Health Sciences": rel = [grades_dict.get('biology', 0), grades_dict.get('chemistry', 0)]
        elif interest_category == "Business & Commerce": rel = [grades_dict.get('math', 0), grades_dict.get('tech_business', 0)]
        
        valid = [v for v in rel if v > 0]
        if valid:
            avg = sum(valid) / len(valid)
            if avg >= 10: final_conf += 10
            elif avg < 6: final_conf -= 10

    return {
        "major": ranked[0], "school": data["school"], 
        "confidence": int((final_conf + confidence) / 2),
        "reason": f"Based on {interest_category} profile"
    }


def analyze_interest_text(interest_text: str):
    cat, conf, kws, reason, major = analyze_interest_text_advanced(interest_text)
    codes = {"Technology & Engineering": 0, "Health Sciences": 1, "Business & Commerce": 2, "Humanities & Social Sciences": 3, "Creative Arts & Media": 4}
    return codes.get(cat, -1), kws
