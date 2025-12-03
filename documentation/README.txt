REF-Manager Documentation
=========================

Version 4.0.0 "REF 2029 Ready"
December 2025

Author: George Tsoulas
Institution: University of York, Department of Language and Linguistic Science


CONTENTS
--------

This folder contains REF-Manager documentation in three formats:

  md/       - Markdown files (for GitHub, online viewing)
  latex/    - LaTeX source files (for professional printing)
  pdf/      - PDF files (for distribution, offline reading)


DOCUMENTS
---------

  README                  - Overview and quick installation
  QUICK-START-GUIDE       - Get running in 15 minutes
  USER-GUIDE              - Complete feature documentation
  TECHNICAL-DOCUMENTATION - Server deployment and development
  TROUBLESHOOTING         - Common issues and solutions
  CHANGELOG               - Version history
  DOCUMENTATION-INDEX     - This index


BUILDING PDFs
-------------

To rebuild PDF documentation from LaTeX sources:

  cd documentation
  ./build_docs.sh

Or manually:

  cd latex
  pdflatex README.tex
  pdflatex USER-GUIDE.tex
  pdflatex QUICK-START-GUIDE.tex
  pdflatex TECHNICAL-DOCUMENTATION.tex
  pdflatex TROUBLESHOOTING.tex
  pdflatex CHANGELOG.tex
  pdflatex DOCUMENTATION-INDEX.tex


NEW IN VERSION 4.0
------------------

- O/S/R Rating System (Originality, Significance, Rigour)
- DOI Auto-Fetch via OpenAlex API
- Enhanced Bulk Import with three modes
- Open Access Compliance tracking
- REF Narrative Statements support


CONTACT
-------

Author: George Tsoulas
Email:  george.tsoulas@york.ac.uk
GitHub: https://github.com/gtsoulas/ref-manager


LICENSE
-------

GNU General Public License v3.0
