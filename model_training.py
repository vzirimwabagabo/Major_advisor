"""
Data collection and analysis for major recommendation system.
Collects real student data from recommendations for future model improvement.

REFACTORED APPROACH:
Instead of training on synthetic random data, we now:
1. Use rule-based logic that encodes USIU admission criteria
2. Collect real student data with each recommendation
3. Build authentic data over time for future model training
"""

import pandas as pd
import os
from datetime import datetime

# ==================== DATA STORAGE ====================

DATA_FILE = 'student_recommendation_data.csv'


def save_recommendation_data(student_data):
    """
    Save student recommendation to CSV for future analysis.
    This allows us to build real data over time from actual users.
    
    Args:
        student_data: dict with keys:
            - username: student username
            - email: student email
            - math, english, kiswahili, biology, physics, chemistry, humanities, tech_business
            - interest: interest area selected
            - recommended_major: major recommended
            - school: school of major
            - confidence: confidence score
            - timestamp: when recommendation was made
    """
    try:
        # Check if file exists
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
        else:
            df = pd.DataFrame()
        
        # Create new record
        new_record = pd.DataFrame([student_data])
        
        # Append to dataframe
        df = pd.concat([df, new_record], ignore_index=True)
        
        # Save to CSV
        df.to_csv(DATA_FILE, index=False)
        print(f"✓ Student recommendation data saved to {DATA_FILE}")
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not save recommendation data: {e}")
        return False


def get_recommendation_statistics():
    """
    Get statistics from collected data.
    
    Returns:
        dict with summary statistics
    """
    if not os.path.exists(DATA_FILE):
        return {
            'total_recommendations': 0,
            'message': 'No data collected yet.'
        }
    
    df = pd.read_csv(DATA_FILE)
    
    stats = {
        'total_recommendations': len(df),
        'unique_students': df['email'].nunique() if 'email' in df.columns else 0,
        'top_recommended_majors': df['recommended_major'].value_counts().head(5).to_dict() if 'recommended_major' in df.columns else {},
        'avg_confidence': df['confidence'].mean() if 'confidence' in df.columns else 0,
    }
    return stats


def print_data_summary():
    """Display summary of collected recommendation data."""
    stats = get_recommendation_statistics()
    print("\n" + "="*60)
    print("RECOMMENDATION DATA SUMMARY")
    print("="*60)
    print(f"Total Recommendations: {stats['total_recommendations']}")
    print(f"Unique Students: {stats.get('unique_students', 0)}")
    if stats.get('top_recommended_majors'):
        print("\nTop Recommended Majors:")
        for major, count in stats['top_recommended_majors'].items():
            print(f"  - {major}: {count}")
    print(f"Average Confidence: {stats.get('avg_confidence', 0):.2f}%")
    print("="*60 + "\n")


if __name__ == '__main__':
    print("Student Recommendation Data Collection System")
    print("=" * 60)
    print("This system collects REAL student data for model improvement.")
    print("Data is saved to: student_recommendation_data.csv")
    print("\nKey Change:")
    print("  The model now uses DETERMINISTIC RULE-BASED LOGIC")
    print("  instead of training on synthetic random data.")
    print("\nRecommendation factors:")
    print("  1. KCSE Subject Scores (8 subjects)")
    print("  2. Student Interest Area")
    print("  3. USIU-Africa Admission Criteria (built-in rules)")
    print("  4. Academic Performance Patterns")
    print("\nAs real data accumulates, we can build ML models")
    print("based on ACTUAL student performance patterns.")
    print("="*60)
    
    # Show current statistics
    print_data_summary()