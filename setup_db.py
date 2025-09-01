#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from django.core.management import execute_from_command_line
from fuel_route.models import FuelStation

def setup_database():
    print("🔧 Setting up database...")
    
    # Run migrations
    print("1. Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("   ✅ Migrations completed")
    except Exception as e:
        print(f"   ❌ Migration error: {e}")
        return False
    
    # Check if tables exist
    print("2. Checking database tables...")
    try:
        count = FuelStation.objects.count()
        print(f"   ✅ FuelStation table exists, count: {count}")
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
        return False
    
    # Load fuel station data
    print("3. Loading fuel station data...")
    try:
        execute_from_command_line(['manage.py', 'load_fuel_data', 'fuel_stations.csv', '--skip-geocoding'])
        print("   ✅ Fuel station data loaded")
    except Exception as e:
        print(f"   ❌ Data loading error: {e}")
        return False
    
    # Final check
    print("4. Final database check...")
    try:
        count = FuelStation.objects.count()
        print(f"   ✅ Total fuel stations: {count}")
        return True
    except Exception as e:
        print(f"   ❌ Final check failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n🎉 Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
