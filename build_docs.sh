#!/bin/bash

echo "Building REF Manager Documentation..."

# Create output directory
mkdir -p documentation/pdf

# Copy source files
cp INSTALLATION.md documentation/
cp *.tex documentation/

cd documentation

# Compile with XeLaTeX
echo "Compiling User Manual..."
xelatex -output-directory=pdf REF_Manager_User_Manual.tex
xelatex -output-directory=pdf REF_Manager_User_Manual.tex  # Second pass for TOC

echo "Compiling Quick Reference..."
xelatex -output-directory=pdf REF_Manager_Quick_Reference.tex

echo "Compiling FAQ..."
xelatex -output-directory=pdf REF_Manager_FAQ.tex

# Clean up auxiliary files
cd pdf
rm -f *.aux *.log *.out *.toc

echo "Done! PDFs are in documentation/pdf/"
ls -lh *.pdf

