"""
Educational Systems and Universities Registry
Supports multi-country curricula (KCSE, Rwanda NESB, Uganda UACE, WASSCE, Cambridge A-Levels)
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
        "name": "KCSE (Kenya Certificate of Secondary Education)",
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
        "subjects": {
            "compulsory": [
                {"id": "math", "name": "Mathematics", "code": "121/122", "desc": "Compulsory quantitative requirement"},
                {"id": "english", "name": "English", "code": "101", "desc": "Language proficiency"},
                {"id": "kiswahili", "name": "Kiswahili", "code": "102", "desc": "Compulsory language"},
                {"id": "humanities", "name": "Best Humanity (History/Geo/CRE)", "code": "Group III", "desc": "Highest Group III grade"}
            ],
            "electives": [
                {"id": "biology", "name": "Biology", "code": "231", "desc": "Health & Life Sciences prerequisite"},
                {"id": "physics", "name": "Physics", "code": "232", "desc": "Engineering & Technology"},
                {"id": "chemistry", "name": "Chemistry", "code": "233", "desc": "Pharmacy & Pure Sciences"},
                {"id": "tech_bus", "name": "Best Technical/Business", "code": "Group IV/V", "desc": "Business Studies, Computer Studies, etc."}
            ]
        }
    },
    "rw_nesb": {
        "id": "rw_nesb",
        "country": "Rwanda",
        "name": "Rwanda Advanced Level (NESB / REB)",
        "grade_scale": [
            ("A", "A (Principal Pass - 6 points)", 12),
            ("B", "B (Principal Pass - 5 points)", 10),
            ("C", "C (Principal Pass - 4 points)", 8),
            ("D", "D (Principal Pass - 3 points)", 6),
            ("E", "E (Principal Pass - 2 points)", 4),
            ("S", "S (Subsidiary Pass - 1 point)", 2),
            ("F", "F (Fail - 0 points)", 0)
        ],
        "subjects": {
            "compulsory": [
                {"id": "math", "name": "Mathematics / Core Quantitative", "code": "MATH", "desc": "Advanced Mathematics or Core Math"},
                {"id": "english", "name": "English Language & Communication", "code": "ENG", "desc": "Instructional language requirement"},
                {"id": "kiswahili", "name": "French / Kinyarwanda / General Paper", "code": "LANG/GP", "desc": "Language / General Paper score"},
                {"id": "humanities", "name": "Economics / History / Geography", "code": "HUM", "desc": "Best Humanities / Social Science discipline"}
            ],
            "electives": [
                {"id": "biology", "name": "Biology", "code": "BIO", "desc": "Key for MCB / PCB science combinations"},
                {"id": "physics", "name": "Physics", "code": "PHY", "desc": "Key for MPC / PCM combinations"},
                {"id": "chemistry", "name": "Chemistry", "code": "CHM", "desc": "Key for Medical & Chemistry combinations"},
                {"id": "tech_bus", "name": "Computer Science / Entrepreneurship", "code": "ICT/ENT", "desc": "Applied science or business subject"}
            ]
        }
    },
    "ug_uace": {
        "id": "ug_uace",
        "country": "Uganda",
        "name": "Uganda UACE (UNEB Advanced Certificate)",
        "grade_scale": [
            ("A", "A (Principal - 6 points)", 12),
            ("B", "B (Principal - 5 points)", 10),
            ("C", "C (Principal - 4 points)", 8),
            ("D", "D (Principal - 3 points)", 6),
            ("E", "E (Principal - 2 points)", 4),
            ("O", "O (Subsidiary Pass - 1 point)", 2),
            ("F", "F (Fail - 0 points)", 0)
        ],
        "subjects": {
            "compulsory": [
                {"id": "math", "name": "Principal Mathematics / Sub-Math", "code": "P-MATH", "desc": "Principal Math or Subsidiary Mathematics"},
                {"id": "english", "name": "General Paper (GP) / English", "code": "GP", "desc": "General Paper university requirement"},
                {"id": "kiswahili", "name": "Literature / Second Subject", "code": "SUB2", "desc": "Secondary subject assessment"},
                {"id": "humanities", "name": "Economics / History / Divinity / Geography", "code": "ARTS", "desc": "Best Arts/Humanities Principal Subject"}
            ],
            "electives": [
                {"id": "biology", "name": "Biology (Principal)", "code": "P-BIO", "desc": "Health Sciences prerequisite (e.g. BCM/PCB)"},
                {"id": "physics", "name": "Physics (Principal)", "code": "P-PHY", "desc": "Engineering & Technology (PCM)"},
                {"id": "chemistry", "name": "Chemistry (Principal)", "code": "P-CHM", "desc": "Pure Sciences & Pharmacy"},
                {"id": "tech_bus", "name": "Sub-ICT / Entrepreneurship", "code": "ICT", "desc": "Subsidiary ICT or Business Subject"}
            ]
        }
    },
    "wa_wassce": {
        "id": "wa_wassce",
        "country": "Nigeria / Ghana / West Africa",
        "name": "WASSCE (West African Senior School Certificate)",
        "grade_scale": [
            ("A1", "A1 (Excellent - 80-100%)", 12),
            ("B2", "B2 (Very Good - 70-79%)", 11),
            ("B3", "B3 (Good - 65-69%)", 10),
            ("C4", "C4 (Credit - 60-64%)", 8),
            ("C5", "C5 (Credit - 55-59%)", 7),
            ("C6", "C6 (Credit - 50-54%)", 6),
            ("D7", "D7 (Pass - 45-49%)", 4),
            ("E8", "E8 (Pass - 40-44%)", 2),
            ("F9", "F9 (Fail - 0-39%)", 0)
        ],
        "subjects": {
            "compulsory": [
                {"id": "math", "name": "General / Core Mathematics", "code": "WAEC-M", "desc": "Compulsory Core Mathematics (Credit required)"},
                {"id": "english", "name": "English Language", "code": "WAEC-E", "desc": "Compulsory English Language (Credit required)"},
                {"id": "kiswahili", "name": "Civic Education / Integrated Science", "code": "WAEC-CIV", "desc": "Core curriculum subject"},
                {"id": "humanities", "name": "Government / Literature / CRK / Economics", "code": "WAEC-HUM", "desc": "Best Humanities/Social Science Elective"}
            ],
            "electives": [
                {"id": "biology", "name": "Biology (Elective)", "code": "WAEC-BIO", "desc": "Medical/Biological Sciences prerequisite"},
                {"id": "physics", "name": "Physics (Elective)", "code": "WAEC-PHY", "desc": "Engineering & Physical Sciences"},
                {"id": "chemistry", "name": "Chemistry (Elective)", "code": "WAEC-CHM", "desc": "Pharmacy & Chemical Sciences"},
                {"id": "tech_bus", "name": "Financial Accounting / Commerce / Further Math", "code": "WAEC-BUS", "desc": "Applied science, commerce or advanced math"}
            ]
        }
    },
    "intl_cambridge": {
        "id": "intl_cambridge",
        "country": "International / British Curriculum",
        "name": "Cambridge International A-Levels / GCE",
        "grade_scale": [
            ("A*", "A* (Outstanding)", 12),
            ("A", "A (Excellent)", 11),
            ("B", "B (Good)", 9),
            ("C", "C (Pass / Satisfactory)", 7),
            ("D", "D (Low Pass)", 5),
            ("E", "E (Minimum Pass)", 3),
            ("U", "U (Ungraded / Fail)", 0)
        ],
        "subjects": {
            "compulsory": [
                {"id": "math", "name": "A-Level Mathematics / Pure Math", "code": "AL-MATH", "desc": "Mathematics or Further Mathematics"},
                {"id": "english", "name": "English Language / English General Paper", "code": "AL-ENG", "desc": "Language proficiency qualification"},
                {"id": "kiswahili", "name": "Second Language / Literature in English", "code": "AL-LANG", "desc": "Language or Literature A-Level / AS-Level"},
                {"id": "humanities", "name": "Economics / History / Geography / Psychology", "code": "AL-HUM", "desc": "Best Humanities / Social Science subject"}
            ],
            "electives": [
                {"id": "biology", "name": "A-Level Biology", "code": "AL-BIO", "desc": "Life sciences prerequisite"},
                {"id": "physics", "name": "A-Level Physics", "code": "AL-PHY", "desc": "Physical sciences & Engineering"},
                {"id": "chemistry", "name": "A-Level Chemistry", "code": "AL-CHM", "desc": "Pharmaceutical & Chemical sciences"},
                {"id": "tech_bus", "name": "A-Level Computer Science / Business", "code": "AL-CS", "desc": "Computing or Business Studies"}
            ]
        }
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

    # Fallback: check if grade string contains the code or common KCSE format
    fallback_map = {
        'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
        'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3,
        'D-': 2, 'E': 1, 'A1': 12, 'B2': 11, 'B3': 10,
        'C4': 8, 'C5': 7, 'C6': 6, 'D7': 4, 'E8': 2, 'F9': 0,
        'A*': 12, 'S': 2, 'O': 2, 'U': 0, 'F': 0
    }
    return fallback_map.get(val, 0)


def get_country_options() -> List[Dict[str, str]]:
    """Returns list of supported countries for UI dropdowns."""
    return [
        {"id": "Kenya", "name": "Kenya", "default_curriculum": "ke_kcse", "default_uni": "usiu"},
        {"id": "Rwanda", "name": "Rwanda", "default_curriculum": "rw_nesb", "default_uni": "alu"},
        {"id": "Uganda", "name": "Uganda", "default_curriculum": "ug_uace", "default_uni": "makerere"},
        {"id": "West Africa", "name": "Nigeria / Ghana / West Africa", "default_curriculum": "wa_wassce", "default_uni": "ashesi"},
        {"id": "International", "name": "International (British / Cambridge / Other)", "default_curriculum": "intl_cambridge", "default_uni": "usiu"},
    ]


def get_curricula_for_country(country_id: str) -> List[Dict[str, Any]]:
    """Get matching curricula for a country."""
    if country_id == "Kenya":
        return [CURRICULA["ke_kcse"], CURRICULA["intl_cambridge"]]
    elif country_id == "Rwanda":
        return [CURRICULA["rw_nesb"], CURRICULA["intl_cambridge"]]
    elif country_id == "Uganda":
        return [CURRICULA["ug_uace"], CURRICULA["intl_cambridge"]]
    elif country_id == "West Africa":
        return [CURRICULA["wa_wassce"], CURRICULA["intl_cambridge"]]
    else:
        return list(CURRICULA.values())


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
