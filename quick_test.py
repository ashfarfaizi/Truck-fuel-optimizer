#!/usr/bin/env python
import os
import sys
import django

print("Starting Django test...")

try:
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
    django.setup()
    print("✅ Django setup successful")
    
    # Test basic imports
    from fuel_route.models import FuelStation
    print("✅ Models imported successfully")
    
    from fuel_route.views import FuelRouteView
    print("✅ Views imported successfully")
    
    from fuel_route.serializers import RouteRequestSerializer
    print("✅ Serializers imported successfully")
    
    # Test database connection
    count = FuelStation.objects.count()
    print(f"✅ Database working - {count} stations in DB")
    
    print("\n🎉 All imports successful! Ready to start server.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
