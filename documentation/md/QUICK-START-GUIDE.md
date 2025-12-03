# REF-Manager Quick Start Guide

## Get Running in 15 Minutes

**Version 4.0.0** | December 2025

---

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher installed
- Git installed
- Terminal/command line access

---

## Step 1: Download and Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/gtsoulas/ref-manager.git
cd ref-manager

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate   # Linux/Mac
# or: venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install requests  # For DOI auto-fetch
```

---

## Step 2: Configure (2 minutes)

```bash
# Copy example configuration
cp env.example .env

# Edit .env file (optional for development)
# nano .env  or open in your editor
```

For development, the defaults work fine. For production, set:
- `DEBUG=False`
- `SECRET_KEY=your-secure-key`
- `ALLOWED_HOSTS=your-domain.ac.uk`

---

## Step 3: Initialise Database (3 minutes)

```bash
# Create database tables
python manage.py migrate

# Create admin account
python manage.py createsuperuser
# Enter: username, email, password

# Setup user roles
python manage.py setup_roles --create-profiles --superusers-admin
```

---

## Step 4: Start the Server (1 minute)

```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

Login with your superuser credentials.

---

## Step 5: First Steps (4 minutes)

### Add a Colleague

1. Navigate to **Colleagues → Add Colleague**
2. Enter details:
   - Staff ID, Name, FTE
   - Category, Unit of Assessment
3. Click **Save**

### Add an Output with DOI Auto-Fetch (NEW in v4.0)

1. Navigate to **Outputs → Add Output**
2. In the **Intelligent Output Entry** section:
   - Paste a DOI (e.g., `10.1038/nature12373`)
   - Click **Auto-Fill**
3. Review populated fields
4. Select the Colleague
5. Add O/S/R self-assessment ratings (0.00-4.00):
   - Originality
   - Significance
   - Rigour
6. Click **Save**

### Enter Quality Ratings

1. Edit an output
2. Scroll to **Quality Ratings (O/S/R)** section
3. Enter ratings from any source:
   - **Internal Panel** (blue card)
   - **Critical Friend** (yellow card)
   - **Self-Assessment** (green card)
4. Each source has three components: Originality, Significance, Rigour
5. Save

---

## O/S/R Rating Scale

| Score Range | Star Rating | Description |
|-------------|-------------|-------------|
| 3.50 - 4.00 | 4★ | World-leading |
| 2.50 - 3.49 | 3★ | Internationally excellent |
| 1.50 - 2.49 | 2★ | Internationally recognised |
| 0.50 - 1.49 | 1★ | Nationally recognised |
| 0.00 - 0.49 | U | Unclassified |

---

## What's Next?

- **[User Guide](USER-GUIDE.md)**: Complete feature documentation
- **[Technical Documentation](TECHNICAL-DOCUMENTATION.md)**: Server deployment
- **[Troubleshooting](TROUBLESHOOTING.md)**: Common issues

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start server | `python manage.py runserver` |
| Create migration | `python manage.py makemigrations` |
| Apply migrations | `python manage.py migrate` |
| Create admin | `python manage.py createsuperuser` |
| Collect static | `python manage.py collectstatic` |
| Run tests | `python manage.py test` |

---

## Need Help?

- **Email**: george.tsoulas@york.ac.uk
- **GitHub**: https://github.com/gtsoulas/ref-manager
