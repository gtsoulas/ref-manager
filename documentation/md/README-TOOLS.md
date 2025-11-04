# REF Manager Documentation Tools

**Building PDF Documentation from Markdown**

**Version:** 2.0.0  
**Last Updated:** November 3, 2025

---

## Overview

This guide explains how to build PDF documentation from the markdown source files using the provided `build_docs.sh` script.

---

## What Gets Built

The build script converts these markdown files to PDF:

1. `REF-MANAGER-README.md` - Main documentation
2. `QUICK-START-GUIDE.md` - Installation guide
3. `USER-GUIDE.md` - Feature guide
4. `TECHNICAL-DOCUMENTATION.md` - Developer reference
5. `TROUBLESHOOTING.md` - Problem solving
6. `CHANGELOG.md` - Version history
7. `DOCUMENTATION-INDEX.md` - Navigation guide
8. `README-TOOLS.md` - This file
9. `00-START-HERE.md` - Overview

Plus compiles LaTeX source files:
- `QUICK-START-GUIDE.tex` - LaTeX version

---

## Prerequisites

### Required Software

**1. Pandoc** - Document converter
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Check installation
pandoc --version
```

**2. XeLaTeX** - LaTeX engine
```bash
# Ubuntu/Debian (full install recommended)
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra

# macOS
brew install --cask mactex

# Check installation
xelatex --version
```

**3. PDF Tools** (optional, for combined PDF)
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

---

## Quick Start

### Basic Usage

```bash
# Make script executable
chmod +x build_docs.sh

# Run the build script
./build_docs.sh
```

That's it! PDFs will be generated in `documentation/pdf/`

---

## Build Process Details

### What the Script Does

1. **Checks dependencies** - Verifies pandoc and xelatex are installed
2. **Creates directories** - Makes `documentation/pdf/` and `documentation/latex/`
3. **Converts markdown** - Uses pandoc to convert .md files to PDF
4. **Compiles LaTeX** - Compiles .tex sources with xelatex
5. **Combines PDFs** - Creates single combined PDF (if pdfunite available)
6. **Cleans up** - Removes auxiliary files

### Build Options

**Pandoc options used:**
```bash
--pdf-engine=xelatex          # Use XeLaTeX for better Unicode support
--toc                         # Include table of contents
--toc-depth=3                 # Three levels in TOC
--number-sections             # Number all sections
-V geometry:margin=2.5cm      # Set margins
-V fontsize=11pt              # Set font size
-V linkcolor:blue             # Blue links
-V papersize:a4               # A4 paper
--highlight-style=tango       # Code syntax highlighting
-V mainfont="DejaVu Sans"     # Main font
-V monofont="DejaVu Sans Mono" # Monospace font
```

---

## Output Structure

```
documentation/
├── pdf/                                           # Generated PDFs
│   ├── REF-MANAGER-README.pdf
│   ├── QUICK-START-GUIDE.pdf
│   ├── USER-GUIDE.pdf
│   ├── TECHNICAL-DOCUMENTATION.pdf
│   ├── TROUBLESHOOTING.pdf
│   ├── CHANGELOG.pdf
│   ├── DOCUMENTATION-INDEX.pdf
│   ├── README-TOOLS.pdf
│   ├── 00-START-HERE.pdf
│   └── REF-Manager-Complete-Documentation.pdf    # Combined (optional)
│
├── latex/                                         # LaTeX intermediate files
│   └── QUICK-START-GUIDE.tex
│
└── README.txt                                     # Info file
```

---

## Customizing the Build

### Editing the Script

The script can be customized by editing `build_docs.sh`:

**Add/remove markdown files:**
```bash
# Find this section in the script
MD_FILES=(
    "REF-MANAGER-README.md"
    "QUICK-START-GUIDE.md"
    # Add your files here
    "YOUR-NEW-FILE.md"
)
```

**Add/remove LaTeX files:**
```bash
# Find this section
TEX_FILES=(
    "QUICK-START-GUIDE.tex"
    # Add your .tex files here
)
```

**Change PDF options:**
```bash
# Modify the pandoc command
pandoc "$md_file" -o "documentation/pdf/$pdf_name" \
    --pdf-engine=xelatex \
    -V geometry:margin=3cm \    # Change margin
    -V fontsize=12pt \          # Change font size
    # Add more options...
```

### Skip Certain Files

Comment out files you don't want to build:
```bash
MD_FILES=(
    "REF-MANAGER-README.md"
    # "TECHNICAL-DOCUMENTATION.md"  # Commented out
)
```

---

## Troubleshooting Build Issues

### Pandoc Not Found

**Error:**
```
✗ Error: pandoc not found
```

**Solution:**
```bash
# Install pandoc
sudo apt-get install pandoc

# Verify
pandoc --version
```

### XeLaTeX Not Found

**Error:**
```
✗ Error: xelatex not found
```

**Solution:**
```bash
# Ubuntu/Debian - full install
sudo apt-get install texlive-full

# Or minimal install
sudo apt-get install texlive-xetex texlive-fonts-recommended

# Verify
xelatex --version
```

### Font Errors

**Error:**
```
! Font \TU/DejaVuSans(0)/m/n/10=DejaVu Sans at 10.0pt not loadable
```

**Solution:**
```bash
# Install DejaVu fonts
sudo apt-get install fonts-dejavu

# Or change font in script
-V mainfont="Liberation Sans"
```

### Build Fails on Specific File

**Check:**
1. File exists and is readable
2. File is valid markdown
3. No special characters causing issues
4. Check pandoc can read it:
   ```bash
   pandoc YOUR-FILE.md -o test.pdf
   ```

### LaTeX Compilation Errors

**Error:**
```
! LaTeX Error: ...
```

**Solution:**
1. Check .tex file syntax
2. Ensure all packages are installed:
   ```bash
   sudo apt-get install texlive-latex-extra
   ```
3. Try compiling manually:
   ```bash
   xelatex QUICK-START-GUIDE.tex
   ```

### Combined PDF Fails

**Error:**
```
pdfunite: command not found
```

**Solution:**
```bash
# Install poppler-utils
sudo apt-get install poppler-utils
```

---

## Manual PDF Generation

### Convert Single Markdown File

```bash
pandoc INPUT.md -o OUTPUT.pdf \
    --pdf-engine=xelatex \
    --toc \
    --number-sections \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt
```

### Compile Single LaTeX File

```bash
xelatex FILE.tex
xelatex FILE.tex  # Run twice for TOC
```

### Combine Multiple PDFs

```bash
pdfunite file1.pdf file2.pdf file3.pdf output.pdf
```

---

## Advanced Usage

### Generate HTML Instead

```bash
# Modify script or run manually
pandoc INPUT.md -o OUTPUT.html \
    --toc \
    --standalone \
    --css=style.css
```

### Generate DOCX

```bash
pandoc INPUT.md -o OUTPUT.docx \
    --toc \
    --reference-doc=template.docx
```

### Generate EPUB

```bash
pandoc INPUT.md -o OUTPUT.epub \
    --toc \
    --epub-cover-image=cover.jpg
```

---

## Build Script Reference

### Command Line Options

The script takes no arguments currently, but you can modify it to accept options:

```bash
# Example modifications you could add:

# Clean only (no build)
./build_docs.sh --clean

# Build specific file
./build_docs.sh --file USER-GUIDE.md

# Verbose output
./build_docs.sh --verbose

# Custom output directory
./build_docs.sh --output /path/to/output
```

### Exit Codes

- **0**: Success
- **1**: Dependency missing or build error

### Environment Variables

You can set these before running:

```bash
# Use different LaTeX engine
export PDF_ENGINE=pdflatex
./build_docs.sh

# Change output directory
export DOC_OUTPUT_DIR=/custom/path
./build_docs.sh
```

---

## Best Practices

### Before Building

1. **Update all markdown files** with latest changes
2. **Check markdown syntax** - use a markdown linter
3. **Test manually** - convert one file first to test
4. **Check disk space** - PDFs can be large

### After Building

1. **Verify PDFs** - open each to check formatting
2. **Check page numbers** - ensure TOC is correct
3. **Test links** - click internal links
4. **Review combined PDF** - check page order

### For Distribution

1. **Compress PDFs** if needed:
   ```bash
   gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
      -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
      -sOutputFile=output-compressed.pdf input.pdf
   ```

2. **Create ZIP archive**:
   ```bash
   cd documentation
   zip -r REF-Manager-Documentation.zip pdf/
   ```

3. **Upload to documentation site** or share folder

---

## Integration with Git

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Auto-build docs on commit

echo "Building documentation..."
./build_docs.sh

# Add PDFs to commit
git add documentation/pdf/*.pdf

echo "Documentation built and staged"
```

### GitHub Actions

Create `.github/workflows/build-docs.yml`:

```yaml
name: Build Documentation

on:
  push:
    paths:
      - '**.md'
      - 'build_docs.sh'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y pandoc texlive-xetex
      - name: Build documentation
        run: ./build_docs.sh
      - name: Upload PDFs
        uses: actions/upload-artifact@v2
        with:
          name: documentation
          path: documentation/pdf/
```

---

## Scheduled Builds

### Daily Build with Cron

```bash
# Edit crontab
crontab -e

# Add line for daily 2 AM build
0 2 * * * cd /path/to/ref-manager && ./build_docs.sh >> /path/to/build.log 2>&1
```

### Weekly Summary Email

```bash
#!/bin/bash
# weekly-doc-build.sh

cd /path/to/ref-manager
./build_docs.sh

# Email results
mail -s "Weekly Documentation Build" admin@example.com < build.log
```

---

## Tips and Tricks

1. **Preview before building**:
   Use a markdown preview tool to check formatting

2. **Keep builds fast**:
   Comment out files you're not changing

3. **Version PDFs**:
   ```bash
   cp documentation/pdf/USER-GUIDE.pdf \
      documentation/archive/USER-GUIDE-v2.0.pdf
   ```

4. **Watermark drafts**:
   Add draft watermark to PDFs in development

5. **Check file sizes**:
   ```bash
   ls -lh documentation/pdf/
   ```
   Large files may indicate embedded images that could be optimized

---

## Support

**Script issues?**
- Check dependencies are installed
- Read error messages carefully
- Try building one file manually
- Check file permissions

**PDF quality issues?**
- Adjust pandoc options
- Try different font
- Check source markdown
- Review LaTeX output

**Still stuck?**
- Check TROUBLESHOOTING.md
- Contact system administrator
- Submit issue on GitHub (if using)

---

## Summary

**To build all documentation:**
```bash
./build_docs.sh
```

**Output location:**
```
documentation/pdf/
```

**Requirements:**
- pandoc
- xelatex (texlive)
- poppler-utils (optional)

**Build time:**
~2-5 minutes depending on system

---

**Version:** 2.0.0  
**Last Updated:** November 3, 2025  
**Script Author:** George Tsoulas

For complete documentation, see the generated PDFs in `documentation/pdf/`.
