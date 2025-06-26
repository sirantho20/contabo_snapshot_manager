#!/usr/bin/env python3
"""
Development setup script for Contabo Snapshot Manager Django project.
"""
import os
import sys
import subprocess
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snapshot_manager.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Setup the development environment."""
    print("Setting up Contabo Snapshot Manager Django project...")
    
    # Run migrations
    print("Running Django migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    print("Creating superuser (if needed)...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            print("Superuser created: admin/admin")
        else:
            print("Superuser already exists")
    except Exception as e:
        print(f"Error creating superuser: {e}")
    
    # Setup scheduled task
    print("Setting up scheduled task...")
    execute_from_command_line(['manage.py', 'run_snapshot_job', '--schedule'])
    
    print("\nSetup complete!")
    print("\nTo run the development server:")
    print("  python manage.py runserver")
    print("\nTo run the snapshot job manually:")
    print("  python manage.py run_snapshot_job")
    print("\nTo start the Django Q cluster:")
    print("  python -m django_q.cluster")

if __name__ == "__main__":
    main() 