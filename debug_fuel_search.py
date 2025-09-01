#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_project.settings')
django.setup()

from fuel_route.models import FuelStation
from fuel_route.views import FuelRouteView
from geopy.distance import geodesic

def main():
    print("Debugging fuel station search...")
    
    # Get PA fuel stations
    pa_stations = FuelStation.objects.filter(state='PA')
    print(f"PA fuel stations: {pa_stations.count()}")
    
    for station in pa_stations:
        print(f"- {station.name}: {station.city}, PA ({station.latitude}, {station.longitude})")
    
    # Create a route from Philadelphia to Pittsburgh
    route_coords = [
        [39.9526, -75.1652],  # Philadelphia
        [40.4406, -79.9959]   # Pittsburgh
    ]
    
    print(f"\nRoute: Philadelphia ({route_coords[0]}) to Pittsburgh ({route_coords[1]})")
    
    # Calculate distances from route to each station
    print("\nDistances from route to PA stations:")
    for station in pa_stations:
        station_coords = (station.latitude, station.longitude)
        
        # Calculate distance to each route point
        min_distance = float('inf')
        for route_point in route_coords:
            distance = geodesic(route_point, station_coords).miles
            min_distance = min(min_distance, distance)
        
        print(f"- {station.name}: {min_distance:.2f} miles from route")
    
    # Test the view's fuel station search
    print("\nTesting view's fuel station search...")
    view = FuelRouteView()
    
    # Create a more detailed route with intermediate points
    detailed_route = [
        [39.9526, -75.1652],  # Philadelphia
        [40.0, -77.5],        # Intermediate point
        [40.2, -78.0],        # Intermediate point
        [40.4, -78.5],        # Intermediate point
        [40.4406, -79.9959]   # Pittsburgh
    ]
    
    nearby_stations = view.get_nearby_fuel_stations(detailed_route)
    print(f"Found {len(nearby_stations)} nearby stations")
    
    for station in nearby_stations:
        print(f"- {station['name']}: ${station['retail_price']}/gal, {station['distance_from_route']} miles from route")

if __name__ == "__main__":
    main()
