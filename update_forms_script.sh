#!/bin/bash

# ============================================================
# Script to Update Forms - Filter to Current Employees Only
# ============================================================
# This script will help you update your forms to show only
# current employees in dropdowns
# ============================================================

echo "======================================"
echo "REF Manager - Filter Current Employees"
echo "======================================"
echo ""
echo "This will update your forms to show only current employees"
echo "in the dropdown menus for internal panel assignments."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Check we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found!"
    echo "Please run this script from your ref-manager directory"
    exit 1
fi

echo ""
echo "✓ Found Django project"
echo ""

# Backup the current forms.py
echo "Step 1: Creating backup of core/forms.py..."
cp core/forms.py core/forms.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"
echo ""

# Check if employment_status field exists
echo "Step 2: Checking if employment_status field exists..."
if grep -q "employment_status" core/models.py; then
    echo "✓ employment_status field found"
else
    echo "⚠ Warning: employment_status field not found in models!"
    echo "You may need to add it first."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Show current form
echo "Step 3: Checking current InternalPanelMemberForm..."
if grep -q "class InternalPanelMemberForm" core/forms.py; then
    echo "✓ Found InternalPanelMemberForm"
else
    echo "❌ InternalPanelMemberForm not found!"
    echo "This script expects the form to exist."
    exit 1
fi
echo ""

echo "Step 4: Manual Update Instructions"
echo "======================================"
echo ""
echo "Open this file: core/forms.py"
echo ""
echo "Find: class InternalPanelMemberForm(forms.ModelForm):"
echo ""
echo "Replace the entire class with the code from:"
echo "  /home/claude/forms_update_code.py"
echo ""
echo "The key changes are:"
echo "  1. Add __init__ method"
echo "  2. Filter queryset to employment_status='current'"
echo "  3. Add custom labels and help text"
echo ""
echo "Press Enter when you've made the changes..."
read

echo ""
echo "Step 5: Testing the changes"
echo "======================================"
echo ""
echo "Run these commands to test:"
echo ""
echo "# Start development server"
echo "python manage.py runserver"
echo ""
echo "Then in your browser:"
echo "1. Go to Internal Panel page"
echo "2. Click 'Add Panel Member'"
echo "3. Check the colleague dropdown only shows current employees"
echo ""
echo "✅ Setup complete!"
echo ""
echo "If you need to revert:"
echo "  cp core/forms.py.backup.* core/forms.py"
echo ""
