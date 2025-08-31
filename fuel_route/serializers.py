from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    """Serializer for route request data"""
    
    start_location = serializers.CharField(
        max_length=200,
        help_text="Start city, state or full address (e.g., 'New York, NY' or 'Chicago, IL')",
        error_messages={
            'required': 'Start location is required',
            'blank': 'Start location cannot be empty'
        }
    )
    end_location = serializers.CharField(
        max_length=200,
        help_text="End city, state or full address (e.g., 'Los Angeles, CA' or 'Miami, FL')",
        error_messages={
            'required': 'End location is required',
            'blank': 'End location cannot be empty'
        }
    )
    
    def validate_start_location(self, value):
        """Validate start location format"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Start location must be at least 3 characters long")
        return value
    
    def validate_end_location(self, value):
        """Validate end location format"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("End location must be at least 3 characters long")
        return value
    
    def validate(self, data):
        """Validate that start and end locations are different"""
        start = data.get('start_location', '').strip().lower()
        end = data.get('end_location', '').strip().lower()
        
        if start == end:
            raise serializers.ValidationError("Start and end locations must be different")
        
        return data


class FuelStationSerializer(serializers.Serializer):
    """Serializer for fuel station data in API responses"""
    
    name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    price = serializers.DecimalField(max_digits=5, decimal_places=3)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_from_route = serializers.FloatField(help_text="Distance from route in miles")


class RouteResponseSerializer(serializers.Serializer):
    """Serializer for route response data"""
    
    total_distance_miles = serializers.FloatField(
        help_text="Total route distance in miles"
    )
    total_fuel_cost = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Total estimated fuel cost in USD"
    )
    total_fuel_needed_gallons = serializers.FloatField(
        help_text="Total fuel needed in gallons (based on 10 MPG)"
    )
    fuel_stops = FuelStationSerializer(
        many=True,
        help_text="List of recommended fuel stops along the route"
    )
    route_polyline = serializers.CharField(
        help_text="Route geometry data for mapping"
    )
    route_coordinates = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        help_text="Array of [latitude, longitude] coordinate pairs defining the route"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    
    error = serializers.CharField(help_text="Error message")
    details = serializers.DictField(
        required=False,
        help_text="Additional error details"
    )
