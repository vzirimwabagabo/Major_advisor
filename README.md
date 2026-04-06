# 🎓 USIU-Africa Major Advisor: AI-Powered Career Guidance

An intelligent recommendation system designed to bridge the gap between high school academic performance (KCSE) and university success at USIU-Africa.

---

## 🚀 Overview

The **USIU-Africa Major Advisor** is a hybrid intelligence platform that helps students discover their ideal major. It combines the rigorous academic standards of USIU-Africa with the advanced natural language understanding of **Google Gemini AI** to provide deeply personalized, human-like guidance.

### ✨ Key Features

*   **🧠 Gemini-Powered Brain**: Analyzes student interests and career passions using state-of-the-art LLM technology.
*   **👤 Personalization Engine**: Addresses every student by name and crafts unique, conversational "Decision Logic" for every request.
*   **🛡️ Safety Validator**: An internal rule-engine that ensures students meet mandatory KCSE prerequisites (e.g., Group I subjects like Math/English) before recommending a major.
*   **📊 Future-Ready Data**: Automatically logs student profiles and recommendations to CSV for future Machine Learning model training.
*   **🖥️ Admin Insights**: A dedicated dashboard for administrators to monitor school-wide trends and student interests.

---

## 🛠️ Technical Architecture

The system follows a **Hybrid Intelligence** model:

1.  **AI Layer (Google Gemini)**: Handles the "Human" side of advice—interpreting passions, matching them to the USIU catalog, and generating unique reasoning.
2.  **Rule Layer (Local Python Logic)**: Handles the "Academic" side—enforcing strict USIU admission criteria and KCSE point thresholds.
3.  **Persistence Layer (Supabase/PostgreSQL)**: Securely stores user profiles and historical recommendations.
4.  **Deployment (Vercel)**: Scalable serverless infrastructure with production-grade security (Flask-Talisman).

---

## 📖 How It Works

1.  **Input**: Student enters their KCSE grades across 8 subjects and describes their career passion (e.g., *"I want to lead technical teams"*).
2.  **AI Interpretation**: Gemini analyzes the text, detects the core interest (e.g., "Leadership" + "Technology"), and selects the best-fit Major.
3.  **Cross-Validation**: The system checks if the student's grades meet the USIU requirements for that specific major.
4.  **Result**: The student receives a personalized greeting and a detailed justification: 
    > *"Hi [Name], your passion for leadership combined with your A in Math makes you a perfect candidate for Applied Computer Technology..."*

---

## 🚦 Getting Started

### Prerequisites

*   Python 3.10+
*   Google Gemini API Key
*   PostgreSQL Database (Supabase recommended)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/vzirimwabagabo/Major_advisor.git
    cd Major_advisor
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure environment variables in `.env`:
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    DATABASE_URL=postgresql://...
    GEMINI_API_KEY=your_key_here
    SECRET_KEY=your_secret_key
    ```
4.  Run the server:
    ```bash
    python run_waitress.py
    ```

---

## 📈 Future Roadmap

*   **Self-Training ML**: Once the CSV reaches 1,000+ entries, train a custom `RandomForest` model as a local fallback.
*   **Financial Aid Integration**: Suggest scholarships based on high-performing KCSE profiles.
*   **Alumni Connect**: Link recommended majors to successful alumni profiles at USIU-Africa.

---

**Developed for APT4900 - USIU-Africa 2026** 🎓✨
