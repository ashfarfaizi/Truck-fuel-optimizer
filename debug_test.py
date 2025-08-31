#!/usr/bin/env python
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Current directory:", os.getcwd())
print("Python path:", sys.path[:3])

# Try to import Django settings
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
    import django
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Try to import the models module
try:
    import fuel_route.models
    print("✅ fuel_route.models imported")
    print("Available in models:", [attr for attr in dir(fuel_route.models) if not attr.startswith('_')])
except Exception as e:
    print(f"❌ fuel_route.models import failed: {e}")

# Try to import specific model
try:
    from fuel_route.models import FuelStation
    print("✅ FuelStation model imported successfully")
    print("FuelStation fields:", [f.name for f in FuelStation._meta.fields])
except Exception as e:
    print(f"❌ FuelStation import failed: {e}")
    
    # Try to see what's in the models module
    try:
        import fuel_route.models as models
        print("Models module contents:")
        for attr in dir(models):
            if not attr.startswith('_'):
                print(f"  {attr}: {getattr(models, attr)}")
    except Exception as e2:
        print(f"❌ Could not inspect models module: {e2}")

print("Debug test completed")
