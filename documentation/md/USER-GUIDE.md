# REF-Manager User Guide

## Complete Guide to Using REF-Manager v3.0

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Managing Colleagues](#3-managing-colleagues)
4. [Managing Outputs](#4-managing-outputs)
5. [Quality Assessments](#5-quality-assessments)
6. [Risk Assessment](#6-risk-assessment)
7. [Critical Friends](#7-critical-friends)
8. [Internal Panel](#8-internal-panel)
9. [REF Submissions](#9-ref-submissions)
10. [Task Management](#10-task-management)
11. [Reports & Export](#11-reports--export)
12. [User Management](#12-user-management)

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

### Colleague Categories

Staff breakdown by category:
- Independent Researchers
- Non-Independent Researchers
- Post-Doctoral Researchers
- Academic Staff
- Research Assistants
- Support Staff

### Recent Activity

Shows recently updated outputs and reviews.

---

## 3. Managing Colleagues

### Viewing Colleagues

Navigate to **Colleagues** to see all staff members.

**Filters:**
- Employment Status (Current/Former)
- Colleague Category
- Returnable Status
- Search by name

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

### Colleague Categories

| Category | Description |
|----------|-------------|
| Independent | Leads own research programme |
| Non-Independent | Contributes to others' research |
| Post-Doctoral | Post-doctoral researchers |
| Academic | Teaching-focused academic staff |
| Research Assistant | Research support roles |
| Support | Administrative/technical support |

### Marking Former Staff

1. Go to colleague profile
2. Click **Mark as Former**
3. Enter employment end date
4. Save

### Required Outputs Calculation

REF-Manager calculates required outputs based on FTE:
- Formula: FTE × 2.5 (rounded down, max 5)
- Example: 0.8 FTE = 2 outputs required

---

## 4. Managing Outputs

### Viewing Outputs

Navigate to **Outputs** to see all research outputs.

**Filters:**
- Status
- Quality Rating
- Publication Year
- Publication Type
- Colleague

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

| Status | Description |
|--------|-------------|
| Draft | Work in progress |
| Submitted | Submitted for review |
| Internal Review | Internal panel assessment |
| External Review | Critical friend assessment |
| Approved | Ready for REF |
| Rejected | Not suitable |
| Revision | Needs changes |
| Reserve | Backup output |

### Importing Outputs

**CSV Import:**
1. Go to **Outputs → Import**
2. Upload CSV file
3. Map columns
4. Review and confirm

**BibTeX Import:**
1. Go to **Outputs → Import**
2. Select BibTeX format
3. Upload .bib file
4. Assign to colleagues

---

## 5. Quality Assessments

### Rating System

REF quality ratings:

| Rating | Description | GPA Value |
|--------|-------------|-----------|
| 4★ | World-leading | 4 |
| 3★ | Internationally excellent | 3 |
| 2★ | Recognised internationally | 2 |
| 1★ | Recognised nationally | 1 |
| U | Unclassified | 0 |

### Multi-Dimensional Ratings

Each output can receive three independent ratings:

1. **Internal Panel Rating**: Departmental reviewers
2. **Critical Friend Rating**: External reviewers
3. **Self-Assessment**: Author's own evaluation

### Average Rating

Automatically calculated from available ratings:
- Includes Internal and External by default
- Self-Assessment optional in calculation
- Shows as decimal (e.g., 3.5) or star rating

### Submitting Ratings

**As Reviewer:**
1. View assigned output
2. Assess quality
3. Enter rating
4. Add feedback comments
5. Click **Submit Rating**

**Finalising:**
- Click **Finalise** to lock rating
- Only administrators can unfinalise

---

## 6. Risk Assessment

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
| Planned | 1.00 |

### Open Access Compliance

Critical for REF eligibility:
- Flagged outputs receive minimum 0.85 risk
- Check deposit dates and licences
- Verify compliance before submission

### Risk Dashboard

Navigate to **Reports → Risk Dashboard**:
- View risk distribution
- Identify high-risk outputs
- Check OA compliance
- Review panel alignment

### Updating Risk Assessment

1. Edit output
2. Scroll to Risk Assessment section
3. Update scores and rationale
4. Save

---

## 7. Critical Friends

External reviewers providing independent assessments.

### Managing Critical Friends

Navigate to **Critical Friends**:
- View all reviewers
- Add new reviewers
- Track assignments

### Adding a Critical Friend

1. Click **Add Critical Friend**
2. Enter details:
   - Name and email
   - Institution
   - Expertise area
   - Internal/External status
3. Save

### Assigning Outputs

1. Open output detail page
2. Click **Assign Critical Friend**
3. Select reviewer
4. Mark Specialist/Non-Specialist
5. Save

### Specialist Classification

- **Specialist**: Expert in specific area
- **Non-Specialist**: General academic reviewer

Helps contextualise assessment feedback.

---

## 8. Internal Panel

Departmental colleagues reviewing outputs.

### Managing Panel Members

Navigate to **Internal Panel**:
- View all members
- Add new members
- Track workload

### Assigning Outputs

1. Open output detail page
2. Click **Assign Internal Panel**
3. Select panel member
4. Mark Specialist/Non-Specialist
5. Save

### Panel Workflow

1. Administrator assigns outputs
2. Panel member reviews
3. Rating submitted
4. Rating finalised
5. Administrator reviews

---

## 9. REF Submissions

Model different submission scenarios.

### Creating a Submission

1. Go to **Reports → Submissions**
2. Click **Create Submission**
3. Enter:
   - Name (e.g., "Main Strategy v1")
   - Unit of Assessment
   - Submission Year
4. Create

### Adding Outputs

1. Open submission
2. Browse available outputs
3. Click **Add** to include
4. Mark as Reserve if backup

### Submission Metrics

| Metric | Description |
|--------|-------------|
| Quality Score | GPA-style average |
| Risk Score | Portfolio risk level |
| Representativeness | Research area coverage |
| Equality Score | Staff inclusion % |
| Gender Balance | Representation metric |

### Comparing Scenarios

Create multiple scenarios:
- Conservative (lower risk)
- Ambitious (higher 4★ potential)
- Balanced (mixed approach)

Compare metrics to choose optimal strategy.

---

## 10. Task Management

Track REF preparation tasks.

### Viewing Tasks

Navigate to **Tasks**:
- Your assigned tasks
- All tasks (Administrators)
- Task dashboard

### Creating a Task

1. Click **Create Task**
2. Enter:
   - Title and description
   - Category
   - Priority
   - Assigned to
   - Due date
3. Save

### Task Categories

- Administrative
- Review
- Submission
- Communication
- Data
- Other

### Task Priorities

| Priority | Urgency |
|----------|---------|
| Low | When possible |
| Medium | This week |
| High | This week, prioritise |
| Urgent | Immediate |

### Completing Tasks

1. Open task
2. Update status to In Progress
3. Add notes as needed
4. Click **Mark Complete**

---

## 11. Reports & Export

### Available Reports

| Report | Description |
|--------|-------------|
| Submission Overview | Status summary |
| Quality Profile | Rating distribution |
| Staff Progress | Individual tracking |
| Review Status | Assessment progress |
| Risk Dashboard | Risk analysis |
| Comprehensive | Full report |

### Exporting Data

**Excel Export:**
- Outputs with all fields
- Assignments and ratings
- Submission portfolios

**CSV Export:**
- Simple tabular data
- For import into other tools

**LaTeX Export:**
- Formal reports
- Professional formatting

### Generating Reports

1. Go to Reports section
2. Select report type
3. Apply filters if needed
4. Click **Export**
5. Choose format
6. Download

---

## 12. User Management

*Administrator access required*

### Viewing Users

Navigate to **Manage → Users**:
- List all users
- View roles
- Edit permissions

### Assigning Roles

**Via Interface:**
1. Click user
2. Select/deselect roles
3. Save

**Via Command Line:**
```bash
python manage.py assign_roles username --add ADMIN
python manage.py assign_roles username --set OBSERVER
python manage.py assign_roles username --remove INTERNAL_PANEL
```

### Role Permissions

| Permission | Admin | Observer | Panel | Colleague |
|------------|:-----:|:--------:|:-----:|:---------:|
| View all outputs | ✓ | ✓ | - | - |
| Edit any output | ✓ | - | - | - |
| Rate assigned | ✓ | - | ✓ | - |
| Manage users | ✓ | - | - | - |
| Export data | ✓ | ✓ | - | - |

---

## Tips & Best Practices

### Data Quality
- Keep output information complete
- Update publication statuses regularly
- Verify DOIs and URLs

### Risk Management
- Address high-risk outputs early
- Ensure OA compliance
- Document risk rationale

### Portfolio Strategy
- Model multiple scenarios
- Balance risk and quality
- Ensure staff representation

### Regular Reviews
- Schedule periodic reviews
- Track progress against milestones
- Update assessments as needed

---

## Getting Help

- Check [Troubleshooting](TROUBLESHOOTING.md)
- Contact: george.tsoulas@york.ac.uk
- GitHub Issues: https://github.com/gtsoulas/ref-manager
