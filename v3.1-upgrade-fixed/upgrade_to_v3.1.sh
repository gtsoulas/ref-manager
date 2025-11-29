#!/bin/bash

# REF-Manager v3.1 Upgrade Script (Fixed)
# Three-component ratings with visibility controls

set -e

echo "=========================================="
echo "REF-Manager v3.1 Upgrade"
echo "Three-Component Ratings System"
echo "=========================================="
echo ""

# Check we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ ERROR: Run this from your ref-manager directory"
    echo "   cd ~/REF-Stuff/ref-manager"
    exit 1
fi

# Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Activating virtual environment..."
    source venv/bin/activate
fi

echo "✓ Running in: $(pwd)"
echo ""

# Backup database
echo "Step 1: Backing up database..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p backups

if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "backups/db.sqlite3.pre-v3.1.$TIMESTAMP"
    echo "✓ SQLite backup: backups/db.sqlite3.pre-v3.1.$TIMESTAMP"
fi

python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.Permission \
    --indent 2 \
    > "backups/data_pre_v3.1_$TIMESTAMP.json" 2>/dev/null || true
echo "✓ Data export: backups/data_pre_v3.1_$TIMESTAMP.json"
echo ""

# Copy templates
echo "Step 2: Installing templates..."
mkdir -p templates/core/includes
cp v3.1-upgrade-fixed/templates/core/includes/rating_display.html templates/core/includes/
cp v3.1-upgrade-fixed/templates/core/includes/rating_form.html templates/core/includes/
cp v3.1-upgrade-fixed/templates/core/output_detail_ratings.html templates/core/
echo "✓ Templates installed"
echo ""

# Patch models using Python script (safer)
echo "Step 3: Patching models.py..."
python v3.1-upgrade-fixed/patch_models.py
echo ""

# Create and run migrations
echo "Step 4: Running migrations..."
python manage.py makemigrations core --name three_component_ratings
python manage.py migrate
echo "✓ Migrations applied"
echo ""

# Collect static files (for server)
if [ -d "staticfiles" ]; then
    echo "Step 5: Collecting static files..."
    python manage.py collectstatic --noinput -v 0
    echo "✓ Static files collected"
    echo ""
fi

# Verify
echo "Step 6: Verifying installation..."
python manage.py check
echo "✓ System check passed"
echo ""

echo "=========================================="
echo "✅ Upgrade to v3.1 Complete!"
echo "=========================================="
echo ""
echo "New features:"
echo "  • Three-component ratings: Originality, Significance, Rigour"
echo "  • Decimal ratings from 0.00 to 4.00"
echo "  • Automatic average calculation"
echo "  • Confidential comments (role-restricted)"
echo ""
echo "Visibility rules:"
echo "  • Internal Panel: values visible to all, confidential to Admin/Observer/Panel"
echo "  • Critical Friend: visible ONLY to Admin/Observer"
echo ""
echo "Restart your server if needed:"
echo "  python manage.py runserver  # development"
echo "  sudo systemctl restart ref-manager  # production"
echo ""
