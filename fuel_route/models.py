from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FuelStation(models.Model):
    """Model representing a fuel station with pricing and location data"""
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the fuel station"
    )
    address = models.CharField(
        max_length=500,
        help_text="Street address or location description"
    )
    city = models.CharField(
        max_length=100,
        help_text="City name"
    )
    state = models.CharField(
        max_length=2,
        help_text="Two-letter state code (e.g., CA, NY)"
    )
    rack_id = models.IntegerField(
        unique=True,
        help_text="Unique rack identifier"
    )
    retail_price = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0.001), MaxValueValidator(99.999)],
        help_text="Retail fuel price per gallon in USD"
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Latitude coordinate"
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Longitude coordinate"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fuel_route'
        db_table = 'fuel_stations'
        verbose_name = 'Fuel Station'
        verbose_name_plural = 'Fuel Stations'
        ordering = ['state', 'city', 'name']
        indexes = [
            models.Index(fields=['latitude', 'longitude'], name='location_idx'),
            models.Index(fields=['state', 'city'], name='state_city_idx'),
            models.Index(fields=['retail_price'], name='price_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} (${self.retail_price}/gal)"
    
    def get_coordinates(self):
        """Return coordinates as tuple if available"""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None
    
    def get_full_address(self):
        """Return formatted full address"""
        parts = [self.address, self.city, self.state]
        return ", ".join([part for part in parts if part.strip()])
    
    @property
    def has_coordinates(self):
        """Check if station has valid coordinates"""
        return self.latitude is not None and self.longitude is not None
