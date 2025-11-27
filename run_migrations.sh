#!/bin/bash
# REF Manager Migration Script
# Run this after applying patches

echo "🔄 Running migrations..."
python manage.py makemigrations
echo ""
echo "✓ Migration files created"
echo ""
python manage.py migrate
echo ""
echo "✅ Migrations applied successfully!"
echo ""
echo "📦 Don't forget to install bibtexparser:"
echo "   pip install bibtexparser"
