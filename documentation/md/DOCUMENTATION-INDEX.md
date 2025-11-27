# REF-Manager Documentation Index

## Complete Documentation Guide for v3.0

---

## Document Overview

| Document | Description | Audience | Time |
|----------|-------------|----------|------|
| [README](README.md) | System overview | Everyone | 20 min |
| [Quick Start Guide](QUICK-START-GUIDE.md) | Get running fast | New users | 15 min |
| [User Guide](USER-GUIDE.md) | Complete user docs | All users | 60 min |
| [Technical Documentation](TECHNICAL-DOCUMENTATION.md) | Developer reference | Developers, Admins | 45 min |
| [Troubleshooting](TROUBLESHOOTING.md) | Problem solving | Everyone | As needed |
| [Changelog](CHANGELOG.md) | Version history | Everyone | 10 min |

---

## Reading Paths

### New Users
1. **Quick Start Guide** (15 min) - Get running
2. **User Guide** sections 1-4 (30 min) - Basic features
3. **User Guide** remaining sections - As needed

### Department Coordinators
1. **Quick Start Guide** - Installation
2. **User Guide** - Complete guide
3. **Troubleshooting** - Reference

### System Administrators
1. **Technical Documentation** - Full guide
2. **README** - Overview
3. **Troubleshooting** - Reference

### Developers
1. **README** - Overview
2. **Technical Documentation** - Full reference
3. **Changelog** - Version history

### Upgrading from v2.x
1. **Changelog** - What's new
2. **Technical Documentation** - Migration steps
3. **User Guide** - New features

---

## Quick Reference

### Essential Commands

```bash
# Start server
python manage.py runserver

# Create admin
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Setup roles
python manage.py setup_roles --create-profiles --superusers-admin

# Assign roles
python manage.py assign_roles username --add ADMIN
```

### Key URLs

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/admin/` | Django Admin |
| `/colleagues/` | Colleague management |
| `/outputs/` | Output management |
| `/reports/` | Reports and exports |

### User Roles

| Role | Access Level |
|------|--------------|
| Administrator | Full access |
| Observer | Read-only |
| Internal Panel | Review assigned |
| Colleague | Own outputs |

---

## Document Summaries

### README.md
**Purpose:** Main overview of REF-Manager

**Contents:**
- System overview
- Feature summary
- Requirements
- Quick installation
- Configuration basics

**Use when:** First exploring REF-Manager or need quick reference

---

### QUICK-START-GUIDE.md
**Purpose:** Fastest path to running system

**Contents:**
- 5-step installation
- First steps
- Essential commands
- Quick tips

**Use when:** Want to start immediately

---

### USER-GUIDE.md
**Purpose:** Complete user documentation

**Contents:**
- All features explained
- Step-by-step instructions
- Best practices
- Tips and tricks

**Use when:** Learning features or need detailed guidance

---

### TECHNICAL-DOCUMENTATION.md
**Purpose:** Developer and admin reference

**Contents:**
- Architecture overview
- Database schema
- Configuration reference
- API documentation
- Deployment guide
- Security settings

**Use when:** Developing, customising, or deploying

---

### TROUBLESHOOTING.md
**Purpose:** Solve common problems

**Contents:**
- Installation issues
- Permission problems
- Database errors
- Performance tips
- Error messages

**Use when:** Something isn't working

---

### CHANGELOG.md
**Purpose:** Track version changes

**Contents:**
- Version history
- New features
- Breaking changes
- Upgrade guides
- Roadmap

**Use when:** Upgrading or checking what's new

---

## Available Formats

Documentation is available in three formats:

| Format | Location | Use Case |
|--------|----------|----------|
| Markdown | `documentation/md/` | Reading, editing |
| LaTeX | `documentation/latex/` | Professional printing |
| PDF | `documentation/pdf/` | Distribution, offline |

---

## Getting Help

### Self-Help Resources
1. Check this index
2. Read relevant documentation
3. Search Troubleshooting guide

### Contact
- **Email:** george.tsoulas@york.ac.uk
- **GitHub Issues:** https://github.com/gtsoulas/ref-manager/issues

### Reporting Issues
Include:
1. What you were trying to do
2. What happened
3. Error messages
4. System information

---

## Documentation Version

- **Version:** 3.0.0
- **Date:** November 2024
- **Application Version:** 3.0.0
