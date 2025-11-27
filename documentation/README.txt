# REF-Manager Documentation
# Version 3.0.0 - November 2024

## Directory Structure

documentation/
├── md/                    # Markdown format (for reading/editing)
│   ├── README.md
│   ├── QUICK-START-GUIDE.md
│   ├── USER-GUIDE.md
│   ├── TECHNICAL-DOCUMENTATION.md
│   ├── TROUBLESHOOTING.md
│   ├── CHANGELOG.md
│   └── DOCUMENTATION-INDEX.md
│
├── latex/                 # LaTeX source files
│   ├── README.tex
│   ├── QUICK-START-GUIDE.tex
│   ├── USER-GUIDE.tex
│   ├── TECHNICAL-DOCUMENTATION.tex
│   ├── TROUBLESHOOTING.tex
│   ├── CHANGELOG.tex
│   └── DOCUMENTATION-INDEX.tex
│
└── pdf/                   # PDF format (for distribution)
    ├── README.pdf
    ├── QUICK-START-GUIDE.pdf
    ├── USER-GUIDE.pdf
    ├── TECHNICAL-DOCUMENTATION.pdf
    ├── TROUBLESHOOTING.pdf
    ├── CHANGELOG.pdf
    └── DOCUMENTATION-INDEX.pdf

## Document Descriptions

1. README - System overview and quick installation
2. QUICK-START-GUIDE - Get running in 15 minutes
3. USER-GUIDE - Complete user documentation
4. TECHNICAL-DOCUMENTATION - Developer and admin reference
5. TROUBLESHOOTING - Common issues and solutions
6. CHANGELOG - Version history
7. DOCUMENTATION-INDEX - Guide to all documentation

## Quick Start Reading Path

1. Read QUICK-START-GUIDE.pdf (15 minutes)
2. Install and run the system
3. Use USER-GUIDE.pdf as daily reference
4. Check TROUBLESHOOTING.pdf if stuck

## Regenerating PDFs

To regenerate PDFs from LaTeX sources:

    cd documentation/latex
    pdflatex DOCUMENT-NAME.tex
    pdflatex DOCUMENT-NAME.tex  # Run twice for TOC
    mv DOCUMENT-NAME.pdf ../pdf/

## Contact

george.tsoulas@york.ac.uk
https://github.com/gtsoulas/ref-manager
