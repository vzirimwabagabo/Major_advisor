"""
Advanced AI Interest Analyzer for Major Recommendation System
Uses NLP to intelligently understand student interests and map to majors

Features:
- Natural Language Processing (NLP)
- Semantic similarity analysis
- Optional GPT-4 integration for complex cases
- Confidence scoring
- Context-aware recommendations
"""

import os
from typing import Tuple, List, Dict
import json

# Optional: AI service integration
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ==================== INTEREST TO MAJOR MAPPING ====================
INTEREST_MAJOR_MAP = {
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
        "human_interaction": 2  # Low interaction (1=low, 5=high)
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
        "human_interaction": 5  # Very high interaction (direct patient care)
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
        "human_interaction": 4  # High interaction (leadership, client-facing)
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
        "human_interaction": 5  # Very high interaction (people-centered)
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
        "human_interaction": 3  # Moderate interaction (audience, collaboration)
    }
}

# ==================== ADVANCED NLP ANALYZER ====================

def detect_interaction_preference(text: str) -> Tuple[int, str]:
    """
    Detect student's preference for human interaction.
    
    Returns:
        (preference_score, preference_type)
        - preference_score: -2 (avoid people) to +2 (loves people)
        - preference_type: description of their preference
    """
    text = text.lower().strip()
    
    # High interaction keywords (people-focused)
    interaction_high = {
        'people', 'help', 'helping', 'helping people', 'working with people', 
        'communication', 'communicate', 'interact', 'interaction', 'connect',
        'teamwork', 'team', 'collaboration', 'collaborate', 'social', 'community',
        'leadership', 'lead', 'leading', 'guide', 'mentor', 'coaching',
        'client', 'customer', 'service', 'leadership', 'persuade',
        'public speaking', 'presentation', 'counseling', 'advising', 'teaching',
        'organization', 'organizing people', 'networking', 'relationship',
        'empathy', 'understand people', 'psychology', 'psychology',
        'influence', 'inspire', 'motivate', 'support'
    }
    
    # Low interaction keywords (solo/analytical work)
    interaction_low = {
        'alone', 'solitary', 'independent', 'solo', 'by myself', 'individual',
        'data', 'analysis', 'analytical', 'research', 'problem solving',
        'coding', 'programming', 'technical', 'computer', 'algorithm',
        'algorithm', 'logical', 'technical skills', 'problem', 'coding',
        'concentration', 'focused', 'detail', 'precise', 'accurate',
        'system', 'structure', 'organized', 'logical', 'technical',
        'debugging', 'configuration', 'automation', 'experiment',
        'research', 'laboratory', 'analysis', 'theory'
    }
    
    # Avoid people keywords
    interaction_avoid = {
        'not good with people', 'avoid people', 'hate people',
        'people drain me', 'prefer alone', 'introvert', 'shy'
    }
    
    # Count matches
    high_count = sum(1 for kw in interaction_high if kw in text)
    low_count = sum(1 for kw in interaction_low if kw in text)
    avoid_count = sum(1 for kw in interaction_avoid if kw in text)
    
    # Calculate preference score
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

def adjust_confidence_for_interaction(base_confidence: float, interaction_score: int, category: str) -> Tuple[float, str]:
    """
    Adjust confidence based on interaction preference and category alignment.
    
    Returns:
        (adjusted_confidence, adjustment_reason)
    """
    category_interaction = INTEREST_MAJOR_MAP.get(category, {}).get("human_interaction", 3)
    
    if interaction_score == 0:
        # No preference stated
        return base_confidence, "No interaction preference indicated"
    
    # Calculate compatibility
    if interaction_score > 0 and category_interaction >= 4:
        # Student loves people, category is high interaction
        adjustment = 10
        reason = "Strong alignment: You're people-oriented and this field is collaborative"
    elif interaction_score > 0 and category_interaction <= 2:
        # Student loves people, category is low interaction
        adjustment = -5
        reason = "Consider: This field is more independent than collaborative"
    elif interaction_score < 0 and category_interaction <= 2:
        # Student prefers solo work, category is low interaction
        adjustment = 8
        reason = "Great fit: This field offers independent work opportunities"
    elif interaction_score < 0 and category_interaction >= 4:
        # Student prefers solo work, category is high interaction
        adjustment = -8
        reason = "Advisory: This field requires significant people interaction"
    else:
        adjustment = 0
        reason = "Moderate alignment with your interaction preference"
    
    final_confidence = max(30, min(99, base_confidence + adjustment))
    return int(final_confidence), reason

def rank_majors_by_interaction(majors: List[str], category: str, interaction_score: int) -> List[str]:
    """
    Re-rank major recommendations based on interaction preference.
    Moves more compatible majors to the top.
    """
    # Define interaction levels for each major
    major_interaction_levels = {
        # Technology
        "Applied Computer Technology": 2,
        "Artificial Intelligence (AI) & Robotics": 1,
        "Software Engineering": 2,
        "Cybersecurity": 1,
        "Data Science & Analytics": 1,
        "Information Technology": 2,
        
        # Health Sciences
        "Nursing": 5,
        "Public Health": 4,
        "Pharmaceutical Sciences": 2,
        "Biomedical Sciences": 1,
        "Health Management": 4,
        "Clinical Medicine": 5,
        
        # Business
        "International Business Administration": 5,
        "Accounting": 2,
        "Finance": 2,
        "Entrepreneurship": 4,
        "Marketing Management": 5,
        "Supply Chain Management": 3,
        
        # Humanities & Social Sciences
        "International Relations": 5,
        "Political Science": 4,
        "History & Archaeology": 2,
        "Psychology": 4,
        "Sociology": 4,
        "Development Studies": 5,
        
        # Creative Arts & Media
        "Communication & Media Studies": 5,
        "Graphic Design & Multimedia": 2,
        "Film & Digital Production": 3,
        "Journalism & Broadcasting": 4,
        "Creative Writing": 1,
        "Visual Arts": 1,
    }
    
    if interaction_score == 0:
        return majors  # No change if no preference
    
    # Score each major based on interaction alignment
    scored_majors = []
    for major in majors:
        major_interaction = major_interaction_levels.get(major, 3)
        
        if interaction_score > 0:
            # Student likes interaction - score based on interaction level
            score = major_interaction
        else:
            # Student prefers solo work - inverse score
            score = 6 - major_interaction
        
        scored_majors.append((major, score))
    
    # Sort by score (descending)
    scored_majors.sort(key=lambda x: x[1], reverse=True)
    ranked_majors = [major for major, score in scored_majors]
    
    return ranked_majors

def semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts using word overlap.
    Returns score 0-1.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    # Jaccard similarity
    return len(intersection) / len(union)

def analyze_interest_with_gpt(interest_text: str) -> Tuple[str, float, List[str]]:
    """
    Use GPT-4 to intelligently analyze student interests.
    Falls back to keyword analysis if API not available.
    
    Returns: (interest_category, confidence, reasoning)
    """
    if not HAS_OPENAI:
        return None, 0, []
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None, 0, []
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Analyze this student interest statement and determine their best academic path at USIU-Africa.

Interest Statement: "{interest_text}"

Available Paths:
1. Technology & Engineering - Tech, AI, Software, Data Science, Cybersecurity
2. Health Sciences - Medicine, Nursing, Health Management, Pharmacy
3. Business & Commerce - Business Admin, Accounting, Finance, Entrepreneurship
4. Humanities & Social Sciences - Politics, International Relations, Psychology, History
5. Creative Arts & Media - Film, Journalism, Design, Communication, Writing

Respond in JSON format:
{{
    "category": "one of the 5 paths above",
    "confidence": 0-100,
    "reasoning": "brief explanation",
    "key_interests": ["detected", "interest", "phrases"]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        result = json.loads(response.choices[0].message.content)
        return (
            result.get("category", ""),
            result.get("confidence", 0),
            result.get("key_interests", [])
        )
    
    except Exception as e:
        print(f"⚠️  GPT Analysis failed: {e}")
        return None, 0, []

def analyze_interest_text_advanced(interest_text: str, grades_dict: Dict = None) -> Tuple[str, float, List[str], str]:
    """
    Advanced interest analysis using multiple techniques.
    
    Args:
        interest_text: Student's interest description
        grades_dict: Optional grades dict for context
    
    Returns:
        (interest_category, confidence_score, key_interests, reasoning)
    """
    if not interest_text or len(interest_text.strip()) < 2:
        return "Undecided", 0, ["unclear"], "No interest provided"
    
    text = interest_text.lower().strip()
    
    # Detect interaction preference from the text
    interaction_score, interaction_pref = detect_interaction_preference(text)
    
    # Try GPT first if available
    gpt_category, gpt_confidence, gpt_keywords = analyze_interest_with_gpt(interest_text)
    if gpt_category and gpt_confidence > 60:
        reasoning = f"Advanced AI analysis (GPT-4) - {interaction_pref}"
        # Adjust for interaction preference
        final_confidence, interaction_reason = adjust_confidence_for_interaction(
            gpt_confidence, interaction_score, gpt_category
        )
        return gpt_category, final_confidence, gpt_keywords, reasoning + f" | {interaction_reason}"
    
    # Fall back to enhanced semantic analysis with interaction awareness
    return analyze_interest_text_semantic(text, grades_dict, interaction_score, interaction_pref)

def generate_analytical_reasoning(interest_name: str, keywords_found: List[str], grades_dict: Dict = None, interaction_pref: str = "", confidence: float = 0) -> str:
    """
    Generate detailed, conversational reasoning that shows analysis of interests and grades.
    
    Returns:
        Detailed explanation of the recommendation
    """
    reasoning_parts = []
    
    # 1. Interest Analysis
    if keywords_found:
        keyword_str = ", ".join(keywords_found[:5])
        reasoning_parts.append(f"📌 **Your Interests:** You mentioned key interests in {keyword_str}")
    else:
        reasoning_parts.append(f"📌 **Your Interests:** Your interests point toward {interest_name}")
    
    # 2. Grade Analysis for the Category
    if grades_dict:
        relevant_grades = []
        grade_strengths = []
        grade_challenges = []
        
        if interest_name == "Technology & Engineering":
            relevant_subjects = {'math': 'Mathematics', 'physics': 'Physics', 'chemistry': 'Chemistry'}
        elif interest_name == "Health Sciences":
            relevant_subjects = {'biology': 'Biology', 'chemistry': 'Chemistry', 'physics': 'Physics'}
        elif interest_name == "Business & Commerce":
            relevant_subjects = {'math': 'Mathematics', 'english': 'English', 'physics': 'Tech/Business'}
        elif interest_name in ["Humanities & Social Sciences", "Creative Arts & Media"]:
            relevant_subjects = {'english': 'English', 'humanities': 'Humanities', 'kiswahili': 'Kiswahili'}
        else:
            relevant_subjects = {}
        
        # Analyze relevant grades
        grade_map = {12: 'A', 11: 'A-', 10: 'B+', 9: 'B', 8: 'B-', 7: 'C+', 6: 'C', 5: 'C-', 4: 'D+', 3: 'D', 2: 'D-', 1: 'E'}
        
        for key, display_name in relevant_subjects.items():
            grade_val = grades_dict.get(key, 0)
            if grade_val > 0:
                grade_letter = grade_map.get(grade_val, f"Score {grade_val}")
                relevant_grades.append(f"{display_name}: {grade_letter}")
                
                if grade_val >= 10:
                    grade_strengths.append(display_name)
                elif grade_val < 6:
                    grade_challenges.append(display_name)
        
        if relevant_grades:
            grade_analysis = f"📊 **Your Academic Strengths:** {', '.join(relevant_grades)}"
            reasoning_parts.append(grade_analysis)
        
        # 3. Alignment Analysis
        if grade_strengths:
            alignment = f"✅ **Strong Alignment:** Your excellent grades in {', '.join(grade_strengths)} are perfect for {interest_name}"
            reasoning_parts.append(alignment)
        elif grade_challenges:
            alignment = f"⚠️ **Academic Consideration:** You may want to strengthen {', '.join(grade_challenges)} to maximize your success in this field"
            reasoning_parts.append(alignment)
        else:
            alignment = f"✅ **Alignment:** Your academic profile supports your interest in {interest_name}"
            reasoning_parts.append(alignment)
    
    # 4. Interaction Preference (if mentioned)
    if interaction_pref and interaction_pref != "Flexible/no clear preference":
        if "Very people-oriented" in interaction_pref:
            reasoning_parts.append(f"👥 **Work Style:** You're clearly people-focused - this recommendation considers roles with high collaboration")
        elif "Prefers independent" in interaction_pref:
            reasoning_parts.append(f"🎯 **Work Style:** You prefer focused, independent work - recommended majors emphasize analytical roles")
        elif "Enjoys some" in interaction_pref:
            reasoning_parts.append(f"⚡ **Work Style:** You enjoy a mix of independent and team work - good balance in this field")
    
    # 5. Final Confidence Statement
    if confidence >= 85:
        conf_msg = f"🎯 **Confidence:** Very strong match ({confidence}%) - your interests align perfectly with both your grades and work style"
    elif confidence >= 70:
        conf_msg = f"💪 **Confidence:** Good match ({confidence}%) - strong alignment of interests and academic strengths"
    elif confidence >= 50:
        conf_msg = f"👍 **Confidence:** Moderate match ({confidence}%) - this direction fits your expressed interests"
    else:
        conf_msg = f"🤔 **Confidence:** {confidence}% - consider this as one option to explore"
    
    reasoning_parts.append(conf_msg)
    
    return " | ".join(reasoning_parts)

def analyze_interest_text_semantic(text: str, grades_dict: Dict = None, interaction_score: int = 0, interaction_pref: str = "") -> Tuple[str, float, List[str], str]:
    """
    Enhanced semantic analysis using word similarity and context, with interaction awareness.
    """
    
    # Keywords for each interest
    interest_keywords = {
        "Technology & Engineering": {
            "strong": ['technology', 'tech', 'programming', 'coding', 'software', 'ai', 'artificial intelligence', 
                      'robotics', 'data science', 'cybersecurity', 'algorithm', 'machine learning', 'innovation'],
            "moderate": ['computer', 'engineering', 'it', 'app', 'web', 'analysis', 'automation', 'digital'],
            "weak": ['smart', 'electronic', 'online'],
        },
        "Health Sciences": {
            "strong": ['doctor', 'nurse', 'medicine', 'pharmacy', 'healthcare', 'medical', 'surgery', 'patient care',
                      'healing', 'health', 'hospital', 'treatment', 'disease'],
            "moderate": ['health', 'biology', 'chemistry', 'anatomy', 'wellness', 'therapy', 'care'],
            "weak": ['help people', 'helping', 'science'],
        },
        "Business & Commerce": {
            "strong": ['business', 'entrepreneur', 'consulting', 'finance', 'accounting', 'marketing', 'management',
                      'economics', 'investment', 'leadership', 'strategy'],
            "moderate": ['corporate', 'sales', 'startup', 'commerce', 'banking', 'trading'],
            "weak": ['success', 'money', 'profit', 'career'],
        },
        "Humanities & Social Sciences": {
            "strong": ['politics', 'international relations', 'history', 'psychology', 'sociology', 'law', 'policy',
                      'diplomacy', 'government', 'social', 'politics', 'justice', 'cultural'],
            "moderate": ['society', 'people', 'community', 'understanding', 'research', 'education', 'development'],
            "weak": ['helping', 'change', 'impact'],
        },
        "Creative Arts & Media": {
            "strong": ['design', 'film', 'media', 'journalism', 'photography', 'animation', 'writing', 'graphic',
                      'music', 'acting', 'art', 'creative', 'storytelling', 'broadcast'],
            "moderate": ['communication', 'content', 'production', 'visual', 'entertainment', 'advertising'],
            "weak": ['creative', 'expression', 'performance'],
        }
    }
    
    # Check for undecided
    undecided_keywords = {'not sure', 'undecided', 'unclear', 'confused', 'don\'t know', 'unsure', 'no idea', 'confused', '?'}
    if any(kw in text for kw in undecided_keywords):
        return "Undecided", 20, ["undecided"], "Student indication of uncertainty"
    
    # Score each interest
    scores = {}
    detected_keywords = {}
    
    for interest, keywords_dict in interest_keywords.items():
        score = 0
        found_keywords = []
        
        # Strong keywords (weight: 3)
        for kw in keywords_dict["strong"]:
            if kw in text:
                score += 3
                found_keywords.append(kw)
        
        # Moderate keywords (weight: 2)
        for kw in keywords_dict["moderate"]:
            if kw in text:
                score += 2
                found_keywords.append(kw)
        
        # Weak keywords (weight: 1)
        for kw in keywords_dict["weak"]:
            if kw in text:
                score += 1
                found_keywords.append(kw)
        
        if found_keywords:
            scores[interest] = score
            detected_keywords[interest] = found_keywords[:5]  # Top 5 keywords
    
    # Get best match
    if not scores:
        return "Undecided", 30, ["unclear_input"], "Could not determine interest from input"
    
    best_interest = max(scores.items(), key=lambda x: x[1])
    interest_name = best_interest[0]
    score = best_interest[1]
    keywords_found = detected_keywords.get(interest_name, [])
    
    # Calculate confidence (0-100)
    max_possible_score = 15  # 5 strong keywords
    confidence = min(95, int((score / max_possible_score) * 100))
    confidence = max(50, confidence)  # Minimum 50% confidence
    
    # Adjust confidence based on grades if provided
    if grades_dict and interest_name == "Technology & Engineering":
        tech_scores = [grades_dict.get('physics', 0), grades_dict.get('math', 0), grades_dict.get('chemistry', 0)]
        if any(s >= 10 for s in tech_scores):
            confidence = min(99, confidence + 10)
    
    # Adjust confidence based on interaction preference  
    if interaction_score != 0:
        adjusted_confidence, _ = adjust_confidence_for_interaction(
            confidence, interaction_score, interest_name
        )
        confidence = adjusted_confidence
    
    # Generate detailed, analytical reasoning
    reasoning = generate_analytical_reasoning(
        interest_name, 
        keywords_found, 
        grades_dict, 
        interaction_pref, 
        confidence
    )
    
    return interest_name, confidence, keywords_found, reasoning

def get_major_recommendation(interest_category: str, confidence: float, grades_dict: Dict = None, interaction_score: int = 0) -> Dict:
    """
    Get major recommendation based on interest category, grades, and interaction preference.
    
    Returns:
        dict with major, school, and adjusted confidence
    """
    if interest_category not in INTEREST_MAJOR_MAP:
        return {
            "major": "General Studies",
            "school": "School of Humanities and Social Sciences",
            "confidence": 50,
            "reason": f"Unknown interest category: {interest_category}"
        }
    
    interest_data = INTEREST_MAJOR_MAP[interest_category]
    
    # Rank majors based on interaction preference
    ranked_majors = rank_majors_by_interaction(
        interest_data["majors"], 
        interest_category, 
        interaction_score
    )
    major = ranked_majors[0]  # Best recommendation based on interaction + category
    
    # Adjust confidence based on grades if provided
    adjusted_confidence = interest_data["base_confidence"]
    
    if grades_dict:
        # Check subject relevance
        relevant_scores = []
        if interest_category == "Technology & Engineering":
            relevant_scores = [grades_dict.get('Physics', 0), grades_dict.get('Mathematics', 0)]
        elif interest_category == "Health Sciences":
            relevant_scores = [grades_dict.get('Biology', 0), grades_dict.get('Chemistry', 0)]
        elif interest_category == "Business & Commerce":
            relevant_scores = [grades_dict.get('Mathematics', 0), grades_dict.get('Economics', 0)]
        
        if relevant_scores:
            avg_score = sum(relevant_scores) / len(relevant_scores)
            if avg_score >= 10:
                adjusted_confidence = min(99, adjusted_confidence + 10)
            elif avg_score < 5:
                adjusted_confidence = max(50, adjusted_confidence - 10)
    
    # Factor in interest analysis confidence
    final_confidence = int((adjusted_confidence + confidence) / 2)
    
    return {
        "major": major,
        "school": interest_data["school"],
        "confidence": final_confidence,
        "all_options": ranked_majors,  # Now ranked by interaction preference
        "reason": f"Based on {interest_category} interest with personalized ranking"
    }

# ==================== LEGACY COMPATIBILITY ====================

def analyze_interest_text(interest_text):
    """
    Legacy function for backward compatibility.
    Maps to new advanced analyzer.
    """
    category, confidence, keywords, reasoning = analyze_interest_text_advanced(interest_text)
    
    # Map category names to codes for legacy system
    category_codes = {
        "Technology & Engineering": 0,
        "Health Sciences": 1,
        "Business & Commerce": 2,
        "Humanities & Social Sciences": 3,
        "Creative Arts & Media": 4,
        "Undecided": -1
    }
    
    code = category_codes.get(category, -1)
    return code, keywords

if __name__ == "__main__":
    # Test the analyzer
    test_interests = [
        "I love coding and building AI applications",
        "I want to help people through medicine and healthcare",
        "I'm passionate about starting my own business",
        "I'm interested in international politics and diplomacy",
        "I enjoy creating videos and telling stories through film"
    ]
    
    print("🧠 AI Interest Analyzer Test\n" + "="*50)
    
    for interest in test_interests:
        category, confidence, keywords, reasoning = analyze_interest_text_advanced(interest)
        print(f"\n📝 Interest: {interest}")
        print(f"📊 Category: {category}")
        print(f"💡 Confidence: {confidence}%")
        print(f"🔑 Keywords: {', '.join(keywords)}")
        print(f"📌 Reasoning: {reasoning}")
