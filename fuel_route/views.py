from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import requests
import json
import time
import hashlib
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from .models import FuelStation
from .serializers import RouteRequestSerializer, RouteResponseSerializer, ErrorResponseSerializer


class FuelRouteView(APIView):
    """
    API View to calculate optimal fuel stops along a route between two US locations.
    
    This view:
    1. Takes start and end locations in the USA
    2. Calculates the optimal route using external mapping API
    3. Finds fuel stations along the route considering 500-mile vehicle range
    4. Optimizes fuel stops based on price and distance from route
    5. Calculates total fuel cost assuming 10 miles per gallon
    """
    
    def __init__(self):
        super().__init__()
        self.geolocator = Nominatim(user_agent="fuel_route_optimizer_v1")
        self.max_range_miles = 500
        self.miles_per_gallon = 10
        self.max_station_distance_miles = 30
    
    def get_cache_key(self, start_location, end_location):
        """Generate cache key for route data"""
        key_string = f"route_{start_location}_{end_location}".lower().replace(" ", "_")
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def get_cached_response(self, start_location, end_location):
        """Get cached route response if available"""
        cache_key = self.get_cache_key(start_location, end_location)
        return cache.get(cache_key)
    
    def cache_response(self, start_location, end_location, response_data, timeout=3600):
        """Cache route response for 1 hour"""
        cache_key = self.get_cache_key(start_location, end_location)
        cache.set(cache_key, response_data, timeout)
    
    def geocode_location(self, location_string):
        """
        Convert location string to coordinates using Nominatim geocoder
        Returns tuple (latitude, longitude) or None if not found
        """
        try:
            # Check cache first
            cache_key = f"geocode_{hashlib.md5(location_string.encode()).hexdigest()[:12]}"
            cached_coords = cache.get(cache_key)
            if cached_coords:
                return cached_coords
            
            # Geocode with USA bias
            location_query = f"{location_string}, USA"
            location = self.geolocator.geocode(location_query, timeout=10)
            
            if location:
                coords = (location.latitude, location.longitude)
                # Cache geocoding result for 24 hours
                cache.set(cache_key, coords, 86400)
                return coords
                
        except Exception as e:
            print(f"Geocoding error for '{location_string}': {e}")
        
        return None
    
    def get_route_from_openrouteservice(self, start_coords, end_coords):
        """
        Get route using OpenRouteService Directions API (free tier)
        This makes exactly ONE external API call as required
        """
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        # IMPORTANT: Replace with your actual OpenRouteService API key
        # Get free key from: https://openrouteservice.org/dev/#/signup
        # For testing, we'll use a fallback approach
        headers = {
            'Accept': 'application/json, application/geo+json',
            'Authorization': 'Bearer 5b3ce3597851110001cf6248YOUR_API_KEY_HERE',  # ⚠️ REPLACE THIS
            'Content-Type': 'application/json'
        }
        
        body = {
            "coordinates": [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]],
            "format": "geojson",
            "instructions": False,
            "geometry_simplify": True
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                route = data['features'][0]
                coordinates = route['geometry']['coordinates']
                distance_meters = route['properties']['summary']['distance']
                distance_miles = distance_meters * 0.000621371
                
                # Convert coordinates from [lng, lat] to [lat, lng] format
                route_coords = [[coord[1], coord[0]] for coord in coordinates]
                
                return {
                    'coordinates': route_coords,
                    'distance_miles': distance_miles,
                    'polyline': route['geometry'],
                    'api_used': 'openrouteservice'
                }
            else:
                print(f"OpenRouteService API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"OpenRouteService API request failed: {e}")
        
        # Fallback to straight-line route if API fails
        return self.create_fallback_route(start_coords, end_coords)
    
    def create_fallback_route(self, start_coords, end_coords):
        """
        Create a fallback straight-line route when external API is unavailable
        """
        distance_miles = geodesic(start_coords, end_coords).miles
        
        # Create intermediate points for better fuel stop placement
        num_segments = max(3, int(distance_miles / 200))  # Segment every ~200 miles
        coordinates = []
        
        for i in range(num_segments + 1):
            ratio = i / num_segments
            lat = start_coords[0] + (end_coords[0] - start_coords[0]) * ratio
            lng = start_coords[1] + (end_coords[1] - start_coords[1]) * ratio
            coordinates.append([lat, lng])
        
        return {
            'coordinates': coordinates,
            'distance_miles': distance_miles,
            'polyline': f"Fallback straight-line route with {num_segments} segments",
            'api_used': 'fallback'
        }
    
    def get_nearby_fuel_stations(self, route_coordinates):
        """
        Get fuel stations from database that are near the route
        Returns stations within max_station_distance_miles of any route point
        """
        # Get all stations with valid coordinates
        all_stations = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).values(
            'name', 'address', 'city', 'state', 'retail_price',
            'latitude', 'longitude', 'rack_id'
        )
        
        nearby_stations = []
        
        # Sample route points for performance (every 10th point or so)
        sample_points = route_coordinates[::max(1, len(route_coordinates) // 20)]
        
        for station in all_stations:
            station_coords = (station['latitude'], station['longitude'])
            min_distance_to_route = float('inf')
            
            # Find minimum distance from station to any sampled route point
            for route_point in sample_points:
                distance = geodesic(route_point, station_coords).miles
                min_distance_to_route = min(min_distance_to_route, distance)
                
                # Early exit if station is very close
                if min_distance_to_route < 5:
                    break
            
            # Include station if within reasonable distance of route
            if min_distance_to_route <= self.max_station_distance_miles:
                station['distance_from_route'] = round(min_distance_to_route, 2)
                nearby_stations.append(station)
        
        return nearby_stations
    
    def find_optimal_fuel_stops(self, route_coordinates, nearby_stations):
        """
        Find optimal fuel stops along the route considering:
        1. Vehicle range limitation (500 miles)
        2. Fuel price optimization
        3. Distance from route minimization
        """
        if not nearby_stations:
            return [], 0
        
        fuel_stops = []
        total_distance = 0
        current_range = 0
        
        # Calculate total route distance
        for i in range(len(route_coordinates) - 1):
            segment_distance = geodesic(route_coordinates[i], route_coordinates[i + 1]).miles
            total_distance += segment_distance
        
        # Calculate cumulative distances along route
        route_distances = [0]
        for i in range(len(route_coordinates) - 1):
            segment_distance = geodesic(route_coordinates[i], route_coordinates[i + 1]).miles
            route_distances.append(route_distances[-1] + segment_distance)
        
        current_distance_covered = 0
        last_fuel_distance = 0
        
        while current_distance_covered < total_distance:
            # Calculate remaining range and distance to cover
            distance_since_fuel = current_distance_covered - last_fuel_distance
            remaining_range = self.max_range_miles - distance_since_fuel
            
            # Look for fuel stop when we've used 80% of range or approaching end
            need_fuel_soon = (
                remaining_range <= self.max_range_miles * 0.2 or
                (total_distance - current_distance_covered) > remaining_range
            )
            
            if need_fuel_soon:
                # Find route segment to search for fuel stations
                search_start = max(0, current_distance_covered - 50)  # Look back 50 miles
                search_end = min(total_distance, current_distance_covered + remaining_range)
                
                # Get route coordinates for this search segment
                search_coords = self.get_route_segment_coords(
                    route_coordinates, route_distances, search_start, search_end
                )
                
                # Find best station in this segment
                best_station = self.find_best_station_in_segment(search_coords, nearby_stations)
                
                if best_station:
                    fuel_stops.append({
                        'name': best_station['name'],
                        'address': best_station.get('address', ''),
                        'city': best_station['city'],
                        'state': best_station['state'],
                        'price': float(best_station['retail_price']),
                        'latitude': best_station['latitude'],
                        'longitude': best_station['longitude'],
                        'distance_from_route': best_station['distance_from_route']
                    })
                    
                    # Reset range after fuel stop
                    last_fuel_distance = current_distance_covered
            
            # Move forward along route
            current_distance_covered += 100  # Check every 100 miles
        
        return fuel_stops, total_distance
    
    def get_route_segment_coords(self, route_coordinates, route_distances, start_dist, end_dist):
        """Get coordinates for a specific distance segment of the route"""
        segment_coords = []
        
        for i, distance in enumerate(route_distances):
            if start_dist <= distance <= end_dist:
                segment_coords.append(route_coordinates[i])
        
        return segment_coords if segment_coords else route_coordinates
    
    def find_best_station_in_segment(self, segment_coords, nearby_stations):
        """
        Find the best fuel station in a route segment
        Scoring considers both price and distance from route
        """
        candidates = []
        
        for station in nearby_stations:
            station_coords = (station['latitude'], station['longitude'])
            min_distance = float('inf')
            
            # Find minimum distance to segment
            for coord in segment_coords:
                distance = geodesic(coord, station_coords).miles
                min_distance = min(min_distance, distance)
            
            if min_distance <= self.max_station_distance_miles:
                # Calculate composite score: lower is better
                # Weight: 60% price, 40% distance
                price_score = float(station['retail_price'])
                distance_score = min_distance / self.max_station_distance_miles
                composite_score = (price_score * 0.6) + (distance_score * 0.4)
                
                candidates.append({
                    **station,
                    'distance_from_route': round(min_distance, 2),
                    'score': composite_score
                })
        
        if not candidates:
            return None
        
        # Return best scoring station
        candidates.sort(key=lambda x: x['score'])
        return candidates[0]
    
    def post(self, request):
        """
        Main API endpoint for route optimization
        
        POST /api/route/
        {
            "start_location": "New York, NY",
            "end_location": "Los Angeles, CA"
        }
        """
        # Validate request data
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start_location = serializer.validated_data['start_location'].strip()
        end_location = serializer.validated_data['end_location'].strip()
        
        # Check cache for existing result
        cached_response = self.get_cached_response(start_location, end_location)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)
        
        # Geocode locations
        start_coords = self.geocode_location(start_location)
        end_coords = self.geocode_location(end_location)
        
        if not start_coords:
            return Response(
                {'error': f'Could not find coordinates for start location: "{start_location}". Please check spelling and ensure it\'s a valid US location.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not end_coords:
            return Response(
                {'error': f'Could not find coordinates for end location: "{end_location}". Please check spelling and ensure it\'s a valid US location.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get route (single external API call as required)
        route_data = self.get_route_from_openrouteservice(start_coords, end_coords)
        
        # Get nearby fuel stations from database
        nearby_stations = self.get_nearby_fuel_stations(route_data['coordinates'])
        
        # Find optimal fuel stops
        fuel_stops, total_distance = self.find_optimal_fuel_stops(
            route_data['coordinates'], nearby_stations
        )
        
        # Calculate fuel consumption and costs
        fuel_needed_gallons = total_distance / self.miles_per_gallon
        
        if fuel_stops:
            # Distribute fuel consumption across stops
            gallons_per_stop = fuel_needed_gallons / len(fuel_stops)
            total_fuel_cost = sum(stop['price'] * gallons_per_stop for stop in fuel_stops)
        else:
            total_fuel_cost = 0
            # If no fuel stops found, add a note
            if total_distance > self.max_range_miles:
                fuel_stops = [{
                    'name': 'WARNING: No fuel stations found along route',
                    'address': 'Please check route or add fuel stations to database',
                    'city': 'N/A',
                    'state': 'N/A',
                    'price': 0.0,
                    'latitude': 0.0,
                    'longitude': 0.0,
                    'distance_from_route': 0.0
                }]
        
        # Prepare response data
        response_data = {
            'total_distance_miles': round(total_distance, 2),
            'total_fuel_cost': round(total_fuel_cost, 2),
            'total_fuel_needed_gallons': round(fuel_needed_gallons, 2),
            'fuel_stops': fuel_stops,
            'route_polyline': str(route_data['polyline']),
            'route_coordinates': route_data['coordinates'][:50],  # Limit for response size
            'api_info': {
                'route_source': route_data.get('api_used', 'unknown'),
                'stations_considered': len(nearby_stations),
                'vehicle_range_miles': self.max_range_miles,
                'fuel_efficiency_mpg': self.miles_per_gallon
            }
        }
        
        # Cache successful response
        self.cache_response(start_location, end_location, response_data)
        
        return Response(response_data, status=status.HTTP_200_OK)