#!/bin/bash
#
# Debug script for REF Manager comparison system
# This helps diagnose internal server errors
#

echo "================================"
echo "REF MANAGER DEBUG SCRIPT"
echo "================================"
echo ""

PROJECT_DIR="$HOME/ref-project-app/ref-manager"

# Check if we can find the project
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project not found at $PROJECT_DIR"
    read -p "Enter path to your ref-manager project: " PROJECT_DIR
fi

echo "Checking installation at: $PROJECT_DIR"
echo ""

# 1. Check Django logs
echo "1. CHECKING DJANGO ERROR LOGS"
echo "==============================="
if [ -f "$PROJECT_DIR/ref-manager.log" ]; then
    echo "Last 30 lines of error log:"
    tail -30 "$PROJECT_DIR/ref-manager.log"
else
    echo "No log file found at $PROJECT_DIR/ref-manager.log"
fi
echo ""

# 2. Check if module imports correctly
echo "2. TESTING MODULE IMPORT"
echo "========================"
cd "$PROJECT_DIR"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from core.output_comparison import OutputComparator, parse_csv_to_dict
    print("✓ output_comparison module imports successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    from core import views
    print("✓ views.py imports successfully")
except ImportError as e:
    print(f"✗ Import error in views.py: {e}")
except Exception as e:
    print(f"✗ Error in views.py: {e}")

try:
    from core import urls
    print("✓ urls.py imports successfully")
except ImportError as e:
    print(f"✗ Import error in urls.py: {e}")
except Exception as e:
    print(f"✗ Error in urls.py: {e}")
EOF
echo ""

# 3. Check views.py syntax
echo "3. CHECKING VIEWS.PY SYNTAX"
echo "============================"
python3 -m py_compile "$PROJECT_DIR/core/views.py" 2>&1 || echo "Syntax error in views.py"
echo ""

# 4. Check urls.py syntax
echo "4. CHECKING URLS.PY SYNTAX"
echo "==========================="
python3 -m py_compile "$PROJECT_DIR/core/urls.py" 2>&1 || echo "Syntax error in urls.py"
echo ""

# 5. Run Django check
echo "5. RUNNING DJANGO CHECK"
echo "======================="
cd "$PROJECT_DIR"
python3 manage.py check 2>&1
echo ""

# 6. Check for specific comparison views
echo "6. CHECKING COMPARISON VIEWS"
echo "============================"
if grep -q "def compare_outputs" "$PROJECT_DIR/core/views.py"; then
    echo "✓ compare_outputs view found"
else
    echo "✗ compare_outputs view not found"
fi

if grep -q "def review_comparison" "$PROJECT_DIR/core/views.py"; then
    echo "✓ review_comparison view found"
else
    echo "✗ review_comparison view not found"
fi
echo ""

# 7. Check templates exist
echo "7. CHECKING TEMPLATES"
echo "====================="
if [ -f "$PROJECT_DIR/core/templates/core/compare_outputs.html" ]; then
    echo "✓ compare_outputs.html exists"
else
    echo "✗ compare_outputs.html missing"
fi

if [ -f "$PROJECT_DIR/core/templates/core/review_comparison.html" ]; then
    echo "✓ review_comparison.html exists"
else
    echo "✗ review_comparison.html missing"
fi
echo ""

# 8. Test the view directly
echo "8. TESTING VIEW IMPORT IN DJANGO SHELL"
echo "======================================="
cd "$PROJECT_DIR"
python3 manage.py shell << 'SHELLEOF'
try:
    from core.views import compare_outputs, review_comparison
    print("✓ Views import successfully")
except Exception as e:
    print(f"✗ Error importing views: {e}")
    import traceback
    traceback.print_exc()
SHELLEOF
echo ""

echo "================================"
echo "DEBUG COMPLETE"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Look at the errors above"
echo "2. Check your Django development server output"
echo "3. Run: python manage.py runserver"
echo "4. Try accessing the page and copy the full error"
