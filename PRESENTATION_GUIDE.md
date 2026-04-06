# 🎤 Presentation Guide: USIU-Africa Major Advisor

Use this guide to structure your presentation and highlight the "WOW" factors of your AI system.

## 1. The Problem Statement
*   Many students choose majors based on family pressure or generic advice.
*   Manual academic advising is time-consuming and often misses the "passion" factor.
*   **Your Solution**: An AI companion that understands dreams and validates them against reality.

## 2. Technical Highlights (The "Brain")
*   **Google Gemini Integration**: We aren't just using simple keywords. We are using a Large Language Model (LLM) to "listen" to the student's passion.
*   **The Hybrid Model**: Explain that it is **Deterministic + Generative**. 
    *   *Deterministic*: Hard rules for grades (Consistency).
    *   *Generative*: AI for personality and advice (Engagement).
*   **Data Collection**: Mention the `student_recommendation_data.csv`. This shows you aren't just building a one-off tool, but a **system that learns over time**.

## 3. Key "WOW" Factors for the Demo
*   **Personalization**: Show how the AI calls the user by name.
*   **Uniqueness**: Show that if you ask the same thing twice, the AI gives slightly different, better advice (not a hardcoded template).
*   **Passion-First**: Demo a student with high grades in every subject but a specific interest in "Film." Show how the AI honors that choice instead of just suggesting "Engineering" because of the grades.

## 4. Potential Questions & Answers
*   **Q: What happens if the AI suggests something the student can't do?**
    *   *A: We have a "Safety Validator" layer. It checks the suggested major against KCSE rules and adds a warning if prerequisites are missing.*
*   **Q: Why use Gemini and not just a trained model?**
    *   *A: Gemini provides high "Semantic Intelligence" (understanding meaning) immediately. We are collecting data now so we can train a local model later.*
*   **Q: How secure is the data?**
    *   *A: User accounts are stored in a PostgreSQL database with hashed passwords and protected by Flask-Talisman security headers.*

## 5. Closing Vision
"This isn't just a major recommender; it's the future of the USIU-Africa student experience—personalized, intelligent, and data-driven."
