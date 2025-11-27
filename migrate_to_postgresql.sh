#!/bin/bash

# REF-Manager PostgreSQL Migration Script
# Migrates from SQLite to PostgreSQL for multi-user support

set -e  # Exit on any error

echo "=========================================="
echo "REF-Manager PostgreSQL Migration"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="ref_manager_db"
DB_USER="ref_manager_user"
DB_PASSWORD=""
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ ERROR: Not in REF-manager root directory${NC}"
    echo "Please run this from: ~/REF-Stuff/ref-manager/"
    exit 1
fi

echo -e "${GREEN}✅ Found REF-manager project${NC}"
echo ""

# Step 1: Get database password
echo "=========================================="
echo "Step 1: Database Configuration"
echo "=========================================="
echo ""
echo "Enter a secure password for PostgreSQL database user:"
read -s DB_PASSWORD
echo ""
echo "Confirm password:"
read -s DB_PASSWORD_CONFIRM
echo ""

if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
    echo -e "${RED}❌ Passwords don't match. Exiting.${NC}"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ Password cannot be empty. Exiting.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Password set${NC}"
echo ""

# Step 2: Check PostgreSQL installation
echo "=========================================="
echo "Step 2: PostgreSQL Installation Check"
echo "=========================================="
echo ""

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Installing...${NC}"
    echo ""
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib libpq-dev
    echo -e "${GREEN}✅ PostgreSQL installed${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL already installed${NC}"
fi
echo ""

# Check if PostgreSQL service is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    echo -e "${GREEN}✅ PostgreSQL service started${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
fi
echo ""

# Step 3: Install Python PostgreSQL adapter
echo "=========================================="
echo "Step 3: Python PostgreSQL Adapter"
echo "=========================================="
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
fi
echo ""

echo "Installing psycopg2-binary..."
pip install psycopg2-binary
echo -e "${GREEN}✅ psycopg2-binary installed${NC}"
echo ""

# Step 4: Create PostgreSQL database and user
echo "=========================================="
echo "Step 4: Database Creation"
echo "=========================================="
echo ""

# Drop database if it exists (for clean migration)
echo "Checking for existing database..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}⚠️  Database $DB_NAME already exists${NC}"
    echo "Do you want to drop it and create fresh? (yes/no)"
    read -r RESPONSE
    if [ "$RESPONSE" = "yes" ]; then
        echo "Dropping existing database..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
        sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;"
        echo -e "${GREEN}✅ Existing database dropped${NC}"
    else
        echo -e "${RED}❌ Migration cancelled${NC}"
        exit 1
    fi
fi

echo "Creating PostgreSQL database and user..."
sudo -u postgres psql <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

echo -e "${GREEN}✅ Database and user created${NC}"
echo ""

# Step 5: Backup SQLite database
echo "=========================================="
echo "Step 5: SQLite Data Backup"
echo "=========================================="
echo ""

mkdir -p $BACKUP_DIR

echo "Creating backup of SQLite database..."
cp db.sqlite3 "$BACKUP_DIR/db.sqlite3.$TIMESTAMP"
echo -e "${GREEN}✅ SQLite database backed up to: $BACKUP_DIR/db.sqlite3.$TIMESTAMP${NC}"
echo ""

echo "Exporting data from SQLite..."
python manage.py dumpdata --natural-foreign --natural-primary \
    -e contenttypes -e auth.Permission \
    --indent 2 > "$BACKUP_DIR/data_export_$TIMESTAMP.json"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Data exported to: $BACKUP_DIR/data_export_$TIMESTAMP.json${NC}"
else
    echo -e "${RED}❌ Data export failed${NC}"
    exit 1
fi
echo ""

# Step 6: Update Django settings
echo "=========================================="
echo "Step 6: Django Settings Update"
echo "=========================================="
echo ""

SETTINGS_FILE="config/settings.py"

# Backup settings
cp $SETTINGS_FILE "$SETTINGS_FILE.backup_$TIMESTAMP"
echo -e "${GREEN}✅ Settings backed up to: $SETTINGS_FILE.backup_$TIMESTAMP${NC}"
echo ""

# Check if PostgreSQL settings already exist
if grep -q "django.db.backends.postgresql" $SETTINGS_FILE; then
    echo -e "${YELLOW}⚠️  PostgreSQL configuration already exists in settings${NC}"
else
    echo "Updating database configuration..."
    
    # Create new database configuration
    cat > /tmp/postgres_db_config.txt <<EOF

# PostgreSQL Database Configuration (migrated on $TIMESTAMP)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '$DB_NAME',
        'USER': '$DB_USER',
        'PASSWORD': '$DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# SQLite backup (commented out)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
EOF

    # Find and replace DATABASES configuration
    python3 << 'PYTHON_EOF'
import re

with open('config/settings.py', 'r') as f:
    content = f.read()

# Find the DATABASES section and replace it
pattern = r"DATABASES\s*=\s*\{[^}]*\{[^}]*\}[^}]*\}"
with open('/tmp/postgres_db_config.txt', 'r') as f:
    replacement = f.read()

new_content = re.sub(pattern, replacement, content, count=1)

with open('config/settings.py', 'w') as f:
    f.write(new_content)

print("Database configuration updated")
PYTHON_EOF

    echo -e "${GREEN}✅ Settings updated for PostgreSQL${NC}"
fi
echo ""

# Step 7: Run migrations on PostgreSQL
echo "=========================================="
echo "Step 7: Database Migration"
echo "=========================================="
echo ""

echo "Running Django migrations on PostgreSQL..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    echo "Restoring original settings..."
    cp "$SETTINGS_FILE.backup_$TIMESTAMP" $SETTINGS_FILE
    exit 1
fi
echo ""

# Step 8: Load data into PostgreSQL
echo "=========================================="
echo "Step 8: Data Import"
echo "=========================================="
echo ""

echo "Loading data into PostgreSQL..."
python manage.py loaddata "$BACKUP_DIR/data_export_$TIMESTAMP.json"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Data imported successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some data import warnings occurred${NC}"
    echo "This is often normal. Check the output above for details."
fi
echo ""

# Step 9: Create environment file for credentials
echo "=========================================="
echo "Step 9: Environment Configuration"
echo "=========================================="
echo ""

cat > .env <<EOF
# REF-Manager Environment Configuration
# Generated: $TIMESTAMP

# Database Configuration
DB_ENGINE=postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: Update these in production
# EMAIL_HOST=smtp.york.ac.uk
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your_email@york.ac.uk
# EMAIL_HOST_PASSWORD=your_password
EOF

echo -e "${GREEN}✅ Environment file created: .env${NC}"
echo ""

# Add .env to .gitignore
if [ -f ".gitignore" ]; then
    if ! grep -q ".env" .gitignore; then
        echo ".env" >> .gitignore
        echo -e "${GREEN}✅ Added .env to .gitignore${NC}"
    fi
else
    echo ".env" > .gitignore
    echo -e "${GREEN}✅ Created .gitignore with .env${NC}"
fi
echo ""

# Step 10: Verification
echo "=========================================="
echo "Step 10: Verification"
echo "=========================================="
echo ""

echo "Testing database connection..."
python manage.py check --database default

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi
echo ""

echo "Verifying data..."
python manage.py shell <<PYTHON_EOF
from core.models import Output, Colleague, CriticalFriend
print(f"Outputs: {Output.objects.count()}")
print(f"Colleagues: {Colleague.objects.count()}")
print(f"Critical Friends: {CriticalFriend.objects.count()}")
PYTHON_EOF
echo ""

# Final summary
echo "=========================================="
echo "✅ MIGRATION COMPLETE!"
echo "=========================================="
echo ""
echo -e "${GREEN}Your REF-Manager is now using PostgreSQL!${NC}"
echo ""
echo "📋 Summary:"
echo "  • Database: PostgreSQL ($DB_NAME)"
echo "  • User: $DB_USER"
echo "  • SQLite backup: $BACKUP_DIR/db.sqlite3.$TIMESTAMP"
echo "  • Data export: $BACKUP_DIR/data_export_$TIMESTAMP.json"
echo "  • Settings backup: $SETTINGS_FILE.backup_$TIMESTAMP"
echo "  • Environment file: .env"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test the application:"
echo "     python manage.py runserver"
echo ""
echo "  2. For multi-user access (same network):"
echo "     python manage.py runserver 0.0.0.0:8000"
echo ""
echo "  3. For production deployment, see:"
echo "     DEPLOYMENT_GUIDE.md"
echo ""
echo "⚠️  Important:"
echo "  • Keep .env file secure (contains database password)"
echo "  • Don't commit .env to git"
echo "  • Update ALLOWED_HOSTS in .env for production"
echo ""
echo "🔄 Rollback (if needed):"
echo "  1. Restore settings: cp $SETTINGS_FILE.backup_$TIMESTAMP $SETTINGS_FILE"
echo "  2. Restore database: cp $BACKUP_DIR/db.sqlite3.$TIMESTAMP db.sqlite3"
echo ""
echo "=========================================="
