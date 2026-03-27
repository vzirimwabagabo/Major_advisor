# ⚡ Admin Dashboard - Quick Reference Guide

## 🔗 All Admin Routes

```
/admin                          📊 Main Dashboard
├── Statistics overview
├── Recent recommendations (5)
├── User management table
└── Quick action buttons

/admin/recommendations          📋 All Recommendations
├── Search by student/major/email
├── Filter by school
├── Paginated table (20 per page)
└── View/Delete actions

/admin/recommendation/<id>      📄 Recommendation Details
├── Full recommendation info
├── Student information
├── Confidence bar chart
└── Delete option

/admin/user/<id>/history        👤 Student History
├── Student info card
├── All their recommendations
└── Timeline view

/admin/analytics                📈 Analytics & Insights
├── Key metrics (4 cards)
├── Top 10 majors chart
├── School distribution table
├── Average confidence analysis
└── Weekly trends

/admin/export-data              💾 Export Data
├── Download as CSV button
├── Preview of CSV data
└── Column information

/admin/export-csv               📥 CSV Download
└── Direct file download
```

---

## 🎯 Common Admin Tasks

### 🔍 Find a Student's Recommendations

**Path 1 (Quick)**
1. Go to `/admin/recommendations`
2. Type student name in search
3. Press Search
4. ✅ See all their recommendations

**Path 2 (Detailed)**
1. Go to `/admin`
2. Find student in user table
3. Click "History"
4. ✅ See all their recommendations

---

### 👁️ View Recommendation Details

1. Go to `/admin/recommendations`
2. Click "View" on any row
3. ✅ See full details with confidence chart

---

### 🗑️ Delete a Recommendation

1. Go to `/admin/recommendations`
2. Click "Delete" on any row
3. ✅ Confirm deletion
4. Recommendation removed from system

---

### 🔑 Make Someone an Admin

1. Go to `/admin`
2. Find user in table
3. Click "Make Admin"
4. ✅ User is now admin

---

### 👥 Delete a User Account

1. Go to `/admin`
2. Find user in table
3. Click "Delete"
4. ✅ User and all their recommendations deleted

---

### 📊 View Analytics

1. Go to `/admin/analytics`
2. ✅ See all insights:
   - Top majors
   - School distribution
   - Confidence scores
   - Weekly trends

---

### 📥 Export All Data

1. Go to `/admin/export-data`
2. Click "📥 Download as CSV"
3. ✅ File downloads to computer
4. Open in Excel/Google Sheets/Python

---

## 🎨 Dashboard Features at a Glance

### Main Dashboard (`/admin`)
| Feature | Details |
|---------|---------|
| Stats Cards | 4 key metrics |
| Recent Feed | Last 5 recommendations |
| User Table | All users with actions |
| Quick Links | Fast jump to other pages |

### Recommendations (`/admin/recommendations`)
| Feature | Details |
|---------|---------|
| Search | Student, email, major |
| Filter | By school/faculty |
| Table | 20 rows per page |
| Actions | View, Delete |

### Analytics (`/admin/analytics`)
| Feature | Details |
|---------|---------|
| Metrics | 4 key stat cards |
| Charts | Top majors, confidence |
| Tables | By school distribution |
| Stats | Weekly, per-user averages |

### Export (`/admin/export-data`)
| Feature | Details |
|---------|---------|
| Download | CSV format |
| Preview | First 1000 chars |
| Columns | 8 data fields |
| Use | Excel, Python, analysis |

---

## 🔒 Permissions

### What You Need
✅ Logged in  
✅ Is admin account  

### What You CAN'T Do
❌ Access admin if not logged in → Redirected to login  
❌ Access admin if not admin → Redirected to home  
❌ Delete own account → System prevents this  
❌ Change own admin status → Disabled in UI  

---

## 💡 Pro Tips

### 1️⃣ Find Problems Fast
- Go to analytics
- Check "average confidence by major"
- Ones < 75% might have issues

### 2️⃣ Monitor Activity
- Check dashboard daily
- Review recent recommendations
- Look for unusual patterns

### 3️⃣ Backup Before Deletes
- Export data before deleting users
- Keep monthly backups of recommendations
- CSV file is your backup

### 4️⃣ Use Search Wisely
- Partial names work: "john" finds "johnny", "john"
- Emails work: "gmail" finds all gmail users
- Majors work: "Computer" finds "Applied Computer Technology", etc.

### 5️⃣ Analyze Trends
- Export monthly
- Look for seasonal patterns
- Track top majors over time
- Monitor confidence scores

---

## ⚠️ Important Notes

### Destructive Actions
- Delete user → Removes user + all recommendations
- Delete recommendation → Cannot be undone
- Both require confirmation
- No automatic backups (except CSV)

### Data Sources
- **Database**: User accounts + recommendations
- **CSV**: Input data + analytics
- Delete from DB = Delete manually from CSV if needed

### Performance
- Large exports take few seconds
- Tables paginated (20 per page)
- Analytics computed on request
- Queries optimized for speed

---

## 🆘 If Something Goes Wrong

### Can't Access Admin
- ✅ Check: Are you logged in?
- ✅ Check: Is your account marked as admin?
- ✅ Solution: Ask another admin to promote you

### Data Missing
- ✅ Check: Refresh page
- ✅ Check: Clear browser cache
- ✅ Check: Search/filter not hiding it

### Can't Delete
- ✅ Check: Confirmation dialog appeared?
- ✅ Check: User still in table?
- ✅ Solution: Try again or contact developer

### Export Not Working
- ✅ Check: Browser download folder
- ✅ Check: Browser pop-up blocker
- ✅ Solution: Try different browser

---

## 📱 Mobile Access

✅ Dashboard works on phone  
✅ Tables horizontally scrollable  
✅ Buttons touch-friendly  
✅ Navigation still works  

**Best on**: Desktop or tablet with keyboard/mouse

---

## 🎯 Admin Dashboard Capabilities

| Category | Capability | Status |
|----------|-----------|--------|
| **View** | All recommendations | ✅ |
| **View** | All users | ✅ |
| **View** | Student histories | ✅ |
| **Search** | By student name | ✅ |
| **Search** | By email | ✅ |
| **Search** | By major | ✅ |
| **Filter** | By school | ✅ |
| **Sort** | By date | ✅ |
| **Paginate** | 20 per page | ✅ |
| **Delete** | Recommendations | ✅ |
| **Delete** | Users | ✅ |
| **Promote** | Student to admin | ✅ |
| **Demote** | Admin to student | ✅ |
| **Analyze** | Top majors | ✅ |
| **Analyze** | By school | ✅ |
| **Analyze** | Confidence scores | ✅ |
| **Analyze** | Weekly trends | ✅ |
| **Export** | As CSV | ✅ |
| **Chart** | Bar charts | ✅ |
| **Chart** | Tables | ✅ |
| **Chart** | Progress bars | ✅ |

---

## 🚀 Getting Started

### First Time Admin?

1. **Login** to your admin account
2. **Visit** `/admin` (main dashboard)
3. **Review** recent recommendations
4. **Check** analytics at `/admin/analytics`
5. **Explore** `/admin/recommendations` to search
6. **Download** data from `/admin/export-data`

That's it! You're ready to manage everything! 🎉

---

## 📞 Need Help?

- Check the detailed guide: `ADMIN_DASHBOARD_GUIDE.md`
- Report issues to developer
- Backup data before major actions
- Test features on staging first

---

**Admin Dashboard v2.0** | March 2026 | Ready to Use ✅
