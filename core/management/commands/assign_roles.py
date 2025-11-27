# ref_manager/management/commands/assign_roles.py
"""
Management command for assigning roles to users.

Usage:
    # Add a single role
    python manage.py assign_roles jane.smith --add OBSERVER
    
    # Add multiple roles
    python manage.py assign_roles john.doe --add OBSERVER INTERNAL_PANEL
    
    # Set exact roles (removes others)
    python manage.py assign_roles admin --set ADMIN
    
    # Remove a role
    python manage.py assign_roles jane.smith --remove INTERNAL_PANEL
    
    # List all users and their roles
    python manage.py assign_roles --list
    
    # Show roles for a specific user
    python manage.py assign_roles jane.smith --show
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from core.models_access_control import Role, UserProfile


class Command(BaseCommand):
    help = 'Manage user roles for REF-Manager access control'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            nargs='?',
            type=str,
            help='Username to modify (optional if using --list)'
        )
        parser.add_argument(
            '--add',
            nargs='+',
            choices=['ADMIN', 'OBSERVER', 'INTERNAL_PANEL', 'COLLEAGUE'],
            metavar='ROLE',
            help='Role(s) to add to the user'
        )
        parser.add_argument(
            '--remove',
            nargs='+',
            choices=['ADMIN', 'OBSERVER', 'INTERNAL_PANEL', 'COLLEAGUE'],
            metavar='ROLE',
            help='Role(s) to remove from the user'
        )
        parser.add_argument(
            '--set',
            nargs='+',
            choices=['ADMIN', 'OBSERVER', 'INTERNAL_PANEL', 'COLLEAGUE'],
            metavar='ROLE',
            help='Set roles to exactly these (removes others)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove all roles from the user'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all users and their roles'
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show detailed roles and permissions for a user'
        )
        parser.add_argument(
            '--create-profile',
            action='store_true',
            help='Create UserProfile if it does not exist'
        )

    def handle(self, *args, **options):
        # Handle --list
        if options['list']:
            self.list_all_users()
            return
        
        # All other operations require a username
        if not options['username']:
            raise CommandError('Username is required (or use --list)')
        
        username = options['username']
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' not found")
        
        # Get or create profile
        try:
            profile = user.ref_profile
        except UserProfile.DoesNotExist:
            if options['create_profile']:
                profile = UserProfile.objects.create(user=user)
                self.stdout.write(
                    self.style.SUCCESS(f"Created profile for {username}")
                )
            else:
                raise CommandError(
                    f"User '{username}' has no profile. "
                    "Use --create-profile to create one."
                )
        
        # Handle --show
        if options['show']:
            self.show_user_details(profile)
            return
        
        # Handle --clear
        if options['clear']:
            profile.roles.clear()
            self.stdout.write(
                self.style.SUCCESS(f"Cleared all roles from {username}")
            )
            return
        
        # Handle --set
        if options['set']:
            roles = Role.objects.filter(code__in=options['set'])
            profile.roles.set(roles)
            role_names = ", ".join(r.name for r in roles)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Set roles for {username}: {role_names}"
                )
            )
            return
        
        # Handle --add
        if options['add']:
            for role_code in options['add']:
                try:
                    role = Role.objects.get(code=role_code)
                    profile.roles.add(role)
                    self.stdout.write(
                        self.style.SUCCESS(f"Added {role.name} to {username}")
                    )
                except Role.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Role '{role_code}' not found")
                    )
        
        # Handle --remove
        if options['remove']:
            for role_code in options['remove']:
                removed = profile.roles.filter(code=role_code)
                if removed.exists():
                    role_name = removed.first().name
                    profile.roles.remove(removed.first())
                    self.stdout.write(
                        self.style.SUCCESS(f"Removed {role_name} from {username}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"User does not have role '{role_code}'"
                        )
                    )
        
        # Show current state if any changes were made
        if options['add'] or options['remove']:
            current_roles = profile.get_role_display()
            self.stdout.write(f"\nCurrent roles for {username}: {current_roles}")
    
    def list_all_users(self):
        """List all users and their roles"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("REF-Manager User Roles")
        self.stdout.write("=" * 60 + "\n")
        
        profiles = UserProfile.objects.select_related('user').prefetch_related('roles')
        
        if not profiles.exists():
            self.stdout.write(self.style.WARNING("No user profiles found"))
            return
        
        # Group by role count for nicer display
        for profile in profiles.order_by('user__username'):
            username = profile.user.username
            roles = profile.get_role_display()
            
            # Color-code by role
            if profile.is_admin:
                self.stdout.write(
                    self.style.ERROR(f"  {username}: {roles}")
                )
            elif profile.is_observer:
                self.stdout.write(
                    self.style.HTTP_INFO(f"  {username}: {roles}")
                )
            elif profile.is_panel_member:
                self.stdout.write(
                    self.style.WARNING(f"  {username}: {roles}")
                )
            elif profile.is_colleague:
                self.stdout.write(f"  {username}: {roles}")
            else:
                self.stdout.write(
                    self.style.HTTP_NOT_MODIFIED(f"  {username}: {roles}")
                )
        
        self.stdout.write("")
    
    def show_user_details(self, profile):
        """Show detailed information about a user's roles and permissions"""
        username = profile.user.username
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"User: {username}")
        self.stdout.write(f"Email: {profile.user.email or 'Not set'}")
        self.stdout.write("=" * 60 + "\n")
        
        # Roles
        self.stdout.write(self.style.HTTP_INFO("Roles:"))
        roles = profile.roles.all()
        if roles:
            for role in roles:
                self.stdout.write(f"  • {role.name}")
                if role.description:
                    self.stdout.write(f"    {role.description}")
        else:
            self.stdout.write(self.style.WARNING("  No roles assigned"))
        
        # Permissions
        self.stdout.write("\n" + self.style.HTTP_INFO("Permissions:"))
        
        permissions = [
            ('can_view_all_outputs', 'View all outputs'),
            ('can_view_all_colleagues', 'View all colleagues'),
            ('can_view_all_ratings', 'View all ratings'),
            ('can_edit_any_output', 'Edit any output'),
            ('can_delete_any_output', 'Delete any output'),
            ('can_edit_any_rating', 'Edit any rating'),
            ('can_create_outputs', 'Create outputs'),
            ('can_rate_assigned', 'Rate assigned outputs'),
            ('can_unfinalise_ratings', 'Un-finalise ratings'),
            ('can_manage_users', 'Manage users'),
            ('can_assign_panel', 'Assign panel members'),
            ('can_export_data', 'Export data'),
            ('can_import_data', 'Import data'),
        ]
        
        for perm_name, perm_label in permissions:
            has_perm = getattr(profile, perm_name, False)
            if has_perm:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {perm_label}"))
            else:
                self.stdout.write(f"  ✗ {perm_label}")
        
        # Linked colleague
        self.stdout.write("\n" + self.style.HTTP_INFO("Linked Colleague:"))
        if profile.linked_colleague:
            self.stdout.write(f"  {profile.linked_colleague}")
        else:
            self.stdout.write("  Not linked")
        
        self.stdout.write("")
