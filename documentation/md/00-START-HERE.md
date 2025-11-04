# 🚀 START HERE - REF Manager v2.0

**Quick Overview and Navigation Guide**

---

## What is REF Manager?

REF Manager v2.0 is a comprehensive web application for managing Research Excellence Framework (REF) submissions at UK academic institutions. It helps you track research outputs, manage staff, coordinate reviews, and generate professional reports.

---

## 🆕 What's New in Version 2.0?

✅ **Employment Status Tracking** - Current vs Former staff  
✅ **Enhanced Categories** - 9 colleague types including non-independent researchers  
✅ **Internal Panel System** - Complete internal review management  
✅ **Task Management** - Track all REF activities with priorities and deadlines  
✅ **CSV Import** - Bulk import for outputs and colleagues  
✅ **Excel Export** - Export assignments with clickable PDF links  
✅ **Request Enhancements** - Mark as completed and delete with confirmation  
✅ **Dashboard Updates** - New widgets for Internal Panel and Tasks  

---

## 📚 Where to Start?

### For New Users

**1. First Time Setup (10 minutes)**
→ Read: **QUICK-START-GUIDE.md**
- Installation in 6 steps
- Create your first colleague and output
- Try new v2.0 features

**2. Learn the System**
→ Read: **USER-GUIDE.md** (sections as needed)
- Dashboard overview
- Feature-by-feature guide
- Best practices
- FAQ

**3. If You Get Stuck**
→ Read: **TROUBLESHOOTING.md**
- Common issues and fixes
- Quick problem finder
- Error message index

### For Administrators

**1. Installation and Deployment**
→ Read: **REF-MANAGER-README.md**
- Complete system documentation
- Installation guide
- Production deployment
- Maintenance procedures

**2. Technical Details**
→ Read: **TECHNICAL-DOCUMENTATION.md**
- Architecture overview
- Database models
- API reference
- Development guide

**3. Building Documentation PDFs**
→ Read: **README-TOOLS.md**
- Documentation build process
- Using build_docs.sh script
- PDF generation

### Learning About Changes

**What Changed in v2.0?**
→ Read: **CHANGELOG.md**
- Complete version history
- All v2.0 additions
- Upgrade notes
- Migration guide

---

## 📖 Documentation Suite

| Document | Purpose | Length | Read When |
|----------|---------|--------|-----------|
| **THIS FILE** | Overview & navigation | 5 min | Start here! |
| **QUICK-START-GUIDE.md** | Fast installation | 15 pages | First install |
| **USER-GUIDE.md** | Complete feature guide | 50 pages | Daily reference |
| **REF-MANAGER-README.md** | System documentation | 60 pages | Installation & admin |
| **TECHNICAL-DOCUMENTATION.md** | Developer reference | 35 pages | Development |
| **TROUBLESHOOTING.md** | Problem solving | 15 pages | When stuck |
| **CHANGELOG.md** | Version history | 10 pages | Upgrade planning |
| **DOCUMENTATION-INDEX.md** | Doc navigation | 5 pages | Find info |
| **README-TOOLS.md** | Build instructions | 5 pages | Generate PDFs |

**Total:** ~155 pages of comprehensive documentation

---

## ⚡ Quick Start (Really Quick!)

### 1. Install (10 minutes)

```bash
# Create project directory
mkdir -p ~/ref-project-app
cd ~/ref-project-app

# Get the code (git clone or extract ZIP)
git clone [repository] ref-manager
cd ref-manager

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add SECRET_KEY

# Initialize database
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 2. First Login

1. Go to http://localhost:8000
2. Log in with superuser credentials
3. Explore the dashboard

### 3. Try v2.0 Features

**Add a colleague with new categories:**
- Colleagues → Add Colleague
- Set Employment Status: Current
- Choose Category: Non-Independent Researcher (for post-docs!)

**Create a task:**
- Tasks → Create Task
- Set priority and due date
- Track your REF activities

**Import outputs:**
- Outputs → Import
- Download template
- Upload CSV file

**Export with links:**
- Export → Assignments
- Choose filters
- Export to Excel with clickable PDF links

---

## 🎯 Common Tasks → Quick Guide

| Task | Where to Look |
|------|---------------|
| Install system | QUICK-START-GUIDE.md |
| Add colleague | USER-GUIDE.md → Colleague Management |
| Add output | USER-GUIDE.md → Output Management |
| Import data | USER-GUIDE.md → Data Import/Export |
| Set up Internal Panel | USER-GUIDE.md → Internal Panel System |
| Create tasks | USER-GUIDE.md → Task Management |
| Export assignments | USER-GUIDE.md → Data Import/Export |
| Generate reports | USER-GUIDE.md → Report Generation |
| Fix errors | TROUBLESHOOTING.md |
| Deploy to production | REF-MANAGER-README.md → Production Deployment |
| Understand changes | CHANGELOG.md |
| Build PDFs | README-TOOLS.md |

---

## 🔍 Finding Information

### By Question Type

**"How do I...?"**
→ USER-GUIDE.md (feature-specific sections)

**"What is...?"**
→ REF-MANAGER-README.md (Features section)

**"Why isn't it working?"**
→ TROUBLESHOOTING.md

**"What changed?"**
→ CHANGELOG.md

**"How does it work technically?"**
→ TECHNICAL-DOCUMENTATION.md

### By User Role

**REF Coordinator:**
- QUICK-START-GUIDE.md (setup)
- USER-GUIDE.md (daily use)
- DOCUMENTATION-INDEX.md (navigation)

**Department Administrator:**
- REF-MANAGER-README.md (full system)
- USER-GUIDE.md (features)
- TROUBLESHOOTING.md (support)

**System Administrator:**
- REF-MANAGER-README.md (deployment)
- TECHNICAL-DOCUMENTATION.md (architecture)
- TROUBLESHOOTING.md (maintenance)

**Developer:**
- TECHNICAL-DOCUMENTATION.md (development)
- CHANGELOG.md (version history)
- README-TOOLS.md (build process)

---

## 💡 Pro Tips

1. **Read the Quick Start first** - Even if you're experienced, it's only 10 minutes
2. **Use the User Guide as reference** - Don't try to read it all at once
3. **Bookmark Troubleshooting** - You'll need it eventually
4. **Check the FAQ** - USER-GUIDE.md has extensive FAQ section
5. **Build PDFs** - Easier to share and read offline (see README-TOOLS.md)
6. **Index is your friend** - DOCUMENTATION-INDEX.md helps navigate

---

## 🚦 3-Step Recommendation

### Step 1: Quick Start (20 minutes)
1. Read QUICK-START-GUIDE.md (10 min)
2. Install and run (10 min)
3. Log in and explore dashboard

### Step 2: Learn Features (1 hour)
1. USER-GUIDE.md → Dashboard Overview (10 min)
2. USER-GUIDE.md → Colleague Management (15 min)
3. USER-GUIDE.md → Output Management (15 min)
4. USER-GUIDE.md → v2.0 New Features (20 min)

### Step 3: Master the System (ongoing)
- Use USER-GUIDE.md as daily reference
- Check TROUBLESHOOTING.md when stuck
- Read CHANGELOG.md for updates
- Explore TECHNICAL-DOCUMENTATION.md for deep understanding

---

## 📞 Need Help?

**Can't find what you need?**
1. Check DOCUMENTATION-INDEX.md for navigation
2. Use Ctrl+F to search in documents
3. Check USER-GUIDE.md → FAQ section
4. Look in TROUBLESHOOTING.md
5. Contact system administrator

**Found an error in documentation?**
- Note document name and section
- Email details to maintainer
- Help improve for everyone!

---

## ✅ Quick Checklist

**Before you start:**
- [ ] Have Python 3.10+ installed
- [ ] Have 500MB free disk space
- [ ] Have internet connection
- [ ] Know your role (coordinator/admin/user)

**After installation:**
- [ ] Can log in successfully
- [ ] Dashboard displays correctly
- [ ] Added first colleague
- [ ] Added first output
- [ ] Tried v2.0 features

**For daily use:**
- [ ] Bookmarked USER-GUIDE.md
- [ ] Know how to find information
- [ ] Comfortable with basic features
- [ ] Know where to get help

---

## 🎓 Learning Path

**Day 1:** Installation + Quick Start
- Install system (QUICK-START-GUIDE.md)
- Explore dashboard
- Add test data

**Day 2:** Core Features
- Colleague management (USER-GUIDE.md)
- Output management (USER-GUIDE.md)
- Dashboard widgets

**Day 3:** v2.0 Features
- Employment status tracking
- Colleague categories
- Internal Panel system
- Task management

**Day 4:** Advanced Features
- CSV import
- Excel export
- Request management
- Report generation

**Day 5:** Administration
- Production deployment (if needed)
- Backup procedures
- Troubleshooting
- Performance optimization

---

## 🗺️ Documentation Map

```
START HERE (this file)
    ↓
┌───────────────────────────────────────────┐
│                                           │
│  New User?                System Admin?  │
│     ↓                          ↓          │
│  QUICK-START              README.md       │
│     ↓                          ↓          │
│  USER-GUIDE           TECHNICAL-DOCS     │
│     ↓                          ↓          │
│  Daily Use              Deployment        │
│                                           │
└───────────────────────────────────────────┘
               ↓
         Need Help?
               ↓
        TROUBLESHOOTING
               ↓
        Still Stuck?
               ↓
    Contact Administrator
```

---

## 📋 Version Information

**Current Version:** 2.0.0  
**Release Date:** November 3, 2025  
**Documentation Updated:** November 3, 2025

**What's in v2.0:**
- Employment status tracking
- 9 colleague categories
- Internal Panel system
- Task management
- CSV import
- Excel export with links
- Enhanced requests
- Dashboard improvements

**Upgrading from v1.0?**
→ See CHANGELOG.md for migration guide

---

## 🎯 Your Next Step

**Choose your path:**

**→ I'm brand new**
Read QUICK-START-GUIDE.md next

**→ I'm upgrading**
Read CHANGELOG.md next

**→ I want technical details**
Read TECHNICAL-DOCUMENTATION.md next

**→ I'm having problems**
Read TROUBLESHOOTING.md next

**→ I want to explore**
Read USER-GUIDE.md next

---

**Welcome to REF Manager v2.0!**

We've built comprehensive documentation to help you succeed. Start with the Quick Start Guide, use the User Guide as your daily reference, and don't hesitate to check the Troubleshooting Guide when needed.

**Questions?** Check DOCUMENTATION-INDEX.md for complete navigation.

**Ready?** Let's get started with QUICK-START-GUIDE.md!

---

**Prepared by:** George Tsoulas  
**Institution:** University of York  
**For:** REF Manager v2.0 Users

**Good luck with your REF submission! 🚀**
