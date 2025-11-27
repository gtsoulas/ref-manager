# ref_manager/management/commands/setup_roles.py
"""
Management command for setting up the role system.

This command:
1. Creates the four default roles if they don't exist
2. Creates UserProfiles for any users that don't have them
3. Optionally assigns default roles to existing users

Usage:
    # Create roles only
    python manage.py setup_roles
    
    # Create roles and profiles for all users
    python manage.py setup_roles --create-profiles
    
    # Create roles and assign Colleague role to users without roles
    python manage.py setup_roles --create-profiles --default-role COLLEAGUE
    
    # Make superusers into admins
    python manage.py setup_roles --superusers-admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models_access_control import Role, UserProfile


class Command(BaseCommand):
    help = 'Set up the role system for REF-Manager'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-profiles',
            action='store_true',
            help='Create UserProfiles for users that do not have them'
        )
        parser.add_argument(
            '--default-role',
            type=str,
            choices=['ADMIN', 'OBSERVER', 'INTERNAL_PANEL', 'COLLEAGUE'],
            help='Assign this role to users without any roles'
        )
        parser.add_argument(
            '--superusers-admin',
            action='store_true',
            help='Give Admin role to all superusers'
        )
        parser.add_argument(
            '--staff-observer',
            action='store_true',
            help='Give Observer role to all staff users (non-superuser)'
        )

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("REF-Manager Role Setup")
        self.stdout.write("=" * 60 + "\n")
        
        # Step 1: Create default roles
        self.create_default_roles()
        
        # Step 2: Create profiles if requested
        if options['create_profiles']:
            self.create_user_profiles()
        
        # Step 3: Assign roles to superusers
        if options['superusers_admin']:
            self.assign_superuser_admin()
        
        # Step 4: Assign roles to staff
        if options['staff_observer']:
            self.assign_staff_observer()
        
        # Step 5: Assign default role to users without roles
        if options['default_role']:
            self.assign_default_role(options['default_role'])
        
        self.stdout.write("\n" + self.style.SUCCESS("Setup complete!") + "\n")
    
    def create_default_roles(self):
        """Create the four default roles"""
        self.stdout.write(self.style.HTTP_INFO("Creating default roles..."))
        
        default_perms = Role.get_default_permissions()
        
        for code, perms in default_perms.items():
            role, created = Role.objects.update_or_create(
                code=code,
                defaults=perms
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {role.name}")
                )
            else:
                self.stdout.write(f"  • Updated: {role.name}")
        
        self.stdout.write("")
    
    def create_user_profiles(self):
        """Create UserProfiles for users that don't have them"""
        self.stdout.write(self.style.HTTP_INFO("Creating user profiles..."))
        
        users_without_profile = User.objects.filter(ref_profile__isnull=True)
        count = 0
        
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(f"  ✓ Created profile for: {user.username}")
            count += 1
        
        if count == 0:
            self.stdout.write("  All users already have profiles")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"  Created {count} profile(s)")
            )
        
        self.stdout.write("")
    
    def assign_superuser_admin(self):
        """Give Admin role to all superusers"""
        self.stdout.write(self.style.HTTP_INFO("Assigning Admin role to superusers..."))
        
        admin_role = Role.objects.get(code=Role.ADMIN)
        superusers = User.objects.filter(is_superuser=True)
        count = 0
        
        for user in superusers:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.roles.filter(code=Role.ADMIN).exists():
                profile.roles.add(admin_role)
                self.stdout.write(f"  ✓ Added Admin to: {user.username}")
                count += 1
            else:
                self.stdout.write(f"  • Already Admin: {user.username}")
        
        if count == 0:
            self.stdout.write("  No changes needed")
        
        self.stdout.write("")
    
    def assign_staff_observer(self):
        """Give Observer role to staff users (non-superuser)"""
        self.stdout.write(self.style.HTTP_INFO("Assigning Observer role to staff..."))
        
        observer_role = Role.objects.get(code=Role.OBSERVER)
        staff = User.objects.filter(is_staff=True, is_superuser=False)
        count = 0
        
        for user in staff:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.roles.filter(code=Role.OBSERVER).exists():
                profile.roles.add(observer_role)
                self.stdout.write(f"  ✓ Added Observer to: {user.username}")
                count += 1
            else:
                self.stdout.write(f"  • Already Observer: {user.username}")
        
        if count == 0:
            self.stdout.write("  No changes needed")
        
        self.stdout.write("")
    
    def assign_default_role(self, role_code):
        """Assign a default role to users without any roles"""
        self.stdout.write(
            self.style.HTTP_INFO(f"Assigning {role_code} to users without roles...")
        )
        
        role = Role.objects.get(code=role_code)
        profiles_without_roles = UserProfile.objects.filter(roles__isnull=True)
        count = 0
        
        for profile in profiles_without_roles:
            profile.roles.add(role)
            self.stdout.write(
                f"  ✓ Added {role.name} to: {profile.user.username}"
            )
            count += 1
        
        if count == 0:
            self.stdout.write("  All users already have roles")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"  Assigned to {count} user(s)")
            )
        
        self.stdout.write("")
