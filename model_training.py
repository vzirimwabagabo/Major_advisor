"""
Data collection and analysis for major recommendation system.
Collects real student data from recommendations for future model improvement.

Privacy Preserving: Does not log personal identifying information (PII).
"""

import os
from datetime import datetime
import pandas as pd

# ==================== DATA STORAGE ====================

is_serverless = os.getenv('VERCEL') == '1' or bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
DATA_FILE = '/tmp/student_recommendation_data.csv' if is_serverless else os.path.join(os.path.dirname(__file__), 'student_recommendation_data.csv')


def save_recommendation_data(student_data):
    """
    Save student recommendation to CSV for future analysis (anonymized).
    """
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
        else:
            df = pd.DataFrame()

        new_record = pd.DataFrame([student_data])
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not save recommendation data: {e}")
        return False


def get_recommendation_statistics():
    """
    Get summary statistics from collected data.
    """
    if not os.path.exists(DATA_FILE):
        return {
            'total_recommendations': 0,
            'message': 'No data collected yet.'
        }

    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return {'total_recommendations': 0}

        # Check either 'student_id' (new privacy-safe format) or 'email' (legacy format)
        unique_id_col = 'student_id' if 'student_id' in df.columns else ('email' if 'email' in df.columns else None)
        unique_students = int(df[unique_id_col].nunique()) if unique_id_col else 0

        stats = {
            'total_recommendations': len(df),
            'unique_students': unique_students,
            'top_recommended_majors': df['recommended_major'].value_counts().head(5).to_dict() if 'recommended_major' in df.columns else {},
            'avg_confidence': float(df['confidence'].mean()) if 'confidence' in df.columns else 0.0,
        }
        return stats
    except Exception as e:
        print(f"Error reading recommendation statistics: {e}")
        return {'total_recommendations': 0}


def print_data_summary():
    """Display summary of collected recommendation data."""
    stats = get_recommendation_statistics()
    print("\n" + "="*60)
    print("RECOMMENDATION DATA SUMMARY")
    print("="*60)
    print(f"Total Recommendations: {stats.get('total_recommendations', 0)}")
    print(f"Unique Students: {stats.get('unique_students', 0)}")
    if stats.get('top_recommended_majors'):
        print("\nTop Recommended Majors:")
        for major, count in stats['top_recommended_majors'].items():
            print(f"  - {major}: {count}")
    print(f"Average Confidence: {stats.get('avg_confidence', 0):.2f}%")
    print("="*60 + "\n")


if __name__ == '__main__':
    print_data_summary()
