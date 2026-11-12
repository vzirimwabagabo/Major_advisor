"""
Test suite for USIU-Africa Major Advisor
Tests algorithm correctness, eligibility validation, security rules, and catalog integrity.
"""

import sys
import unittest

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from recommendations import (
    parse_grade_input, check_eligibility, determine_best_fit,
    get_major_by_rules, PROGRAMS, MAJOR_TO_SCHOOL, VALID_GRADES
)
from ai_interest_analyzer import (
    INTEREST_MAJOR_MAP, VALID_MAJOR_NAMES,
    detect_interaction_preference, adjust_confidence_for_interaction
)
from app import validate_password, sanitize_html


class TestGradeParsing(unittest.TestCase):
    def test_grade_variations(self):
        self.assertEqual(parse_grade_input('A'), 12)
        self.assertEqual(parse_grade_input('a'), 12)
        self.assertEqual(parse_grade_input('A-'), 11)
        self.assertEqual(parse_grade_input('B+'), 10)
        self.assertEqual(parse_grade_input('C+'), 7)
        self.assertEqual(parse_grade_input('E'), 1)
        self.assertEqual(parse_grade_input(''), 0)
        self.assertEqual(parse_grade_input('not taken'), 0)
        self.assertEqual(parse_grade_input('N/A'), 0)


class TestCatalogAlignment(unittest.TestCase):
    def test_all_majors_are_real_usiu_programs(self):
        """Verify that every major in the AI map exists in the real USIU catalog."""
        flat_real_majors = {m for majors in PROGRAMS.values() for m in majors}
        self.assertEqual(len(flat_real_majors), 18)

        for cat, data in INTEREST_MAJOR_MAP.items():
            for major in data["majors"]:
                self.assertIn(
                    major, flat_real_majors,
                    f"Fictitious major detected in AI map: {major}"
                )
                self.assertIn(
                    major, VALID_MAJOR_NAMES,
                    f"Major missing from VALID_MAJOR_NAMES: {major}"
                )

    def test_reverse_school_lookup(self):
        """Verify that every major maps back to its correct school."""
        self.assertEqual(
            MAJOR_TO_SCHOOL['Software Engineering'],
            'School of Science and Technology'
        )
        self.assertEqual(
            MAJOR_TO_SCHOOL['Pharmacy'],
            'School of Pharmacy and Health Sciences'
        )
        self.assertEqual(
            MAJOR_TO_SCHOOL['International Relations'],
            'School of Humanities and Social Sciences'
        )


class TestEligibilityRules(unittest.TestCase):
    def test_compulsory_subjects(self):
        # Missing Math
        scores = {'math': 0, 'english': 10, 'biology': 8}
        eligible, msg = check_eligibility(0, scores)
        self.assertFalse(eligible)
        self.assertIn("compulsory", msg.lower())

    def test_technology_math_requirement(self):
        # Math below C+ (6 points = C)
        scores = {'math': 6, 'english': 10, 'physics': 8}
        eligible, msg = check_eligibility(0, scores)  # 0 = Tech
        self.assertFalse(eligible)
        self.assertIn("c+", msg.lower())

        # Math at C+ (7 points)
        scores['math'] = 7
        eligible, msg = check_eligibility(0, scores)
        self.assertTrue(eligible)

    def test_nursing_vs_health_eligibility(self):
        # Bio below C+ (6 points) -> Ineligible
        scores = {'math': 7, 'english': 8, 'biology': 6, 'chemistry': 0}
        eligible, msg = check_eligibility(1, scores)
        self.assertFalse(eligible)

        # Bio C+ (7 points) -> Eligible for nursing
        scores['biology'] = 7
        eligible, msg = check_eligibility(1, scores)
        self.assertTrue(eligible)

    def test_business_math_requirement(self):
        # Math D+ (4 points) -> Ineligible for Business (needs C = 6pts)
        scores = {'math': 4, 'english': 8}
        eligible, msg = check_eligibility(2, scores)
        self.assertFalse(eligible)
        self.assertIn("c (6pts)", msg.lower())

        # Math C (6 points) -> Eligible
        scores['math'] = 6
        eligible, msg = check_eligibility(2, scores)
        self.assertTrue(eligible)


class TestSecurityFunctions(unittest.TestCase):
    def test_xss_sanitization(self):
        dirty = "<script>alert('xss')</script><strong>Great choice!</strong><img src=x onerror=alert(1)>"
        cleaned = sanitize_html(dirty)
        self.assertNotIn("<script>", cleaned)
        self.assertNotIn("alert", cleaned)
        self.assertNotIn("<img", cleaned)
        self.assertIn("<strong>Great choice!</strong>", cleaned)

    def test_password_strength_validator(self):
        self.assertIsNotNone(validate_password("short"))
        self.assertIsNotNone(validate_password("alllowercase1!"))
        self.assertIsNotNone(validate_password("ALLUPPERCASE1!"))
        self.assertIsNotNone(validate_password("NoSpecialChar123"))
        self.assertIsNotNone(validate_password("NoNumberHere!@#"))
        # Valid password
        self.assertIsNone(validate_password("ValidP@ssw0rd!"))

    def test_session_and_security_configuration(self):
        from app import app, login_manager
        from datetime import timedelta

        # Session timeout is 30 minutes
        self.assertEqual(app.config['PERMANENT_SESSION_LIFETIME'], timedelta(minutes=30))
        # Rolling session resets timer on user activity
        self.assertTrue(app.config['SESSION_REFRESH_EACH_REQUEST'])
        # Cookie security
        self.assertTrue(app.config['SESSION_COOKIE_HTTPONLY'])
        self.assertEqual(app.config['SESSION_COOKIE_SAMESITE'], 'Lax')
        # Session protection against hijacking
        self.assertEqual(login_manager.session_protection, 'strong')
        # Database pool resilience
        self.assertTrue(app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_pre_ping'])
        self.assertEqual(app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_recycle'], 280)


class TestInteractionLogic(unittest.TestCase):
    def test_interaction_detection(self):
        self.assertEqual(
            detect_interaction_preference("I love helping people and collaborating in teams")[0],
            2
        )
        self.assertEqual(
            detect_interaction_preference("I prefer working alone doing solo coding and debugging algorithms")[0],
            -1
        )


class TestEducationSystems(unittest.TestCase):
    def test_curriculum_grade_normalization(self):
        from education_systems import parse_curriculum_grade, CURRICULA

        # KCSE
        self.assertEqual(parse_curriculum_grade('ke_kcse', 'A'), 12)
        self.assertEqual(parse_curriculum_grade('ke_kcse', 'C+'), 7)
        self.assertEqual(parse_curriculum_grade('ke_kcse', 'E'), 1)

        # Rwanda NESB
        self.assertEqual(parse_curriculum_grade('rw_nesb', 'A'), 12)
        self.assertEqual(parse_curriculum_grade('rw_nesb', 'B'), 10)
        self.assertEqual(parse_curriculum_grade('rw_nesb', 'S'), 2)
        self.assertEqual(parse_curriculum_grade('rw_nesb', 'F'), 0)

        # Uganda UACE
        self.assertEqual(parse_curriculum_grade('ug_uace', 'A'), 12)
        self.assertEqual(parse_curriculum_grade('ug_uace', 'O'), 2)

        # West Africa WASSCE
        self.assertEqual(parse_curriculum_grade('wa_wassce', 'A1'), 12)
        self.assertEqual(parse_curriculum_grade('wa_wassce', 'B2'), 11)
        self.assertEqual(parse_curriculum_grade('wa_wassce', 'C4'), 8)
        self.assertEqual(parse_curriculum_grade('wa_wassce', 'F9'), 0)

        # Cambridge International
        self.assertEqual(parse_curriculum_grade('intl_cambridge', 'A*'), 12)
        self.assertEqual(parse_curriculum_grade('intl_cambridge', 'A'), 11)
        self.assertEqual(parse_curriculum_grade('intl_cambridge', 'B'), 9)
        self.assertEqual(parse_curriculum_grade('intl_cambridge', 'U'), 0)

        # Not taken / empty
        self.assertEqual(parse_curriculum_grade('ke_kcse', 'NOT TAKEN'), 0)
        self.assertEqual(parse_curriculum_grade('wa_wassce', ''), 0)


class TestMultiUniversityAdvisor(unittest.TestCase):
    def test_universities_and_catalogs(self):
        from education_systems import UNIVERSITIES, get_country_options

        expected_unis = {'usiu', 'strathmore', 'alu', 'makerere', 'ashesi', 'all'}
        self.assertTrue(expected_unis.issubset(set(UNIVERSITIES.keys())))

        for uid, udata in UNIVERSITIES.items():
            self.assertIn('name', udata)
            self.assertIn('country', udata)
            if uid != 'all':
                self.assertGreater(len(udata['catalog']), 0)

        countries = get_country_options()
        self.assertGreaterEqual(len(countries), 4)

    def test_multi_university_ai_recommendation(self):
        from ai_interest_analyzer import analyze_interest_text_advanced

        scores = {
            'math': 12, 'english': 12, 'kiswahili': 10,
            'biology': 12, 'physics': 12, 'chemistry': 12,
            'humanities': 12, 'tech_business': 12
        }

        # Test ALU target
        cat, conf, kws, reason, major, school = analyze_interest_text_advanced(
            interest_text="I want to lead startups and build software systems for African growth.",
            grades_dict=scores,
            username="Aline",
            target_uni="alu",
            country="Rwanda",
            curriculum_id="rw_nesb"
        )
        self.assertTrue(len(major) > 0)
        self.assertGreaterEqual(conf, 80)
        self.assertIn("Aline", reason)


if __name__ == '__main__':
    unittest.main(verbosity=2)
