# REF-Manager v4.0

## Research Excellence Framework Submission Management System

**Version 4.0.0 "REF 2029 Ready"** | December 2025  
**Author**: George Tsoulas  
**Developed for**: University of York, Department of Language and Linguistic Science  
**License**: GNU General Public License v3.0

---

## Overview

REF-Manager is a comprehensive web-based application designed to help UK university departments manage their Research Excellence Framework (REF) submissions. The system provides tools for tracking research outputs, coordinating quality assessments, managing internal and external reviews, and optimising submission portfolios for REF 2029.

### What's New in v4.0

- **O/S/R Rating System**: Three-component quality ratings (Originality, Significance, Rigour) on 0.00-4.00 scale
- **DOI Auto-Fetch**: Automatic metadata population from OpenAlex API
- **Enhanced Bulk Import**: Hybrid/Smart/Manual import modes with duplicate detection
- **OA Compliance Tracking**: Automated 3-month deposit rule verification
- **REF Narrative Statements**: Double-weighting and interdisciplinary statement support

### Key Capabilities

- **Research Output Management**: Track publications, books, conference papers, and other research outputs with comprehensive metadata
- **Three-Component Quality Assessment**: O/S/R ratings from internal panel, external critical friends, and self-assessment
- **Risk Assessment Framework**: Evaluate content risk, timeline risk, and Open Access compliance for each output
- **Portfolio Optimisation**: Model different submission scenarios with quality, risk, and representativeness metrics
- **Role-Based Access Control**: Four distinct user roles with granular permissions
- **Comprehensive Reporting**: Excel exports, LaTeX report generation, and interactive dashboards

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10 or higher |
| Django | 4.2.x |
| Database | SQLite (development) or PostgreSQL 14+ (production) |
| Memory | 2 GB RAM minimum |
| Storage | 1 GB free space |

### Recommended for Production

| Component | Recommendation |
|-----------|----------------|
| Python | 3.12 |
| Database | PostgreSQL 15 |
| Memory | 4 GB RAM |
| Web Server | Nginx + Gunicorn |
| SSL | TLS 1.2 or higher |

---

## Features Summary

### 1. Colleague Management
- Personal and employment details tracking
- Multiple colleague categories (Independent, Non-Independent, Postdoc, etc.)
- Employment status tracking (Current/Former)
- FTE-based output requirements calculation

### 2. Research Output Management
- Multiple publication types support
- DOI auto-fetch with OpenAlex integration
- BibTeX and CSV import (including enhanced bulk import)
- Complete bibliographic metadata
- File attachment support
- Status workflow tracking

### 3. O/S/R Quality Assessment (NEW in v4.0)
- Three-component ratings: Originality, Significance, Rigour
- Decimal scale 0.00-4.00 mapping to REF star ratings
- Internal Panel, Critical Friend, and Self-Assessment sources
- Automatic average calculation across sources

### 4. Open Access Compliance (NEW in v4.0)
- Acceptance date, deposit date, embargo tracking
- Automatic 3-month deposit rule verification
- OA status classification (Gold, Green, Hybrid, Bronze, Closed)
- Exception recording for non-compliant outputs

### 5. REF Narrative Statements (NEW in v4.0)
- Double-weighting statement (300 words)
- Interdisciplinary statement (500 words)
- Real-time word counting with validation

### 6. Risk Assessment Framework
- Content risk scoring
- Timeline risk scoring
- Open Access compliance tracking
- Configurable risk weights

### 7. Portfolio Optimisation
- Submission scenario modelling
- Quality and risk metrics
- Representativeness scoring
- Equality and diversity metrics

### 8. Role-Based Access Control
- Administrator, Observer, Internal Panel, Colleague roles
- Multi-role support
- Granular permissions

### 9. Import & Export
- CSV and BibTeX import
- Enhanced bulk import with DOI lookup
- Excel and CSV export
- LaTeX report generation

---

## Quick Installation

```bash
# Clone and setup
git clone https://github.com/gtsoulas/ref-manager.git
cd ref-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install requests for DOI auto-fetch
pip install requests

# Configure
cp env.example .env
# Edit .env with your settings

# Initialise
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_roles --create-profiles --superusers-admin
python manage.py runserver
```

Visit http://localhost:8000 to access REF-Manager.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](QUICK-START-GUIDE.md) | Get running in 15 minutes |
| [User Guide](USER-GUIDE.md) | Complete user documentation |
| [Technical Documentation](TECHNICAL-DOCUMENTATION.md) | Developer and admin reference |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| [Changelog](CHANGELOG.md) | Version history |

---

## Support

- **Author**: George Tsoulas
- **Email**: george.tsoulas@york.ac.uk
- **GitHub**: https://github.com/gtsoulas/ref-manager

---

## License

GNU General Public License v3.0
