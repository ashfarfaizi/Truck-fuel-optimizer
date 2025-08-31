#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

print("Django setup complete")

# Try to import the app
try:
    from fuel_route import models
    print("✅ fuel_route.models imported")
    
    # Check what's in the models module
    print("Models module contents:")
    for attr in dir(models):
        if not attr.startswith('_'):
            print(f"  {attr}")
            
    # Try to access the model directly
    if hasattr(models, 'FuelStation'):
        print("✅ FuelStation found in models")
        FuelStation = models.FuelStation
        print(f"Model fields: {[f.name for f in FuelStation._meta.fields]}")
    else:
        print("❌ FuelStation not found in models")
        
except Exception as e:
    print(f"❌ Error importing models: {e}")

print("Test completed")
