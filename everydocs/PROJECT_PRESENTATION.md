# 🎓 USIU Major Advisor System
## AI-Powered Academic Guidance Platform

---

## 📋 **Project Overview**

### **🎯 Mission Statement**
> "Empowering USIU-Africa undergraduate students with intelligent, data-driven major selection guidance based on their KCSE performance and personal interests."

### **🏫 Target Institution**
- **United States International University - Africa (USIU-Africa)**
- Nairobi, Kenya
- Premier private university focused on international education

### **👥 Target Users**
- **Primary:** KCSE graduates seeking undergraduate admission
- **Secondary:** Current students considering major changes
- **Tertiary:** Academic advisors and administrators

---

## 🏗️ **System Architecture**

### **Core Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Rule Engine    │    │   Data Layer    │
│   (Flask App)   │◄──►│ (Python Logic)  │◄──►│ (SQLite/JSON)   │
│                 │    │                 │    │                 │
│ • User Auth     │    │ • KCSE Analysis │    │ • User Accounts │
│ • Forms         │    │ • Interest Match │    │ • Recommendations│
│ • Dashboards    │    │ • Eligibility   │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**
- **Backend:** Python Flask 2.3.3
- **Database:** SQLite (production) / JSON (alternative)
- **Authentication:** Flask-Login + Flask-Bcrypt
- **Frontend:** HTML5, CSS3, JavaScript
- **AI Logic:** Custom rule-based recommendation engine

---

## 👥 **User Roles & Capabilities**

### **🎓 NORMAL USERS (Students)**

#### **Account Management**
- ✅ **Self-registration** with email verification
- ✅ **Secure login/logout** with session management
- ✅ **Password-protected** accounts
- ✅ **Account deletion** with data cleanup

#### **Major Recommendation Process**
1. **Input KCSE Grades** (8 subjects)
   - Mathematics, English, Kiswahili (Compulsory)
   - Biology, Physics, Chemistry (Sciences)
   - Humanities, Technical/Business (Electives)

2. **Select Interest Area** (5 options)
   - Business & Management
   - Science & Technology
   - Humanities & Social Sciences
   - Health Sciences
   - Arts & Communication

3. **Receive AI Recommendation**
   - **Major suggestion** from 18 USIU programs
   - **School/faculty** assignment
   - **Confidence score** (65-95%)
   - **Detailed explanation** of reasoning

#### **Personal Dashboard**
- ✅ **Recommendation history** (all past results)
- ✅ **Input data review** (grades entered)
- ✅ **Progress tracking** over time
- ✅ **Account management** options

---

### **👨‍💼 ADMINISTRATORS (System Managers)**

#### **User Management**
- ✅ **View all registered users**
- ✅ **Promote users** to admin role
- ✅ **Demote admin** privileges
- ✅ **Delete user accounts** (with cascade)
- ✅ **Monitor user activity**

#### **Recommendation Oversight**
- ✅ **View all recommendations** system-wide
- ✅ **Search by student name/email/major**
- ✅ **Filter by school/faculty**
- ✅ **Detailed recommendation review**
- ✅ **Delete inappropriate recommendations**

#### **Analytics & Insights**
- ✅ **System statistics** (users, recommendations)
- ✅ **Top majors** analysis
- ✅ **School distribution** reports
- ✅ **Confidence score** trends
- ✅ **Weekly activity** tracking

#### **Data Management**
- ✅ **CSV export** functionality
- ✅ **Data backup** capabilities
- ✅ **System health** monitoring
- ✅ **Performance analytics**

---

## 🎯 **How It Works: The Recommendation Engine**

### **Phase 1: Input Processing**
```
User Input → Validation → Score Conversion → Interest Analysis
```

#### **Grade Conversion System**
| KCSE Grade | Points | Description |
|------------|--------|-------------|
| A          | 12     | Excellent   |
| A-         | 11     | Very Good   |
| B+         | 10     | Good        |
| B          | 9      | Above Avg   |
| B-         | 8      | Average     |
| C+         | 7      | Below Avg   |
| C          | 6      | Fair        |
| C-         | 5      | Poor        |
| D+         | 4      | Very Poor   |
| D          | 3      | Failing     |
| D-         | 2      | Critical    |

### **Phase 2: Eligibility Check**
- **Compulsory Subjects:** Math, English, Kiswahili (minimum requirements)
- **Interest Alignment:** Match user interest with available programs
- **Score Validation:** Ensure minimum thresholds for programs

### **Phase 3: Recommendation Logic**
```
Interest + Scores → Field Analysis → Program Matching → Confidence Calculation
```

#### **18 USIU Programs Across 5 Schools:**

**🏢 Chandaria School of Business**
- Accounting, Finance, Management, Marketing, International Business

**🔬 School of Science & Technology**
- Computer Science, Applied Computer Technology, Actuarial Science

**📚 School of Humanities & Social Sciences**
- International Relations, Psychology, Development Studies

**🏥 School of Pharmacy & Health Sciences**
- Pharmacy, Public Health, Nursing

**🎨 School of Communication, Arts & Social Sciences**
- Communications, Film & Animation, Journalism

### **Phase 4: Smart Fallback System**
- **Undecided Students:** AI analyzes all fields, suggests best fit
- **Ineligible Choices:** Finds alternative programs based on strengths
- **Confidence Scoring:** 65-95% based on score-program alignment

---

## 🔐 **Security & Privacy**

### **Authentication System**
- **Password Hashing:** Bcrypt encryption
- **Session Management:** Secure Flask-Login sessions
- **Role-Based Access:** Admin vs. regular user permissions
- **CSRF Protection:** Built-in Flask security

### **Data Protection**
- **Personal Data:** Encrypted storage
- **Access Control:** Users see only their data
- **Admin Oversight:** Controlled administrative access
- **Audit Trail:** All actions logged

### **Account Safety**
- **Password Confirmation:** Required for account deletion
- **Admin Protection:** Cannot delete last admin
- **Data Cleanup:** Complete removal on account deletion

---

## 📊 **Data Flow & Storage**

### **Dual Storage Options**

#### **Primary: SQLite Database**
```
site.db/
├── users (id, username, email, password_hash, is_admin)
├── results (id, major, school, confidence, timestamp, user_id)
└── Foreign key relationships
```

#### **Alternative: JSON Files**
```
data/
├── users.json (user accounts)
└── recommendations.json (recommendation data)
```

### **Analytics Integration**
- **CSV Export:** `student_recommendation_data.csv`
- **Real-time Statistics:** Database aggregation
- **Trend Analysis:** Historical data patterns

---

## 🎨 **User Experience Design**

### **Interface Principles**
- **Intuitive Navigation:** Clear menu structure
- **Mobile Responsive:** Works on all devices
- **USIU Branding:** University colors and identity
- **Accessibility:** Screen reader compatible

### **Workflow Optimization**
- **Progressive Disclosure:** Show information as needed
- **Smart Defaults:** Pre-filled common values
- **Error Prevention:** Validation before submission
- **Feedback Systems:** Clear success/error messages

### **Visual Design**
- **Color Scheme:** USIU red (#8B0000) and professional grays
- **Typography:** Clean, readable fonts
- **Layout:** Card-based design with clear sections
- **Icons:** Intuitive symbols for actions

---

## 📈 **Analytics & Reporting**

### **Real-time Metrics**
- Total users and active accounts
- Recommendation volume and trends
- Popular majors and schools
- Average confidence scores

### **Admin Dashboard Features**
- **Interactive Charts:** Top majors visualization
- **Search & Filter:** Advanced data querying
- **Export Capabilities:** CSV download for external analysis
- **Performance Monitoring:** System health indicators

### **Student Insights**
- **Personal History:** Individual recommendation tracking
- **Progress Analysis:** Improvement over time
- **Alternative Suggestions:** Backup options when needed

---

## 🚀 **Deployment & Scalability**

### **Current Deployment**
- **Local Development:** Flask development server
- **Database:** SQLite (file-based)
- **Static Files:** Local assets

### **Production Readiness**
- **WSGI Server:** Gunicorn for production
- **Database:** PostgreSQL for scalability
- **Caching:** Redis for session management
- **CDN:** Static file delivery

### **Scalability Features**
- **Modular Architecture:** Easy feature addition
- **API Design:** RESTful endpoints for mobile apps
- **Data Export:** Multiple format support
- **Backup Systems:** Automated data preservation

---

## 🔮 **Future Enhancements**

### **Phase 1: Enhanced AI**
- **Machine Learning:** Train on real student outcomes
- **Predictive Analytics:** Success probability modeling
- **Career Pathing:** Long-term career recommendations

### **Phase 2: Extended Features**
- **Mobile App:** Native iOS/Android applications
- **Social Features:** Student community discussions
- **Integration:** USIU student portal connection
- **Notifications:** Email/SMS alerts

### **Phase 3: Advanced Analytics**
- **Big Data:** Large-scale student data analysis
- **Predictive Modeling:** Admission success forecasting
- **Market Research:** Industry trend integration
- **Global Comparisons:** International university data

---

## 🏆 **Key Achievements**

### **✅ Technical Excellence**
- **Rule-Based AI:** Deterministic, explainable recommendations
- **Dual Storage:** SQLite + JSON flexibility
- **Security First:** Comprehensive authentication system
- **Scalable Design:** Modular, maintainable codebase

### **✅ User Experience**
- **Intuitive Interface:** Professional, accessible design
- **Complete Workflows:** End-to-end user journeys
- **Role Optimization:** Tailored experiences for each user type
- **Data Privacy:** Secure, user-controlled data management

### **✅ Educational Impact**
- **Academic Guidance:** Data-driven major selection
- **USIU Alignment:** Institution-specific program knowledge
- **Student Success:** Better-informed educational choices
- **Administrative Efficiency:** Streamlined student management

---

## 📞 **System Requirements**

### **Minimum Requirements**
- **Python:** 3.8+
- **Memory:** 512MB RAM
- **Storage:** 100MB disk space
- **Browser:** Modern web browser

### **Recommended Setup**
- **Python:** 3.9+
- **Memory:** 1GB RAM
- **Database:** PostgreSQL (production)
- **Server:** Linux/Windows with WSGI

---

## 🎯 **Conclusion**

The **USIU Major Advisor System** represents a comprehensive solution for intelligent academic guidance, combining:

- **🤖 Advanced AI** with rule-based recommendation logic
- **🔐 Enterprise Security** with role-based access control
- **📊 Rich Analytics** for both students and administrators
- **🎨 Professional UX** with mobile-responsive design
- **🏗️ Scalable Architecture** ready for future growth

This system empowers students to make informed major selections while providing administrators with powerful tools to manage and analyze the academic guidance process.

**Ready for deployment and real-world impact!** 🚀

---

*Developed for United States International University - Africa*  
*March 2026 - Academic Year 2026/2027*</content>
<parameter name="filePath">c:\Users\PC\OneDrive - United States International University (USIU)\Desktop\USIU-NOTES\USIU-NOTES 2026\APT4900\secured site\secured site\PROJECT_PRESENTATION.md