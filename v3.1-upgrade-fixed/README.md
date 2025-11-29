# REF-Manager v3.1 Upgrade Package

## Three-Component Ratings with Visibility Controls

### New Features

1. **Three-Component Ratings**
   - Originality (0.00 - 4.00)
   - Significance (0.00 - 4.00)
   - Rigour (0.00 - 4.00)
   - Automatic average calculation to 2 decimal places

2. **Confidential Comments**
   - Separate field for private reviewer notes
   - Not visible to output authors

3. **Role-Based Visibility**
   - Internal Panel ratings: values visible to all, confidential comments restricted
   - Critical Friend ratings: visible ONLY to Admin and Observer roles

### Visibility Matrix

| Content | Admin | Observer | Panel Member | Colleague |
|---------|:-----:|:--------:|:------------:|:---------:|
| Internal Panel O/S/R values | ✓ | ✓ | ✓ | ✓ |
| Internal Panel comments | ✓ | ✓ | ✓ | ✓ |
| Internal Panel confidential | ✓ | ✓ | ✓ | ✗ |
| Critical Friend (all) | ✓ | ✓ | ✗ | ✗ |

### Installation

#### Method 1: Automated (Recommended)

```bash
# Copy the upgrade package to your ref-manager directory
cp -r v3.1-upgrade-fixed ~/REF-Stuff/ref-manager/

# Run the upgrade script
cd ~/REF-Stuff/ref-manager
source venv/bin/activate
./v3.1-upgrade-fixed/upgrade_to_v3.1.sh
```

#### Method 2: Manual

1. Copy templates:
   ```bash
   cp -r v3.1-upgrade-fixed/templates/core/includes/* templates/core/includes/
   cp v3.1-upgrade-fixed/templates/core/output_detail_ratings.html templates/core/
   ```

2. Patch models:
   ```bash
   python v3.1-upgrade-fixed/patch_models.py
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations core --name three_component_ratings
   python manage.py migrate
   ```

### Files Included

```
v3.1-upgrade-fixed/
├── README.md                    # This file
├── upgrade_to_v3.1.sh          # Automated upgrade script
├── patch_models.py             # Python model patcher (safer)
└── templates/
    └── core/
        ├── includes/
        │   ├── rating_display.html
        │   └── rating_form.html
        └── output_detail_ratings.html
```

### Rating Scale

| Value | Description |
|-------|-------------|
| 4.00 | World-leading quality |
| 3.00 | Internationally excellent |
| 2.00 | Internationally recognised |
| 1.00 | Nationally recognised |
| 0.00 | Below threshold |

### Rollback

If you need to rollback:

```bash
# Restore database backup
cp backups/db.sqlite3.pre-v3.1.TIMESTAMP db.sqlite3

# Restore models.py
cp core/models.py.pre-v3.1.TIMESTAMP core/models.py

# Remove generated migration
rm core/migrations/*three_component_ratings*

# Verify
python manage.py check
```

### After Upgrade

1. Restart your server:
   ```bash
   sudo systemctl restart ref-manager  # production
   ```

2. Verify in browser that ratings display correctly

3. Test entering new ratings with decimal values

### Support

- Email: george.tsoulas@york.ac.uk
- GitHub: https://github.com/gtsoulas/ref-manager
