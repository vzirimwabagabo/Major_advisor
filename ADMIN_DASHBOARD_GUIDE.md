# 🎓 USIU Major Advisor - Admin Dashboard Documentation

## Overview

The enhanced admin dashboard provides comprehensive tools for system administrators to manage users, recommendations, analytics, and data. This gives admins complete control over the Flask application.

---

## 🔐 Admin Access

- **Route**: `/admin`
- **Access**: Must be logged in as an admin user
- **Redirect**: Non-admins are redirected to home with access denied message

---

## 📊 Dashboard Navigation

### Main Navigation (Sidebar)

The admin dashboard includes a fixed sidebar with these sections:

```
🔧 Admin Panel
├── 📊 Dashboard
├── 📋 All Recommendations
├── 📈 Analytics & Insights
├── 💾 Export Data
├── 🏠 Back to Home
└── 🚪 Logout
```

---

## 📋 Dashboard Pages & Features

### 1. **Main Dashboard** (`/admin`)

#### Overview Statistics
- **👥 Total Users**: Count of all registered students and admins
- **📋 Total Recommendations**: Total number of recommendations made
- **👨‍🎓 Unique Students (CSV)**: Count from collected CSV data
- **⭐ Average Confidence**: Mean confidence score of all recommendations

#### Recent Recommendations (Last 5)
- Shows most recent 5 recommendations
- Displays: Date/Time, Student, Major, School, Confidence
- Quick **View** button for each recommendation

#### User Management
- Complete user list with all details
- **User Info**: ID, Username, Email, Role (Admin/Student)
- **Recommendation Count**: How many recommendations each student has
- **Admin Actions**:
  - 👀 **History**: View all recommendations for a student
  - **Make Admin**: Promote student to admin (if not admin)
  - **Remove Admin**: Demote admin back to student
  - **Delete**: Remove user and all their recommendations (with confirmation)

#### Quick Actions
- Direct links to recommendations, analytics, and data export

---

### 2. **All Recommendations** (`/admin/recommendations`)

#### Search & Filter
- **Search by**: Student username, email, or major name
- **Filter by**: School/Faculty (dropdown)
- **Clear filters**: Reset search and return to full list

#### Recommendation Table
Shows paginated list (20 per page) with:
- **ID**: Unique recommendation identifier
- **Date**: When recommendation was made
- **Student**: Username of the student
- **Email**: Student's email address
- **Major**: Recommended major program
- **School**: Faculty/School offering the major
- **Confidence**: Confidence score as percentage
- **Actions**:
  - 👁️ **View**: See full recommendation details
  - 🗑️ **Delete**: Remove recommendation and confirm

#### Pagination
- Navigate between pages of recommendations
- Shows current page and total pages
- Previous/Next buttons with disabled states

---

### 3. **Recommendation Details** (`/admin/recommendation/<id>`)

#### View Full Recommendation
Shows comprehensive information:

**Recommendation Information Section**
- Recommendation ID
- Date/Time (precise timestamp)
- **Recommended Major** (highlighted)
- Faculty/School
- **Confidence Score** (with visual progress bar)

**Student Information Section**
- Student Name
- Email Address
- Student ID
- Total Recommendations This Student Has
- Account Status (Admin or Student)
- Link to View All Student's Recommendations

#### Actions
- ← Back to Recommendations list
- 🗑️ Delete this specific recommendation (with confirmation)

---

### 4. **Student Recommendation History** (`/admin/user/<id>/history`)

#### Student Information Card
Shows:
- Student username (prominently displayed)
- Email address
- User ID number
- Total number of recommendations made
- Account type (Admin or Student)

#### All Recommendations Table
Displays all recommendations for this specific student:
- **ID**: Recommendation identifier
- **Date/Time**: When recommendation was made
- **Major**: Recommended program
- **School**: Faculty offering it
- **Confidence**: Confidence score
- **View**: Link to recommendation details

---

### 5. **Analytics & Insights** (`/admin/analytics`)

#### Key Metrics Dashboard
- 📋 Total Recommendations (lifetime)
- 👥 Total Users (system-wide)
- 📅 Recommendations This Week
- ⭐ Average Confidence Score

#### Top 10 Recommended Majors
- Visual bar chart with:
  - Major name
  - Number of recommendations
  - Percentage of total
- Helps identify popular programs

#### Recommendations by School/Faculty
- Table showing:
  - School/Faculty name
  - Number of recommendations
  - Percentage distribution
- Guides resource allocation

#### Average Confidence by Major
- Top 10 majors by average confidence
- Shows which majors have most reliable recommendations
- Visual bar chart with percentages

#### Quick Statistics
- Unique students from CSV data
- Average confidence score
- Recommendations per student (average)

---

### 6. **Export Data** (`/admin/export-data`)

#### Export Options
- **Download as CSV**: Click to download all data
- One-click export to standard format

#### CSV Preview
- Shows first 1000 characters of CSV data
- Helps verify data before full download

#### Export Information
Lists columns included in CSV export:
1. Recommendation ID
2. Student Username
3. Student Email
4. Major Recommended
5. School
6. Confidence Score %
7. Date (YYYY-MM-DD)
8. Time (HH:MM:SS)

#### Data Analysis Ready
- Open in Excel, Google Sheets, Python, R, etc.
- Perfect for statistical analysis
- Can create pivot tables and custom reports

---

## 🎯 Key Admin Functions

### User Management

#### Toggle Admin Status
- Promote students to admins
- Demute admins back to students
- Cannot perform on own account

#### Delete User
- **Confirmation required** to prevent accidents
- Automatically deletes all user's recommendations
- Irreversible action (use carefully)
- Cannot delete own account

#### View User History
- See all recommendations made by a student
- Track recommendation patterns
- Understand student decision-making journey

---

### Recommendation Management

#### View Recommendations
- **Browse all** recommendations in the system
- **Search** by student or major name
- **Filter** by school/faculty
- **Sort** by date, confidence, etc.

#### View Recommendation Details
- See complete information about any recommendation
- Understand reasoning behind each recommendation
- Track student-major matching

#### Delete Recommendations
- Remove individual recommendations
- Two-step process (click delete, then confirm)
- Useful for correcting errors or anomalies

---

### Analytics & Reporting

#### Pre-Built Insights
- Top recommended majors
- School distribution
- Confidence score analysis
- Weekly trends

#### CSV Export
- Export all data for custom analysis
- Import into external tools
- Create custom reports
- Statistical analysis

---

## 📊 Data Considerations

### Where Data Comes From

1. **Database** (SQLite):
   - User accounts and credentials
   - Recommendation records stored
   - Login history timestamps

2. **CSV File** (`student_recommendation_data.csv`):
   - Real-time student data collection
   - Input scores and recommendations
   - Used for data analytics

### Data Synchronization
- Database stores structured recommendations
- CSV stores all input parameters
- Both updated simultaneously when recommendation made
- Independent data sources = redundancy

---

## 🔒 Security & Access Control

### Required Permissions
- Must be logged in
- Must be marked as admin in database
- Non-admins automatically redirected

### Admin Checks
```python
if not current_user.is_admin:
    flash('Access Denied: Administrators only.', 'danger')
    return redirect(url_for('index'))
```

### Dangerous Operations
- User deletion requires confirmation
- Recommendation deletion requires confirmation
- Admin status changes logged implicitly

---

## 🛠️ Technical Details

### New Backend Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin` | GET | Main admin dashboard |
| `/admin/recommendations` | GET | List all recommendations |
| `/admin/recommendation/<id>` | GET | View recommendation details |
| `/admin/recommendation/<id>/delete` | GET/POST | Delete recommendation |
| `/admin/user/<id>/history` | GET | View student's history |
| `/admin/delete-user/<id>` | POST | Delete user account |
| `/admin/analytics` | GET | Analytics dashboard |
| `/admin/export-data` | GET | Export data view |
| `/admin/export-csv` | GET | Download CSV file |
| `/toggle_admin/<id>` | GET | Toggle admin status |

### Database Queries Used

- `User.query.all()` - Get all users
- `Result.query.join(User)` - Join recommendations with users
- `Result.query.filter_by()` - Search recommendations
- `Result.query.paginate()` - Paginate results (20 per page)
- `func.count()`, `func.avg()` - Aggregate statistics
- `func.group_by()` - Group by school/major

### Response Types

- **HTML Templates**: Rendered pages for admin interface
- **CSV Downloads**: Direct file download with headers
- **Redirects**: Navigate between admin pages
- **Flash Messages**: User feedback (success/error)

---

## 📱 User Interface

### Design Principles
- **Dark Red Sidebar** (#8B0000): USIU brand colors
- **White Cards**: Clean, readable content areas
- **Responsive Layout**: Works on desktop and mobile
- **Clear Navigation**: Intuitive sidebar always visible
- **Consistent Styling**: Buttons, tables, forms throughout

### Accessibility Features
- Clear headings and structure
- Color contrast meets standards
- Keyboard navigation support
- Confirmation dialogs for dangerous actions
- Mobile-responsive design

---

## 🚀 Usage Workflows

### Workflow 1: Review Recent Recommendations
1. Go to `/admin` (Main Dashboard)
2. See "Recent Recommendations (Last 5)"
3. Click "View" to see full details
4. Check recommendation appropriateness

### Workflow 2: Find Recommendations for Specific Student
1. Go to `/admin/recommendations` (All Recommendations)
2. Type student name in search box
3. Click 🔍 Search
4. Review all recommendations for that student

### Workflow 3: Analyze System Trends
1. Go to `/admin/analytics` (Analytics & Insights)
2. View "Top 10 Recommended Majors"
3. Check "Average Confidence by Major"
4. Export data for deeper analysis

### Workflow 4: Export Data for Analysis
1. Go to `/admin/export-data` (Export Data)
2. Click "📥 Download as CSV"
3. Open in Excel/Google Sheets/Python
4. Create custom reports and pivot tables

### Workflow 5: Manage User Permissions
1. Go to `/admin` (Main Dashboard)
2. Scroll to "User Management" section
3. Find user to promote/demote
4. Click "Make Admin" or "Remove Admin"

---

## ⚠️ Important Notes

### Data Integrity
- Deleting user also deletes their recommendations
- No automatic backup created before deletion
- CSV data independent from database
- Can restore from CSV if needed

### Performance
- Recommendations paginated (20 per page)
- Large datasets shown efficiently
- Analytics queries optimized
- CSV export handles large datasets

### Best Practices
1. **Backup regularly** before major admin actions
2. **Verify data** before exporting for reports
3. **Use pagination** when browsing large datasets
4. **Confirm deletions** carefully
5. **Monitor analytics** for system health

---

## 📈 Future Enhancements

Potential admin features to add:
- Bulk import users from CSV
- Recommendation approval workflow
- Email notifications for new recommendations
- Custom report builder
- Admin action audit log
- System settings management
- Recommendation rule editor
- Student feedback ratings on recommendations

---

## 💡 Tips for Admins

### Data Analysis
- Export recommendations monthly
- Track trends over time
- Identify popular majors
- Monitor avg confidence scores

### User Management
- Regular cleanup of inactive accounts
- Promote helpful students to admins
- Track usage patterns per student
- Review student histories before deletion

### System Health
- Check analytics weekly
- Review recent recommendations
- Monitor recommendations per student
- Identify anomalies in data

---

**Admin Dashboard Version**: 2.0  
**Last Updated**: March 2026  
**Status**: ✅ Production Ready
