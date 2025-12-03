# REF-Manager Documentation Index

## Version 4.0.0 "REF 2029 Ready"

**Author**: George Tsoulas  
**Institution**: University of York, Department of Language and Linguistic Science  
**Release Date**: December 2025

---

## Available Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [README](README.md) | Overview and quick start | Everyone |
| [Quick Start Guide](QUICK-START-GUIDE.md) | 15-minute setup guide | New users |
| [User Guide](USER-GUIDE.md) | Complete feature documentation | All users |
| [Technical Documentation](TECHNICAL-DOCUMENTATION.md) | Deployment and development | Administrators, Developers |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions | All users |
| [Changelog](CHANGELOG.md) | Version history | All users |

---

## Document Formats

All documentation is available in three formats:

| Format | Location | Use Case |
|--------|----------|----------|
| Markdown (.md) | `documentation/md/` | Online viewing, GitHub |
| LaTeX (.tex) | `documentation/latex/` | Professional printing |
| PDF (.pdf) | `documentation/pdf/` | Distribution, offline reading |

---

## Quick Links by Topic

### Getting Started
- [Installation](README.md#quick-installation)
- [Quick Start Guide](QUICK-START-GUIDE.md)
- [First Steps](QUICK-START-GUIDE.md#step-5-first-steps)

### New Features in v4.0
- [O/S/R Ratings](USER-GUIDE.md#6-osr-quality-ratings)
- [DOI Auto-Fetch](USER-GUIDE.md#5-doi-auto-fetch)
- [Bulk Import](USER-GUIDE.md#12-bulk-import)
- [OA Compliance](USER-GUIDE.md#7-open-access-compliance)
- [Narrative Statements](USER-GUIDE.md#8-ref-narrative-statements)

### Day-to-Day Usage
- [Managing Outputs](USER-GUIDE.md#4-managing-outputs)
- [Quality Assessment](USER-GUIDE.md#6-osr-quality-ratings)
- [Risk Assessment](USER-GUIDE.md#9-risk-assessment)
- [Reports & Export](USER-GUIDE.md#15-reports--export)

### Administration
- [Server Deployment](TECHNICAL-DOCUMENTATION.md#3-server-deployment)
- [Database Configuration](TECHNICAL-DOCUMENTATION.md#4-database-schema)
- [User Management](USER-GUIDE.md#16-user-management)
- [Backup & Recovery](TECHNICAL-DOCUMENTATION.md#8-backup--recovery)

### Troubleshooting
- [Installation Issues](TROUBLESHOOTING.md#1-installation-issues)
- [Database Issues](TROUBLESHOOTING.md#2-database-issues)
- [DOI Fetch Issues](TROUBLESHOOTING.md#3-doi-auto-fetch-issues)
- [Server Issues](TROUBLESHOOTING.md#6-server-deployment-issues)

---

## Version Information

| Version | Release Date | Status |
|---------|--------------|--------|
| 4.0.0 | December 2025 | Current |
| 3.1.0 | November 2025 | Legacy |
| 3.0.0 | October 2025 | Legacy |
| 2.0.0 | August 2025 | Deprecated |
| 1.0.0 | June 2025 | Deprecated |

---

## Building Documentation

To rebuild PDF documentation from LaTeX sources:

```bash
cd documentation
./build_docs.sh
```

Or manually:

```bash
cd documentation/latex
pdflatex README.tex
pdflatex USER-GUIDE.tex
# etc.
```

---

## Contact

- **Author**: George Tsoulas
- **Email**: george.tsoulas@york.ac.uk
- **GitHub**: https://github.com/gtsoulas/ref-manager

---

## License

This documentation is part of REF-Manager, released under GNU General Public License v3.0.
