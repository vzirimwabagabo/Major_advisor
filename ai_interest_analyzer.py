"""
Advanced AI Interest Analyzer for University Major Recommendation System.
Uses Google Gemini AI as primary analyzer for intelligent student interest analysis.
Supports multi-country curricula (KCSE, Rwanda NESB, Uganda UACE, WASSCE, Cambridge)
and multi-university catalogs (USIU-Africa, Strathmore, ALU, Makerere, Ashesi, Pan-African).

Priority:
  1. Gemini AI (google-genai) — Primary
  2. Academic Aptitude & Keyword Analysis — Robust Offline fallback
"""

import os
import json
from typing import Tuple, List, Dict, Any

from education_systems import UNIVERSITIES, CURRICULA
from recommendations import PROGRAMS, MAJOR_TO_SCHOOL, INTEREST_MAP, determine_best_fit

# --- Gemini SDK ---
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


# ==================== DEFAULT USIU INTEREST -> MAJOR MAP ====================

FieldData = Dict[str, Any]

INTEREST_MAJOR_MAP: Dict[str, FieldData] = {
    "Technology & Engineering": {
        "majors": PROGRAMS["School of Science and Technology"],
        "school": "School of Science and Technology",
        "base_confidence": 88,
        "human_interaction": 2,
    },
    "Health Sciences": {
        "majors": PROGRAMS["School of Pharmacy and Health Sciences"],
        "school": "School of Pharmacy and Health Sciences",
        "base_confidence": 88,
        "human_interaction": 5,
    },
    "Business & Commerce": {
        "majors": PROGRAMS["Chandaria School of Business"],
        "school": "Chandaria School of Business",
        "base_confidence": 85,
        "human_interaction": 4,
    },
    "Humanities & Social Sciences": {
        "majors": PROGRAMS["School of Humanities and Social Sciences"],
        "school": "School of Humanities and Social Sciences",
        "base_confidence": 82,
        "human_interaction": 5,
    },
    "Creative Arts & Media": {
        "majors": PROGRAMS["School of Communication, Cinematic and Creative Arts"],
        "school": "School of Communication, Cinematic and Creative Arts",
        "base_confidence": 80,
        "human_interaction": 3,
    },
}

VALID_MAJOR_NAMES: set = {m for data in INTEREST_MAJOR_MAP.values() for m in data["majors"]}

def _build_uni_catalog_text(target_uni: str = "usiu") -> Tuple[str, set, Dict[str, str]]:
    """Builds program text and lookup sets for the specified university."""
    uni_data = UNIVERSITIES.get(target_uni, UNIVERSITIES["usiu"])
    catalog = uni_data.get("catalog", {})
    
    # If Pan-African, combine all
    if target_uni == "all" or not catalog:
        lines = []
        valid_majors = set()
        major_to_school = {}
        for uid, udata in UNIVERSITIES.items():
            if uid == "all":
                continue
            u_name = udata["name"]
            for school, majors in udata.get("catalog", {}).items():
                for major in majors:
                    display_m = f"{major} — {u_name}"
                    lines.append(f"- {display_m} ({school})")
                    valid_majors.add(display_m)
                    valid_majors.add(major)
                    major_to_school[display_m] = f"{school}, {u_name}"
                    major_to_school[major] = f"{school}, {u_name}"
        return "\n".join(lines), valid_majors, major_to_school

    lines = []
    valid_majors = set()
    major_to_school = {}
    for school, majors in catalog.items():
        for major in majors:
            lines.append(f"- {major} ({school})")
            valid_majors.add(major)
            major_to_school[major] = f"{school}, {uni_data['name']}"
    return "\n".join(lines), valid_majors, major_to_school


# Reliable modern Gemini models in order of priority
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-3.8-flash"
]


# ==================== INTERACTION PREFERENCE DETECTION ====================

def detect_interaction_preference(text: str) -> Tuple[int, str]:
    """Detect student's preference for human vs. independent work."""
    text = text.lower().strip()

    high_words = {
        'people', 'help', 'helping', 'communication', 'communicate', 'interact',
        'teamwork', 'team', 'collaboration', 'collaborate', 'social', 'community',
        'leadership', 'lead', 'leading', 'guide', 'mentor', 'coaching',
        'customer', 'service', 'presentation', 'counseling', 'teaching',
        'networking', 'relationship', 'empathy', 'inspire', 'motivate', 'support'
    }
    low_words = {
        'alone', 'solitary', 'independent', 'solo', 'individual', 'data',
        'analysis', 'analytical', 'research', 'coding', 'programming', 'technical',
        'computer', 'algorithm', 'logical', 'debugging', 'automation', 'experiment',
        'systems', 'software', 'hardware', 'math', 'statistics', 'deep focus'
    }

    # Avoid people keywords
    interaction_avoid = {
        'not good with people', 'avoid people', 'hate people',
        'people drain me', 'prefer alone', 'introvert', 'shy'
    }

    high_count = sum(1 for w in high_words if w in text)
    low_count  = sum(1 for w in low_words  if w in text)
    avoid_count = sum(1 for w in interaction_avoid if w in text)

    # Calculate preference score (-2 to +2)
    if avoid_count > 0:
        score = -2
        pref_type = "Strongly prefers working independently"
    elif low_count > high_count + 1:
        score = -1
        pref_type = "Prefers independent/analytical work"
    elif high_count > low_count + 1:
        score = 2
        pref_type = "Very people-oriented, loves interaction"
    elif high_count > 0:
        score = 1
        pref_type = "Enjoys some human interaction"
    else:
        score = 0
        pref_type = "Flexible/no clear preference"

    return score, pref_type


def adjust_confidence_for_interaction(
    base_confidence: float,
    interaction_score: int,
    field_category: str
) -> Tuple[float, str]:
    """Fine-tunes recommendation confidence based on social preference alignment."""
    field_data = INTEREST_MAJOR_MAP.get(field_category)
    if not field_data:
        return base_confidence, ""

    expected = field_data["human_interaction"]
    if interaction_score > 0 and expected >= 4:
        return min(base_confidence + 2.0, 95.0), "Strong alignment between collaborative preference and field dynamics"
    elif interaction_score < 0 and expected <= 3:
        return min(base_confidence + 2.0, 95.0), "Strong alignment with independent focus in this field"
    return base_confidence, ""


# ==================== GEMINI AI ANALYSIS ====================

def analyze_interest_with_gemini(
    interest_text: str,
    scores: Dict = None,
    username: str = "Student",
    target_uni: str = "usiu",
    country: str = "Kenya",
    curriculum_name: str = "KCSE"
) -> Tuple[str | None, float, List[str], str, str, str]:
    """
    Use Gemini AI to analyze student interests, academic strengths,
    and recommend a verified university major based on their country and target university.
    """
    if not HAS_GEMINI:
        return None, 0, [], "", "", ""

    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        return None, 0, [], "", "", ""

    uni_data = UNIVERSITIES.get(target_uni, UNIVERSITIES["usiu"])
    uni_name = uni_data["name"]
    majors_text, valid_majors, major_to_school = _build_uni_catalog_text(target_uni)

    try:
        client = genai.Client(api_key=api_key)

        grade_context = ""
        if scores:
            grade_lines = [f"{k.capitalize()}: {v} points (0-12 scale)" for k, v in scores.items() if v > 0]
            grade_context = f"\nStudent High School Academic Profile ({curriculum_name}, {country}): {', '.join(grade_lines)}"

        prompt = f"""You are a senior, encouraging Academic Advisor helping high school graduates transition into university.
The student is applying from {country} with a background in the {curriculum_name} curriculum.
Target University: {uni_name}.

Your task: Analyze this student's academic performance and personal interest statement, and recommend exactly ONE official major from the verified university catalog below.

VERIFIED UNIVERSITY PROGRAM CATALOG (select ONLY from this list):
{majors_text}

Advisory Principles:
1. PERSONALIZATION: Address the student warmly by name: "Hi {username}, ..."
2. HIGH ACHIEVERS / UNDECIDED STUDENTS:
   - If the student is undecided, unsure, or says things like "not sure", "don't know", or "exploring":
     CELEBRATE their academic versatility! DO NOT default to generic business degrees unless their grades actually indicate business strengths.
     Look at their highest grades. If they have top STEM grades (Math, Sciences, Tech), recommend high-impact, prestigious programs like Computer Science, Software Engineering, Pharmacy, or Engineering.
     Assign an authoritative confidence score (86-94%) reflecting their proven competence.
3. CLEAR CAREER INTEREST: If the student describes a clear passion (e.g. healthcare, business, creative arts, international relations), align with their passion while verifying their academic foundation.
4. REASONING QUALITY: Explain clearly WHY this major at {uni_name} fits their grades, curriculum strengths, and career aspirations.
5. MAJOR CONSTRAINT: recommended_major MUST match EXACTLY one of the program names listed in the catalog above.

{grade_context}
Student Interest Statement: "{interest_text[:1500]}"

Return ONLY valid JSON with these exact keys:
{{
  "category": "One of: Technology & Engineering, Health Sciences, Business & Commerce, Humanities & Social Sciences, Creative Arts & Media",
  "recommended_major": "EXACT major name from the catalog above",
  "confidence": <integer 75-95>,
  "reasoning": "Inspirational, conversational guidance starting with Hi {username}...",
  "key_interests": ["keyword1", "keyword2", "keyword3"]
}}"""

        # Try models in order of resilience
        response = None
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                if response and response.text:
                    break
            except Exception:
                continue

        if not response or not response.text:
            return None, 0, [], "", "", ""

        result = json.loads(response.text)

        category = result.get("category", "").strip()
        valid_categories = list(INTEREST_MAJOR_MAP.keys())
        if category not in valid_categories:
            for v in valid_categories:
                if v.lower() in category.lower() or category.lower() in v.lower():
                    category = v
                    break
            else:
                return None, 0, [], "", "", ""

        recommended_major = result.get("recommended_major", "").strip()
        matched_school = ""

        # Normalize recommended major against valid catalog
        if recommended_major in valid_majors:
            matched_school = major_to_school.get(recommended_major, uni_name)
        else:
            for valid_m in valid_majors:
                if recommended_major.lower() in valid_m.lower() or valid_m.lower() in recommended_major.lower():
                    recommended_major = valid_m
                    matched_school = major_to_school.get(valid_m, uni_name)
                    break
            else:
                recommended_major = ""

        conf = float(result.get("confidence", 85))
        conf = max(75, min(95, conf))

        return (
            category,
            conf,
            result.get("key_interests", []),
            result.get("reasoning", ""),
            recommended_major,
            matched_school
        )

    except Exception as e:
        print(f"[Gemini] Error during analysis: {e}")
        return None, 0, [], "", "", ""


# ==================== ROBUST OFFLINE ACADEMIC ANALYSIS ====================

def _offline_analysis(
    text: str,
    grades: Dict,
    interaction_score: int,
    interaction_pref: str,
    username: str = "Student",
    target_uni: str = "usiu",
    country: str = "Kenya",
    curriculum_name: str = "KCSE"
) -> Tuple[str, float, List[str], str, str, str]:
    """
    Intelligent fallback when Gemini is offline.
    Evaluates both keyword interests AND academic cluster scores for the target university.
    """
    keywords = {
        "Technology & Engineering":    ['tech', 'code', 'computer', 'software', 'ai', 'engineering', 'programming', 'robot', 'data'],
        "Health Sciences":             ['doctor', 'nurse', 'medicine', 'health', 'pharmacy', 'hospital', 'patient', 'clinic', 'bio'],
        "Business & Commerce":         ['business', 'finance', 'marketing', 'accounting', 'management', 'entrepreneur', 'money', 'trade'],
        "Humanities & Social Sciences": ['politics', 'social', 'history', 'law', 'justice', 'psychology', 'relations', 'society', 'diplomacy'],
        "Creative Arts & Media":       ['film', 'design', 'art', 'media', 'animation', 'journalism', 'writing', 'directing'],
    }

    text_lower = text.lower()
    best_cat, best_count, found_kws = None, 0, []

    for cat, kws in keywords.items():
        matches = [kw for kw in kws if kw in text_lower]
        if len(matches) > best_count:
            best_count = len(matches)
            best_cat = cat
            found_kws = matches

    # If student is undecided or has no keyword matches, use academic cluster analysis
    if best_count == 0 or not best_cat or any(w in text_lower for w in ['not sure', 'undecided', "don't know", 'unsure', 'exploring']):
        best_code, best_field, field_scores = determine_best_fit(grades)
        best_cat = best_field
        found_kws = ["Academic Strengths", "Multidisciplinary Aptitude"]

    taken_scores = [v for v in grades.values() if isinstance(v, (int, float)) and v > 0]
    avg_score = sum(taken_scores) / len(taken_scores) if taken_scores else 6.0

    if avg_score >= 11:
        conf = 92.0
    elif avg_score >= 9:
        conf = 86.0
    elif avg_score >= 7:
        conf = 80.0
    else:
        conf = 72.0

    uni_data = UNIVERSITIES.get(target_uni, UNIVERSITIES["usiu"])
    uni_name = uni_data["name"]

    # Select major from target university matching the category
    major_candidate = ""
    school_candidate = uni_name
    catalog = uni_data.get("catalog", {})

    category_to_school_keywords = {
        "Technology & Engineering": ["science", "computing", "engineering", "technology"],
        "Health Sciences": ["health", "pharmacy", "medical"],
        "Business & Commerce": ["business", "commerce", "management"],
        "Humanities & Social Sciences": ["humanities", "social", "law", "arts"],
        "Creative Arts & Media": ["communication", "cinematic", "creative", "media"]
    }

    match_keywords = category_to_school_keywords.get(best_cat, ["science"])
    for school_name, majors in catalog.items():
        if any(kw in school_name.lower() for kw in match_keywords):
            if majors:
                major_candidate = majors[0]
                school_candidate = f"{school_name}, {uni_name}"
                break

    if not major_candidate and catalog:
        # Default to first available program
        first_school = list(catalog.keys())[0]
        major_candidate = catalog[first_school][0]
        school_candidate = f"{first_school}, {uni_name}"

    reasoning = (
        f"Hi {username}, based on your {curriculum_name} academic strengths from {country}, "
        f"your profile aligns exceptionally well with {best_cat}. "
        f"With an average normalized subject score of {avg_score:.1f} points, "
        f"we recommend pursuing this pathway at {uni_name}."
    )

    return best_cat, conf, found_kws, reasoning, major_candidate, school_candidate


# ==================== MAIN ENTRY POINT ====================

def analyze_interest_text_advanced(
    interest_text: str,
    grades_dict: Dict = None,
    username: str = "Student",
    target_uni: str = "usiu",
    country: str = "Kenya",
    curriculum_id: str = "ke_kcse"
) -> Tuple[str, float, List[str], str, str, str]:
    """
    Main entry point for AI analysis.
    Tries resilient Gemini models first, falls back to academic cluster analysis.
    Returns: (category, confidence, keywords, reasoning, recommended_major, school)
    """
    curr = CURRICULA.get(curriculum_id, CURRICULA["ke_kcse"])
    curriculum_name = curr["name"]

    interaction_score, interaction_pref = detect_interaction_preference(interest_text)

    # 1. Try Gemini (Primary)
    cat, conf, kws, reason, major, school = analyze_interest_with_gemini(
        interest_text=interest_text,
        scores=grades_dict,
        username=username,
        target_uni=target_uni,
        country=country,
        curriculum_name=curriculum_name
    )
    if cat and major:
        conf, note = adjust_confidence_for_interaction(conf, interaction_score, cat)
        final_statement = reason
        if note and "no interaction" not in note.lower():
            final_statement = f"{reason} {note}."
        return cat, conf, kws, final_statement, major, school

    # 2. Offline fallback
    cat, conf, kws, reason, major, school = _offline_analysis(
        text=interest_text,
        grades=grades_dict or {},
        interaction_score=interaction_score,
        interaction_pref=interaction_pref,
        username=username,
        target_uni=target_uni,
        country=country,
        curriculum_name=curriculum_name
    )
    return cat, conf, kws, reason, major, school


def get_major_recommendation(interest_category: str, confidence: float, grades_dict: Dict = None, interaction_score: int = 0) -> Dict:
    data = INTEREST_MAJOR_MAP.get(interest_category, INTEREST_MAJOR_MAP["Humanities & Social Sciences"])
    majors = data["majors"]

    if interaction_score > 0:
        majors = list(reversed(majors))

    return {
        "major":      majors[0],
        "school":     data["school"],
        "confidence": int(confidence),
        "reason":     f"Based on {interest_category} profile",
    }


def analyze_interest_text(interest_text: str):
    cat, conf, kws, reason, major, school = analyze_interest_text_advanced(interest_text)
    code_map = {
        "Technology & Engineering": 0,
        "Health Sciences": 1,
        "Business & Commerce": 2,
        "Humanities & Social Sciences": 3,
        "Creative Arts & Media": 4,
        "Undecided": -1
    }
    return code_map.get(cat, -1), kws
