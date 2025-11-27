# REF-Manager Quick Start Guide

## Get Running in 15 Minutes

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional)

**Verify Python:**
```bash
python3 --version
```

---

## Step 1: Get the Code

```bash
git clone https://github.com/gtsoulas/ref-manager.git
cd ref-manager
```

---

## Step 2: Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Configure

```bash
# Copy example config
cp env.example .env

# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env` and add your secret key.

---

## Step 4: Initialise Database

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Set up roles
python manage.py setup_roles --create-profiles --superusers-admin
```

---

## Step 5: Launch

```bash
python manage.py runserver
```

Open http://localhost:8000 in your browser.

---

## First Steps

### Add a Colleague
1. Navigate to **Colleagues → Add Colleague**
2. Enter staff details
3. Save

### Add an Output
1. Navigate to **Outputs → Add Output**
2. Select colleague and enter publication details
3. Save

### Assign for Review
1. Open an output
2. Click **Assign Internal Panel** or **Assign Critical Friend**
3. Select reviewer and save

---

## Essential Commands

| Task | Command |
|------|---------|
| Start server | `python manage.py runserver` |
| Create admin | `python manage.py createsuperuser` |
| Run migrations | `python manage.py migrate` |
| List users/roles | `python manage.py assign_roles --list` |
| Assign role | `python manage.py assign_roles username --add ADMIN` |

---

## Quick Fixes

**Port in use:**
```bash
python manage.py runserver 8080
```

**Module not found:**
```bash
source venv/bin/activate
```

**Roles missing:**
```bash
python manage.py setup_roles
```

---

## Next Steps

- Read the [User Guide](USER-GUIDE.md) for detailed features
- Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
- See [Technical Documentation](TECHNICAL-DOCUMENTATION.md) for advanced configuration
