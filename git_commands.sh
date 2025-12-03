#!/bin/bash
#
# Git commands for REF-Manager v4.0 release
# Review and run these commands manually
#

# Stage all changes
git add -A

# Commit with release message
git commit -m "Release v4.0 - REF 2029 Ready

Major Changes:
- O/S/R rating system (Originality, Significance, Rigour)
- DOI auto-fetch via OpenAlex API
- Enhanced bulk import with three modes
- OA compliance tracking (3-month deposit rule)
- REF narrative statements (double-weighting, interdisciplinary)

Bug Fixes:
- Fixed admin.py field references
- Fixed forms.py assigned_date conflict
- Fixed views.py related_name issues

See CHANGELOG.md for full details."

# Create annotated tag
git tag -a v4.0 -m "REF-Manager v4.0 - REF 2029 Ready

Release Date: 2025-12-03
Author: George Tsoulas

Features:
- Three-component O/S/R decimal ratings (0.00-4.00)
- OpenAlex DOI metadata integration
- Hybrid/Smart/Manual bulk import modes
- OA compliance date tracking
- Double-weighting and interdisciplinary statements
- Combined rating averages"

# Push to remote
echo "Ready to push. Run:"
echo "  git push origin main"
echo "  git push origin v4.0"
