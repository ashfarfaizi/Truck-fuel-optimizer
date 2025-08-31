#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

print("Testing Django server startup...")

try:
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
    django.setup()
    print("✅ Django setup successful")
    
    # Test server startup
    print("Starting server...")
    sys.argv = ['manage.py', 'runserver', '8000']
    execute_from_command_line(sys.argv)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
