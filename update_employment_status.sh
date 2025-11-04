#!/bin/bash

# ============================================================
# Update Staff Employment Status Interactively
# ============================================================

echo "======================================"
echo "Update Staff Employment Status"
echo "======================================"
echo ""

cd ~/ref-project-app/ref-manager

python manage.py shell << 'EOF'
from core.models import Colleague

print("\n" + "=" * 70)
print("SELECT STAFF TO MARK AS FORMER EMPLOYEES")
print("=" * 70)

colleagues = Colleague.objects.select_related('user').order_by('user__last_name')

print(f"\n{'#':<4} {'ID':<5} {'Name':<35} {'Staff ID':<12} {'Status':<15}")
print("-" * 70)

colleague_list = []
for idx, colleague in enumerate(colleagues, 1):
    name = colleague.user.get_full_name()
    staff_id = colleague.staff_id or 'N/A'
    status = colleague.employment_status or 'NOT SET'
    print(f"{idx:<4} {colleague.id:<5} {name:<35} {staff_id:<12} {status:<15}")
    colleague_list.append(colleague)

print("\n" + "=" * 70)
print("\nEnter the numbers of staff to mark as FORMER (comma-separated)")
print("Example: 1,3,5,7")
print("Or type 'all' to see all options, 'cancel' to exit")
print("-" * 70)

import sys
selection = input("\nYour selection: ").strip()

if selection.lower() == 'cancel':
    print("\n❌ Cancelled")
    sys.exit(0)

if selection.lower() == 'all':
    print("\nShowing additional options...")
    print("Type numbers or use special commands:")
    print("  range:1-5   - Select range of numbers")
    print("  cancel      - Exit without changes")
    selection = input("\nYour selection: ").strip()

if selection:
    try:
        # Parse selection
        selected_indices = []
        for part in selection.split(','):
            part = part.strip()
            if '-' in part and part.split('-')[0].isdigit():
                # Range
                start, end = map(int, part.split('-'))
                selected_indices.extend(range(start, end + 1))
            elif part.isdigit():
                selected_indices.append(int(part))
        
        # Get selected colleagues
        selected_colleagues = []
        for idx in selected_indices:
            if 1 <= idx <= len(colleague_list):
                selected_colleagues.append(colleague_list[idx - 1])
        
        if not selected_colleagues:
            print("\n❌ No valid selections made")
            sys.exit(0)
        
        # Confirm
        print("\n" + "=" * 70)
        print("CONFIRM: These staff will be marked as FORMER:")
        print("=" * 70)
        for c in selected_colleagues:
            print(f"  • {c.user.get_full_name()} ({c.staff_id})")
        
        confirm = input("\nProceed? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            # Update
            updated = 0
            for colleague in selected_colleagues:
                colleague.employment_status = 'former'
                colleague.save()
                updated += 1
            
            print(f"\n✅ Updated {updated} staff member(s) to 'former' status")
            
            # Show summary
            current = Colleague.objects.filter(employment_status='current').count()
            former = Colleague.objects.filter(employment_status='former').count()
            print(f"\nNew totals:")
            print(f"  Current staff: {current}")
            print(f"  Former staff:  {former}")
        else:
            print("\n❌ Cancelled")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please try again with valid numbers")
else:
    print("\n❌ No selection made")

print("\n" + "=" * 70)
EOF

echo ""
echo "Done!"
echo ""
