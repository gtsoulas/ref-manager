#!/bin/bash
#
# REF-Manager Documentation Build Script
# Version 4.0.0
# Author: George Tsoulas
#
# Usage: ./build_docs.sh
#

set -e

echo "=============================================="
echo "REF-Manager v4.0 Documentation Builder"
echo "=============================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create output directory
mkdir -p pdf

# List of documents to compile
DOCS=(
    "README"
    "QUICK-START-GUIDE"
    "USER-GUIDE"
    "TECHNICAL-DOCUMENTATION"
    "TROUBLESHOOTING"
    "CHANGELOG"
    "DOCUMENTATION-INDEX"
)

# Check for pdflatex
if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex not found. Please install texlive."
    echo "  Ubuntu/Debian: sudo apt install texlive-latex-base texlive-latex-extra"
    echo "  macOS: brew install mactex"
    exit 1
fi

cd latex

# Compile each document
for doc in "${DOCS[@]}"; do
    if [ -f "${doc}.tex" ]; then
        echo "Compiling ${doc}..."
        pdflatex -interaction=nonstopmode -output-directory=../pdf "${doc}.tex" > /dev/null 2>&1
        # Second pass for TOC
        pdflatex -interaction=nonstopmode -output-directory=../pdf "${doc}.tex" > /dev/null 2>&1
        echo "  ✓ ${doc}.pdf"
    else
        echo "  ✗ ${doc}.tex not found, skipping"
    fi
done

cd ..

# Clean up auxiliary files
echo ""
echo "Cleaning up auxiliary files..."
cd pdf
rm -f *.aux *.log *.out *.toc *.lof *.lot 2>/dev/null || true
cd ..

echo ""
echo "=============================================="
echo "Build Complete!"
echo "=============================================="
echo ""
echo "PDFs generated in: $(pwd)/pdf/"
echo ""
ls -lh pdf/*.pdf 2>/dev/null || echo "No PDFs found"
echo ""
