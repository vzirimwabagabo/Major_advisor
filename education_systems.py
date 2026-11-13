"""
Educational Systems and Universities Registry
Supports authentic, multi-country curricula:
  - Kenya: KCSE (8-4-4)
  - Rwanda: NESB / REB Advanced Level (Combinations-based)
  - Uganda: UACE UNEB Advanced Level (Combinations-based)
  - West Africa: WASSCE (WAEC Core + Science/Commerce/Arts Streams)
  - International: Cambridge International A-Levels / GCE
and partner universities across Africa.
"""

from typing import Dict, List, Tuple, Any

# ==================== UNIVERSITIES DIRECTORY ====================
UNIVERSITIES: Dict[str, Dict[str, Any]] = {
    "usiu": {
        "id": "usiu",
        "name": "United States International University - Africa (USIU-Africa)",
        "country": "Kenya",
        "city": "Nairobi",
        "catalog": {
            "School of Science and Technology": [
                "Applied Computer Technology",
                "Information Systems & Technology",
                "Artificial Intelligence (AI) & Robotics",
                "Data Science and Analytics",
                "Software Engineering"
            ],
            "Chandaria School of Business": [
                "Global Leadership and Governance",
                "Accounting",
                "Finance",
                "Hotel and Restaurant Management",
                "International Business Administration"
            ],
            "School of Pharmacy and Health Sciences": [
                "Pharmacy",
                "Nursing"
            ],
            "School of Humanities and Social Sciences": [
                "International Relations",
                "Criminal Justice Studies",
                "Psychology"
            ],
            "School of Communication, Cinematic and Creative Arts": [
                "Animation",
                "Film Production and Directing",
                "Journalism"
            ]
        }
    },
    "strathmore": {
        "id": "strathmore",
        "name": "Strathmore University",
        "country": "Kenya",
        "city": "Nairobi",
        "catalog": {
            "School of Computing and Engineering Sciences": [
                "BSc Informatics and Computer Science",
                "BSc Software Engineering",
                "BSc Electrical and Electronics Engineering"
            ],
            "Strathmore Business School": [
                "Bachelor of Commerce (Finance / Accounting)",
                "Bachelor of Financial Services",
                "BSc Supply Chain and Operations Management"
            ],
            "School of Humanities & Social Sciences": [
                "Bachelor of Arts in International Studies",
                "Bachelor of Arts in Communication Studies"
            ],
            "Strathmore Law School": [
                "Bachelor of Laws (LL.B)"
            ]
        }
    },
    "alu": {
        "id": "alu",
        "name": "African Leadership University (ALU)",
        "country": "Rwanda",
        "city": "Kigali",
        "catalog": {
            "School of Science & Engineering": [
                "BSc (Hons) Software Engineering",
                "BSc (Hons) Computer Science"
            ],
            "School of Business & Social Sciences": [
                "BA (Hons) Entrepreneurial Leadership",
                "BA (Hons) International Business and Trade",
                "BA (Hons) Global Challenges"
            ]
        }
    },
    "makerere": {
        "id": "makerere",
        "name": "Makerere University",
        "country": "Uganda",
        "city": "Kampala",
        "catalog": {
            "College of Computing and Information Sciences": [
                "BSc Computer Science",
                "BSc Software Engineering",
                "BSc Information Systems & Technology"
            ],
            "College of Health Sciences": [
                "Bachelor of Pharmacy",
                "BSc Nursing",
                "Bachelor of Medicine and Bachelor of Surgery (MBChB)"
            ],
            "College of Business and Management Sciences": [
                "Bachelor of Commerce",
                "Bachelor of Business Administration"
            ]
        }
    },
    "ashesi": {
        "id": "ashesi",
        "name": "Ashesi University",
        "country": "Ghana",
        "city": "Berekuso",
        "catalog": {
            "Computer Science & Information Systems": [
                "BSc Computer Science",
                "BSc Management Information Systems"
            ],
            "Engineering": [
                "BSc Computer Engineering",
                "BSc Electrical and Electronic Engineering",
                "BSc Mechanical Engineering"
            ],
            "Business Administration": [
                "BSc Business Administration"
            ]
        }
    },
    "all": {
        "id": "all",
        "name": "Pan-African Multi-University Match (Compare Across All Campuses)",
        "country": "Pan-Africa",
        "city": "All Campuses",
        "catalog": {}
    }
}


# ==================== HIGH SCHOOL CURRICULA ====================
CURRICULA: Dict[str, Dict[str, Any]] = {
    "ke_kcse": {
        "id": "ke_kcse",
        "country": "Kenya",
        "name": "Kenya — KCSE (8-4-4 / KICD)",
        "system_desc": "Standard Kenyan Certificate of Secondary Education. Compulsory subjects + Sciences + Humanities + Electives.",
        "grade_scale": [
            ("A", "A (12 points)", 12),
            ("A-", "A- (11 points)", 11),
            ("B+", "B+ (10 points)", 10),
            ("B", "B (9 points)", 9),
            ("B-", "B- (8 points)", 8),
            ("C+", "C+ (7 points)", 7),
            ("C", "C (6 points)", 6),
            ("C-", "C- (5 points)", 5),
            ("D+", "D+ (4 points)", 4),
            ("D", "D (3 points)", 3),
            ("D-", "D- (2 points)", 2),
            ("E", "E (1 point)", 1)
        ],
        "sections": [
            {
                "title": "Group I: Compulsory National Subjects",
                "subtitle": "Mandatory for all KCSE candidates",
                "subjects": [
                    {"id": "math", "name": "Mathematics (121/122)", "required": True, "category": "math", "desc": "Compulsory quantitative foundation"},
                    {"id": "english", "name": "English Language & Lit (101)", "required": True, "category": "english", "desc": "Language proficiency requirement"},
                    {"id": "kiswahili", "name": "Kiswahili (102)", "required": True, "category": "language", "desc": "National compulsory language"}
                ]
            },
            {
                "title": "Group II: Pure & Applied Sciences",
                "subtitle": "Sciences taken (select 'Not Taken' if not studied)",
                "subjects": [
                    {"id": "biology", "name": "Biology (231)", "required": False, "category": "science", "desc": "Prerequisite for Health, Medical & Life Sciences"},
                    {"id": "physics", "name": "Physics (232)", "required": False, "category": "science", "desc": "Prerequisite for Engineering, Technology & Physical Sciences"},
                    {"id": "chemistry", "name": "Chemistry (233)", "required": False, "category": "science", "desc": "Prerequisite for Pharmacy, Medicine & Chemical Sciences"}
                ]
            },
            {
                "title": "Group III: Humanities & Social Sciences",
                "subtitle": "Best performance in Group III",
                "subjects": [
                    {"id": "humanities", "name": "Best Humanity (History / Geo / CRE / IRE)", "required": True, "category": "humanities", "desc": "Highest score in Group III Humanities"}
                ]
            },
            {
                "title": "Group IV & V: Applied & Technical Electives",
                "subtitle": "Business, Computing, or Technical subject",
                "subjects": [
                    {"id": "tech_bus", "name": "Best Technical / Business / Group IV/V", "required": False, "category": "tech_business", "desc": "Business Studies, Computer Studies, Agriculture, French, etc."}
                ]
            }
        ]
    },

    "rw_nesb": {
        "id": "rw_nesb",
        "country": "Rwanda",
        "name": "Rwanda — Advanced Level (NESB / REB)",
        "system_desc": "Rwanda Upper Secondary (S4-S6) combinations system. Consists of 3 Principal combination disciplines, General Paper, and Language.",
        "grade_scale": [
            ("A", "A (Principal Pass — 6 pts)", 12),
            ("B", "B (Principal Pass — 5 pts)", 10),
            ("C", "C (Principal Pass — 4 pts)", 8),
            ("D", "D (Principal Pass — 3 pts)", 6),
            ("E", "E (Principal Pass — 2 pts)", 4),
            ("S", "S (Subsidiary Pass — 1 pt)", 2),
            ("F", "F (Fail — 0 pts)", 0)
        ],
        "sections": [
            {
                "title": "Combination Principal Subjects (e.g. MCB, MPC, MEG, MCE, PCB, HEG, HEL)",
                "subtitle": "Select your 3 Principal combination subjects and grades",
                "subjects": [
                    {
                        "id": "rw_sub1",
                        "name": "1st Principal Subject",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Mathematics", "Physics", "Chemistry", "Biology", "Economics", "History", "Literature in English", "Computer Science"],
                        "default_subject": "Mathematics",
                        "desc": "First combination discipline (e.g. Mathematics or Physics)"
                    },
                    {
                        "id": "rw_sub2",
                        "name": "2nd Principal Subject",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Chemistry", "Physics", "Economics", "Biology", "Computer Science", "Geography", "Literature in English"],
                        "default_subject": "Chemistry",
                        "desc": "Second combination discipline (e.g. Chemistry or Economics)"
                    },
                    {
                        "id": "rw_sub3",
                        "name": "3rd Principal Subject",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Biology", "Geography", "Computer Science", "Physics", "Chemistry", "Entrepreneurship", "History"],
                        "default_subject": "Biology",
                        "desc": "Third combination discipline (e.g. Biology or Geography)"
                    }
                ]
            },
            {
                "title": "National Core & Subsidiary Papers",
                "subtitle": "Compulsory interdisciplinary and language exams",
                "subjects": [
                    {"id": "rw_gp", "name": "General Paper (GP)", "required": True, "category": "humanities", "desc": "Compulsory interdisciplinary reasoning examination"},
                    {"id": "rw_eng", "name": "English Language & Communication", "required": True, "category": "english", "desc": "Instructional language requirement"},
                    {"id": "rw_sub", "name": "Subsidiary Subject (Sub-Math / ICT / French / Kinyarwanda)", "required": False, "category": "language", "desc": "Subsidiary examination subject"}
                ]
            }
        ]
    },

    "ug_uace": {
        "id": "ug_uace",
        "country": "Uganda",
        "name": "Uganda — UACE (UNEB Advanced Certificate)",
        "system_desc": "Uganda Advanced Certificate of Education. 3 Principal subjects + General Paper + Subsidiary Mathematics / ICT.",
        "grade_scale": [
            ("A", "A (Principal — 6 pts)", 12),
            ("B", "B (Principal — 5 pts)", 10),
            ("C", "C (Principal — 4 pts)", 8),
            ("D", "D (Principal — 3 pts)", 6),
            ("E", "E (Principal — 2 pts)", 4),
            ("O", "O (Subsidiary Pass — 1 pt)", 2),
            ("F", "F (Fail — 0 pts)", 0)
        ],
        "sections": [
            {
                "title": "A-Level Combination (3 Principal Subjects)",
                "subtitle": "Your combination (e.g. PCM, BCM, PEM, MEG, HEG, HEL, DEG)",
                "subjects": [
                    {
                        "id": "ug_p1",
                        "name": "Principal Subject 1",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Mathematics", "Physics", "Biology", "Chemistry", "Economics", "History", "Literature in English", "Divinity", "Geography"],
                        "default_subject": "Mathematics",
                        "desc": "First principal discipline"
                    },
                    {
                        "id": "ug_p2",
                        "name": "Principal Subject 2",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Physics", "Chemistry", "Economics", "Mathematics", "Biology", "Geography", "History", "Agriculture"],
                        "default_subject": "Physics",
                        "desc": "Second principal discipline"
                    },
                    {
                        "id": "ug_p3",
                        "name": "Principal Subject 3",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Chemistry", "Mathematics", "Geography", "Biology", "Divinity", "Economics", "Literature in English", "Entrepreneurship"],
                        "default_subject": "Chemistry",
                        "desc": "Third principal discipline"
                    }
                ]
            },
            {
                "title": "Compulsory Subsidiary Subjects",
                "subtitle": "University admission prerequisites",
                "subjects": [
                    {"id": "ug_gp", "name": "General Paper (GP)", "required": True, "category": "humanities", "desc": "Compulsory interdisciplinary reasoning paper"},
                    {"id": "ug_sub_math_ict", "name": "Subsidiary Mathematics / Sub-ICT", "required": True, "category": "math", "desc": "Compulsory subsidiary quantitative/computing exam"}
                ]
            }
        ]
    },

    "wa_wassce": {
        "id": "wa_wassce",
        "country": "Nigeria / Ghana / West Africa",
        "name": "West Africa — WASSCE (WAEC Senior Certificate)",
        "system_desc": "West African Senior School Certificate Examination. Compulsory Core + Science, Commercial, or Arts/Humanities stream electives.",
        "grade_scale": [
            ("A1", "A1 (Excellent — 80-100%)", 12),
            ("B2", "B2 (Very Good — 70-79%)", 11),
            ("B3", "B3 (Good — 65-69%)", 10),
            ("C4", "C4 (Credit — 60-64%)", 8),
            ("C5", "C5 (Credit — 55-59%)", 7),
            ("C6", "C6 (Credit — 50-54%)", 6),
            ("D7", "D7 (Pass — 45-49%)", 4),
            ("E8", "E8 (Pass — 40-44%)", 2),
            ("F9", "F9 (Fail — 0-39%)", 0)
        ],
        "sections": [
            {
                "title": "Compulsory Core Subjects",
                "subtitle": "Credit passes (A1-C6) required for university matriculation",
                "subjects": [
                    {"id": "wa_math", "name": "General / Core Mathematics", "required": True, "category": "math", "desc": "Compulsory Core Mathematics (Credit required)"},
                    {"id": "wa_eng", "name": "English Language", "required": True, "category": "english", "desc": "Compulsory English Language (Credit required)"},
                    {"id": "wa_civic", "name": "Civic Education / Integrated Science", "required": True, "category": "humanities", "desc": "Compulsory core examination"}
                ]
            },
            {
                "title": "Specialized Stream Electives (Science / Commercial / Arts)",
                "subtitle": "Select your stream subjects",
                "subjects": [
                    {
                        "id": "wa_elec1",
                        "name": "Elective 1 (Primary Stream)",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Biology", "Physics", "Chemistry", "Financial Accounting", "Literature-in-English", "Government", "Further Mathematics"],
                        "default_subject": "Biology",
                        "desc": "Primary specialized elective"
                    },
                    {
                        "id": "wa_elec2",
                        "name": "Elective 2 (Secondary Stream)",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Chemistry", "Physics", "Commerce", "Economics", "Government", "Biology", "CRS / IRS"],
                        "default_subject": "Chemistry",
                        "desc": "Secondary specialized elective"
                    },
                    {
                        "id": "wa_elec3",
                        "name": "Elective 3 (Tertiary Stream)",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Physics", "Economics", "Commerce", "Geography", "Literature-in-English", "Agricultural Science", "Computer Studies"],
                        "default_subject": "Physics",
                        "desc": "Tertiary specialized elective"
                    },
                    {
                        "id": "wa_elec4",
                        "name": "Elective 4 (Additional Stream Elective)",
                        "required": False,
                        "type": "custom_select",
                        "options": ["Further Mathematics", "Agricultural Science", "Geography", "Technical Drawing", "French", "Marketing"],
                        "default_subject": "Further Mathematics",
                        "desc": "Additional specialized elective"
                    }
                ]
            }
        ]
    },

    "intl_cambridge": {
        "id": "intl_cambridge",
        "country": "International / British Curriculum",
        "name": "International — Cambridge A-Levels / GCE",
        "system_desc": "Cambridge International / Edexcel General Certificate of Education. 3-4 Advanced Level disciplines + English proficiency.",
        "grade_scale": [
            ("A*", "A* (Outstanding)", 12),
            ("A", "A (Excellent)", 11),
            ("B", "B (Good)", 9),
            ("C", "C (Pass / Satisfactory)", 7),
            ("D", "D (Low Pass)", 5),
            ("E", "E (Minimum Pass)", 3),
            ("U", "U (Ungraded / Fail)", 0)
        ],
        "sections": [
            {
                "title": "Principal A-Level Subjects",
                "subtitle": "Your 3 or 4 Advanced Level subjects",
                "subjects": [
                    {
                        "id": "cam_a1",
                        "name": "A-Level Subject 1",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Mathematics (Pure & Applied)", "Physics", "Chemistry", "Biology", "Economics", "Computer Science", "History", "English Literature"],
                        "default_subject": "Mathematics (Pure & Applied)",
                        "desc": "First principal A-Level"
                    },
                    {
                        "id": "cam_a2",
                        "name": "A-Level Subject 2",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Further Mathematics", "Physics", "Chemistry", "Biology", "Business Studies", "Economics", "Psychology", "Computer Science", "Geography"],
                        "default_subject": "Physics",
                        "desc": "Second principal A-Level"
                    },
                    {
                        "id": "cam_a3",
                        "name": "A-Level Subject 3",
                        "required": True,
                        "type": "custom_select",
                        "options": ["Chemistry", "Biology", "Economics", "Business Studies", "Accounting", "Psychology", "Sociology", "Law", "Art & Design"],
                        "default_subject": "Chemistry",
                        "desc": "Third principal A-Level"
                    },
                    {
                        "id": "cam_a4",
                        "name": "A-Level Subject 4 / AS-Level (Optional)",
                        "required": False,
                        "type": "custom_select",
                        "options": ["Further Mathematics", "Computer Science", "Thinking Skills", "Global Perspectives & Research", "French", "Spanish"],
                        "default_subject": "Computer Science",
                        "desc": "Optional 4th subject or AS qualification"
                    }
                ]
            },
            {
                "title": "English Language & Academic Reasoning",
                "subtitle": "Language proficiency certification",
                "subjects": [
                    {"id": "cam_eng", "name": "English Language / English General Paper (AS/A-Level)", "required": True, "category": "english", "desc": "Cambridge English qualification"}
                ]
            }
        ]
    }
}


# ==================== HELPER FUNCTIONS ====================

def parse_curriculum_grade(curriculum_id: str, grade_value: str) -> int:
    """
    Parses a grade string from any curriculum and normalizes it to a 0-12 point scale.
    """
    if not grade_value:
        return 0

    val = str(grade_value).strip().upper()
    if val in ['NOT TAKEN', 'N/A', 'NONE', '', 'NOT_TAKEN', '0']:
        return 0

    curr = CURRICULA.get(curriculum_id, CURRICULA["ke_kcse"])
    scale = curr["grade_scale"]

    # Match exact code first
    for code, _, points in scale:
        if val == code.upper():
            return points

    # Fallback normalization map
    fallback_map = {
        'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
        'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3,
        'D-': 2, 'E': 1, 'A1': 12, 'B2': 11, 'B3': 10,
        'C4': 8, 'C5': 7, 'C6': 6, 'D7': 4, 'E8': 2, 'F9': 0,
        'A*': 12, 'S': 2, 'O': 2, 'U': 0, 'F': 0
    }
    return fallback_map.get(val, 0)


def extract_candidate_profile(curriculum_id: str, form_data: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, str], List[str]]:
    """
    Parses submitted form data for any curriculum into:
      1. standardized academic cluster scores (math, english, science, humanities, tech_business)
      2. input_summary dict (for user display)
      3. raw_subject_strings list (for Gemini AI prompt)
    """
    curr = CURRICULA.get(curriculum_id, CURRICULA["ke_kcse"])
    grade_lookup = {code: display for code, display, _ in curr["grade_scale"]}
    
    input_summary: Dict[str, str] = {}
    raw_subject_lines: List[str] = []
    
    math_scores: List[int] = []
    eng_scores: List[int] = []
    science_scores: List[int] = []
    humanities_scores: List[int] = []
    business_scores: List[int] = []
    specific_scores = {'biology': 0, 'physics': 0, 'chemistry': 0, 'kiswahili': 0}

    def _categorize(sub_name: str, pts: int):
        s = sub_name.lower()
        if any(w in s for w in ['math', 'calculus', 'algebra']):
            math_scores.append(pts)
        elif any(w in s for w in ['english', 'literature', 'general paper', 'french', 'kinyarwanda', 'language']):
            eng_scores.append(pts)
        if any(w in s for w in ['bio', 'chem', 'phys', 'science']):
            science_scores.append(pts)
        if any(w in s for w in ['history', 'geog', 'politic', 'civic', 'divinity', 'relig', 'cre', 'ire', 'gov', 'philosophy', 'sociology']):
            humanities_scores.append(pts)
        if any(w in s for w in ['business', 'account', 'commerce', 'econ', 'entrepreneur', 'computer', 'ict', 'tech', 'software']):
            business_scores.append(pts)
        
        # Track specific pure sciences & languages for eligibility checks
        if 'bio' in s:
            specific_scores['biology'] = max(specific_scores['biology'], pts)
        if 'phys' in s:
            specific_scores['physics'] = max(specific_scores['physics'], pts)
        if 'chem' in s:
            specific_scores['chemistry'] = max(specific_scores['chemistry'], pts)
        if 'kisw' in s or 'kiny' in s:
            specific_scores['kiswahili'] = max(specific_scores['kiswahili'], pts)

    # Process all sections defined in the curriculum
    for section in curr.get("sections", []):
        for sub in section.get("subjects", []):
            sid = sub["id"]
            
            # If subject has a selectable title (like Rwanda combination subjects or WASSCE electives)
            if sub.get("type") == "custom_select":
                chosen_subject_name = form_data.get(f"{sid}_name") or sub.get("default_subject") or sub["name"]
            else:
                chosen_subject_name = sub["name"]

            raw_grade = form_data.get(sid, "").strip()
            pts = parse_curriculum_grade(curriculum_id, raw_grade)

            if raw_grade and raw_grade.upper() not in ['NOT TAKEN', 'N/A', '', 'NONE']:
                disp_grade = grade_lookup.get(raw_grade, raw_grade)
                input_summary[chosen_subject_name] = f"{disp_grade} ({pts}pts)"
                raw_subject_lines.append(f"{chosen_subject_name}: {raw_grade} ({pts}/12 points)")
                _categorize(chosen_subject_name, pts)
            elif sub.get("required"):
                input_summary[chosen_subject_name] = "Grade not provided"
            else:
                input_summary[chosen_subject_name] = "Not Taken (0pts)"

    # Handle standard KCSE fallback if legacy field names were sent
    if not input_summary:
        legacy_keys = ['math', 'english', 'kiswahili', 'biology', 'physics', 'chemistry', 'humanities', 'tech_bus']
        for k in legacy_keys:
            raw_grade = form_data.get(k, "").strip()
            pts = parse_curriculum_grade(curriculum_id, raw_grade)
            disp_grade = grade_lookup.get(raw_grade, raw_grade) if raw_grade else "Not Taken"
            input_summary[k.capitalize()] = f"{disp_grade} ({pts}pts)" if pts > 0 else "Not Taken"
            if pts > 0:
                raw_subject_lines.append(f"{k.capitalize()}: {raw_grade} ({pts}pts)")
                _categorize(k, pts)

    def _avg(lst: List[int], default_val: int = 6) -> int:
        return int(round(sum(lst) / len(lst))) if lst else default_val

    scores = {
        'math':          _avg(math_scores, 7),
        'english':       _avg(eng_scores, 7),
        'science':       _avg(science_scores, 0),
        'humanities':    _avg(humanities_scores, 6),
        'tech_business': _avg(business_scores, 0),
        # Legacy keys for university requirement functions
        'biology':       specific_scores['biology'],
        'physics':       specific_scores['physics'],
        'chemistry':     specific_scores['chemistry'],
        'kiswahili':     specific_scores['kiswahili'] or _avg(eng_scores, 6),
    }

    return scores, input_summary, raw_subject_lines


def get_country_options() -> List[Dict[str, str]]:
    """Returns list of supported countries for UI dropdowns."""
    return [
        {"id": "Kenya", "name": "Kenya", "default_curriculum": "ke_kcse", "default_uni": "usiu"},
        {"id": "Rwanda", "name": "Rwanda", "default_curriculum": "rw_nesb", "default_uni": "alu"},
        {"id": "Uganda", "name": "Uganda", "default_curriculum": "ug_uace", "default_uni": "makerere"},
        {"id": "West Africa", "name": "Nigeria / Ghana / West Africa", "default_curriculum": "wa_wassce", "default_uni": "ashesi"},
        {"id": "International", "name": "International (British / Cambridge / Other)", "default_curriculum": "intl_cambridge", "default_uni": "usiu"},
    ]


def get_all_programs_for_uni(uni_id: str) -> List[Tuple[str, str]]:
    """Returns a list of (major_name, faculty_name) for a given university."""
    if uni_id == "all":
        results = []
        for uid, udata in UNIVERSITIES.items():
            if uid == "all":
                continue
            for fac, majors in udata.get("catalog", {}).items():
                for m in majors:
                    results.append((f"{m} ({udata['name']})", fac))
        return results

    udata = UNIVERSITIES.get(uni_id, UNIVERSITIES["usiu"])
    results = []
    for fac, majors in udata.get("catalog", {}).items():
        for m in majors:
            results.append((m, fac))
    return results
