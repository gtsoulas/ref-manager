# REF-Manager User Guide

## Complete Guide to Using REF-Manager v4.0

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Managing Colleagues](#3-managing-colleagues)
4. [Managing Outputs](#4-managing-outputs)
5. [DOI Auto-Fetch](#5-doi-auto-fetch)
6. [O/S/R Quality Ratings](#6-osr-quality-ratings)
7. [Open Access Compliance](#7-open-access-compliance)
8. [REF Narrative Statements](#8-ref-narrative-statements)
9. [Risk Assessment](#9-risk-assessment)
10. [Critical Friends](#10-critical-friends)
11. [Internal Panel](#11-internal-panel)
12. [Bulk Import](#12-bulk-import)
13. [REF Submissions](#13-ref-submissions)
14. [Task Management](#14-task-management)
15. [Reports & Export](#15-reports--export)
16. [User Management](#16-user-management)

---

## 1. Getting Started

### Logging In

1. Navigate to your REF-Manager URL
2. Enter your username and password
3. Click **Log In**

### Understanding Your Role

| Role | Description | Capabilities |
|------|-------------|--------------|
| Administrator | Full access | All features, user management |
| Observer | Read-only | View all data, export |
| Internal Panel | Reviewer | Rate assigned outputs |
| Colleague | Staff member | Manage own outputs |

You may have multiple roles with combined permissions.

### Navigation

The main menu provides access to:
- **Dashboard**: Overview and statistics
- **Colleagues**: Staff management
- **Outputs**: Research output management
- **Critical Friends**: External reviewer management
- **Internal Panel**: Internal reviewer management
- **Reports**: Analytics and export
- **Tasks**: Task tracking
- **Admin**: System administration (Administrators)

---

## 2. Dashboard

The dashboard provides an overview of your REF preparation status.

### Statistics Cards

- **Total Colleagues**: Returnable staff count
- **Total Outputs**: All tracked outputs
- **Approved Outputs**: Ready for submission
- **In Review**: Currently being assessed
- **Pending Requests**: Outstanding items

### Quality Distribution Chart

Visual breakdown by quality rating:
- 4★ (World-leading): Green
- 3★ (Internationally excellent): Blue
- 2★ (Recognised internationally): Yellow
- 1★ (Recognised nationally): Orange
- Unclassified: Grey

---

## 3. Managing Colleagues

### Adding a Colleague

1. Click **Add Colleague**
2. Complete the form:
   - **Staff ID**: Unique identifier
   - **Name**: First and last name
   - **FTE**: Full-time equivalent (0.1-1.0)
   - **Contract Type**: Permanent, Fixed-term, Research
   - **Category**: Select from dropdown
   - **Unit of Assessment**: UOA code
3. Click **Save**

### Required Outputs Calculation

REF-Manager calculates required outputs based on FTE:
- Formula: FTE × 2.5 (rounded down, max 5)
- Example: 0.8 FTE = 2 outputs required

---

## 4. Managing Outputs

### Adding an Output

1. Click **Add Output**
2. Complete the form:
   - **Colleague**: Select author
   - **Title**: Full title
   - **Publication Type**: Article, Book, etc.
   - **Publication Year**: 2021-2028
   - **Publication Venue**: Journal, publisher, etc.
   - **Authors**: All authors in citation format
   - **Author Position**: Position in author list
   - **UOA**: Unit of Assessment
3. Click **Save**

### Publication Types

| Code | Type |
|------|------|
| A | Journal Article |
| B | Book |
| C | Book Chapter |
| D | Conference Paper |
| E | Patent |
| F | Software |
| G | Performance/Exhibition |
| H | Other |

### Output Status Workflow

```
Draft → Submitted → Internal Review → External Review → Approved
                         ↓                    ↓
                    Revision ←──────── Rejected
```

---

## 5. DOI Auto-Fetch

**NEW in v4.0**: Automatically populate output metadata from a DOI.

### Using DOI Auto-Fetch

1. Navigate to **Outputs → Add Output**
2. In the **Intelligent Output Entry** section at the top:
   - Paste the DOI (e.g., `10.1038/nature12373`)
   - Click **Auto-Fill**
3. Wait for the metadata to load
4. Review and adjust populated fields:
   - Title, Authors, Publication Venue
   - Year, Volume, Issue, Pages
   - Open Access Status
   - Citation Count
5. Select the Colleague and add ratings
6. Click **Save**

### Supported DOI Formats

All these formats work:
- `10.1038/nature12373`
- `doi:10.1038/nature12373`
- `https://doi.org/10.1038/nature12373`

### Data Source

Metadata is fetched from **OpenAlex**, a free comprehensive academic database that aggregates data from Crossref, Microsoft Academic Graph, and Unpaywall.

---

## 6. O/S/R Quality Ratings

**NEW in v4.0**: Three-component quality assessment system aligned with REF 2029.

### Rating Components

| Component | Description | What to Assess |
|-----------|-------------|----------------|
| **Originality** | Novel contribution | Innovation, new ideas, approaches |
| **Significance** | Impact on field | Importance, influence, reach |
| **Rigour** | Methodological soundness | Quality of execution, evidence |

### Rating Scale

| Score | Star | Description |
|-------|------|-------------|
| 3.50 - 4.00 | 4★ | World-leading |
| 2.50 - 3.49 | 3★ | Internationally excellent |
| 1.50 - 2.49 | 2★ | Internationally recognised |
| 0.50 - 1.49 | 1★ | Nationally recognised |
| 0.00 - 0.49 | U | Unclassified |

### Rating Sources

Each output can receive ratings from three sources:

1. **Internal Panel** (blue card)
   - Departmental reviewers
   - Assigned by administrators

2. **Critical Friend** (yellow card)
   - External reviewers
   - Independent assessment

3. **Self-Assessment** (green card)
   - Author's own evaluation
   - Completed when submitting

### Entering Ratings

1. Edit an output
2. Scroll to **Quality Ratings (O/S/R)** section
3. Enter decimal values (0.00-4.00) for each component:
   - Originality
   - Significance
   - Rigour
4. Save

### Average Calculations

The system automatically calculates:
- **Source Average**: Average of O, S, R for each source
- **Combined Average (excl. self)**: Average of Internal + External
- **Combined Average (all)**: Average of all three sources

---

## 7. Open Access Compliance

**NEW in v4.0**: Track REF 2029 Open Access requirements.

### OA Status Types

| Status | Description |
|--------|-------------|
| Gold | Published in full OA journal (paid APC) |
| Green | Available via repository (e.g., YORA) |
| Hybrid | OA article in subscription journal |
| Bronze | Free to read but no formal license |
| Closed | Paywalled, not openly accessible |

### Compliance Dates

Track these dates for each output:

| Field | Description |
|-------|-------------|
| **Acceptance Date** | When paper was accepted by journal |
| **Deposit Date** | When uploaded to repository (YORA) |
| **Embargo End Date** | When full-text becomes publicly available |

### 3-Month Deposit Rule

REF 2029 requires outputs to be deposited within 3 months (92 days) of acceptance.

The system automatically checks:
- ✅ **Compliant**: deposit_date - acceptance_date ≤ 92 days
- ❌ **Non-compliant**: deposit_date - acceptance_date > 92 days

### Recording Exceptions

If an output is non-compliant with a valid reason:
1. Select **OA Exception** type
2. Add explanation in **OA Compliance Notes**

---

## 8. REF Narrative Statements

**NEW in v4.0**: Support for required REF 2029 statements.

### Double-Weighting Statement

Required if output is marked as double-weighted.

- **Word Limit**: 300 words
- **Purpose**: Justify why output merits double weighting
- **Content**: Explain extended scope, scale, or significance

To add:
1. Check **Double Weighted** flag
2. Complete the statement field
3. Real-time word counter shows progress

### Interdisciplinary Statement

Optional for cross-panel outputs.

- **Word Limit**: 500 words
- **Purpose**: Explain cross-panel methodology and value
- **Content**: Describe how output bridges disciplines

To add:
1. Check **Interdisciplinary** flag
2. Complete the statement field

---

## 9. Risk Assessment

### Understanding Risk Scores

Each output has a composite risk score (0-1 scale):

| Score | Level | Colour | Action |
|-------|-------|--------|--------|
| 0.00-0.24 | Low | Green | Proceed |
| 0.25-0.49 | Medium-Low | Yellow | Monitor |
| 0.50-0.74 | Medium-High | Orange | Mitigate |
| 0.75-1.00 | High | Red | Urgent |

### Risk Components

**Content Risk (60% weight)**
- Panel disagreement likelihood
- Methodology concerns
- Approach controversies

**Timeline Risk (40% weight)**
Based on publication status:
| Status | Risk Score |
|--------|------------|
| Published | 0.00 |
| Accepted | 0.20 |
| Under Review | 0.50 |
| In Revision | 0.70 |
| In Preparation | 0.90 |

### Open Access Compliance Risk

Non-compliant outputs receive minimum 0.85 risk score.

---

## 10. Critical Friends

External reviewers providing independent assessments.

### Adding a Critical Friend

1. Click **Add Critical Friend**
2. Enter details:
   - Name and email
   - Institution
   - Expertise area
3. Save

### Assigning Outputs

1. Open output detail page
2. Click **Assign Critical Friend**
3. Select reviewer
4. Mark Specialist/Non-Specialist
5. Save

---

## 11. Internal Panel

Departmental colleagues reviewing outputs.

### Assigning Outputs

1. Open output detail page
2. Click **Assign Internal Panel**
3. Select panel member
4. Mark Specialist/Non-Specialist
5. Save

### Panel Workflow

1. Administrator assigns outputs
2. Panel member reviews
3. O/S/R ratings submitted
4. Rating finalised
5. Administrator reviews

---

## 12. Bulk Import

**NEW in v4.0**: Enhanced bulk import with DOI lookup.

### Import Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **Hybrid** | Fetches DOI metadata where available, uses CSV otherwise | Mixed content |
| **Smart** | Only imports rows with DOIs | Journal articles |
| **Manual** | Uses CSV data directly, no API calls | Fast import |

### CSV Format

Minimal (with DOIs):
```
doi,staff_id
10.1038/nature12373,ABC123
10.1126/science.1234567,DEF456
```

Full (without DOIs):
```
title,publication_year,publication_venue,all_authors,publication_type,staff_id
"My Paper Title",2024,"Journal Name","Smith, J., Jones, A.",A,ABC123
```

### Publication Type Codes

| Code | Type |
|------|------|
| A | Journal Article |
| B | Book |
| C | Book Chapter |
| D | Conference Paper |
| H | Other |

### Running an Import

1. Navigate to **Outputs → Bulk Import**
2. Select import mode
3. Upload CSV file
4. Enable options:
   - Skip duplicates
   - Auto-link colleagues
5. Click **Start Import**
6. Review results

---

## 13. REF Submissions

Model different submission scenarios.

### Creating a Submission

1. Go to **Reports → Submissions**
2. Click **Create Submission**
3. Enter name and details
4. Add outputs
5. Review metrics

### Submission Metrics

| Metric | Description |
|--------|-------------|
| Quality Score | GPA-style average |
| Risk Score | Portfolio risk level |
| Representativeness | Research area coverage |
| Equality Score | Staff inclusion % |

---

## 14. Task Management

Track REF preparation tasks.

### Creating a Task

1. Click **Create Task**
2. Enter title, description
3. Set category and priority
4. Assign to user
5. Set due date
6. Save

### Task Priorities

| Priority | Urgency |
|----------|---------|
| Low | When possible |
| Medium | This week |
| High | Prioritise |
| Urgent | Immediate |

---

## 15. Reports & Export

### Available Reports

| Report | Description |
|--------|-------------|
| Submission Overview | Status summary |
| Quality Profile | Rating distribution |
| Staff Progress | Individual tracking |
| Review Status | Assessment progress |
| Risk Dashboard | Risk analysis |

### Export Formats

- **Excel**: Full data with formatting
- **CSV**: Simple tabular data
- **LaTeX**: Professional reports

---

## 16. User Management

*Administrator access required*

### Assigning Roles

1. Navigate to **Manage → Users**
2. Select user
3. Assign/remove roles
4. Save

### Role Permissions

| Permission | Admin | Observer | Panel | Colleague |
|------------|:-----:|:--------:|:-----:|:---------:|
| View all outputs | ✓ | ✓ | - | - |
| Edit any output | ✓ | - | - | - |
| Enter O/S/R ratings | ✓ | - | ✓ | - |
| Manage users | ✓ | - | - | - |
| Export data | ✓ | ✓ | - | - |

---

## Getting Help

- Check [Troubleshooting](TROUBLESHOOTING.md)
- Contact: george.tsoulas@york.ac.uk
- GitHub: https://github.com/gtsoulas/ref-manager
