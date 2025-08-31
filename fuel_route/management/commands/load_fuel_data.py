import csv
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from fuel_route.models import FuelStation


class Command(BaseCommand):
    """
    Django management command to load fuel station data from CSV file
    
    Usage:
        python manage.py load_fuel_data fuel_stations.csv
        python manage.py load_fuel_data fuel_stations.csv --skip-geocoding
        python manage.py load_fuel_data fuel_stations.csv --update-existing
    """
    
    help = 'Load fuel station data from CSV file with geocoding'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing fuel station data'
        )
        
        parser.add_argument(
            '--skip-geocoding',
            action='store_true',
            help='Skip geocoding step (faster but no coordinates)',
        )
        
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing stations instead of skipping duplicates',
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch (default: 100)',
        )
        
        parser.add_argument(
            '--geocode-delay',
            type=float,
            default=0.1,
            help='Delay between geocoding requests in seconds (default: 0.1)',
        )

    def __init__(self):
        super().__init__()
        self.geolocator = Nominatim(user_agent="fuel_station_loader")
        self.geocode_cache = {}
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'geocoded': 0,
            'geocode_failed': 0
        }

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        skip_geocoding = options['skip_geocoding']
        update_existing = options['update_existing']
        batch_size = options['batch_size']
        geocode_delay = options['geocode_delay']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting to load fuel station data from: {csv_file}')
        )
        
        if skip_geocoding:
            self.stdout.write(
                self.style.WARNING('Geocoding is disabled - stations will not have coordinates')
            )
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                self.stdout.write(f'Successfully opened CSV file: {csv_file}')
                self.process_csv_file(
                    file, skip_geocoding, update_existing, batch_size, geocode_delay
                )
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')
        
        self.print_final_stats()

    def process_csv_file(self, file, skip_geocoding, update_existing, batch_size, geocode_delay):
        """Process the CSV file in batches"""
        reader = csv.reader(file)
        
        # Try to detect if first row is header
        first_row = next(reader, None)
        if first_row and self.is_header_row(first_row):
            self.stdout.write('Detected header row, skipping...')
        else:
            # Reset file pointer if first row contains data
            file.seek(0)
            reader = csv.reader(file)
        
        batch = []
        
        for row_num, row in enumerate(reader, 1):
            self.stdout.write(f'Processing row {row_num}: {row[:3]}...')  # Show first 3 columns
            if len(row) < 6:  # Need at least 6 columns for basic data
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Insufficient columns ({len(row)}), skipping')
                )
                continue
            
            station_data = self.parse_csv_row(row, row_num)
            if station_data:
                batch.append(station_data)
                self.stdout.write(f'Added station: {station_data["name"]}')
            else:
                self.stdout.write(f'Failed to parse row {row_num}')
            
            # Process batch when it reaches the specified size
            if len(batch) >= batch_size:
                self.process_batch(batch, skip_geocoding, update_existing, geocode_delay)
                batch = []
        
        # Process remaining records
        if batch:
            self.process_batch(batch, skip_geocoding, update_existing, geocode_delay)

    def is_header_row(self, row):
        """Try to detect if the row is a header row"""
        if len(row) < 3:
            return False
        
        # Check if first column contains header text
        first_col = row[0].strip().lower() if row[0] else ''
        return first_col in ['name', 'station', 'location', 'fuel']

    def parse_csv_row(self, row, row_num):
        """Parse a single CSV row into station data"""
        try:
            # Expected CSV structure: name,address,city,state,rack_id,retail_price
            if len(row) < 6:
                return None
            
            # Extract fields directly from CSV columns
            name = row[0].strip() if len(row) > 0 else 'Unknown Station'
            address = row[1].strip() if len(row) > 1 else ''
            city = row[2].strip() if len(row) > 2 else 'Unknown'
            state = row[3].strip() if len(row) > 3 else 'XX'
            
            # Get numeric fields
            try:
                rack_id = int(float(row[4])) if len(row) > 4 else 0
                retail_price = float(row[5]) if len(row) > 5 else 0.0
            except (ValueError, IndexError):
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Invalid numeric data, using defaults')
                )
                rack_id = 0
                retail_price = 0.0
            
            return {
                'name': name[:200],  # Truncate to fit model field
                'address': address[:500],
                'city': city[:100],
                'state': state[:2],
                'rack_id': rack_id,
                'retail_price': retail_price,
                'raw_row': row  # Keep for debugging
            }
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Row {row_num}: Error parsing - {e}')
            )
            return None

    @transaction.atomic
    def process_batch(self, batch, skip_geocoding, update_existing, geocode_delay):
        """Process a batch of station data"""
        for station_data in batch:
            self.stats['processed'] += 1
            
            try:
                # Check if station already exists
                existing_station = None
                if station_data['rack_id']:
                    try:
                        existing_station = FuelStation.objects.get(rack_id=station_data['rack_id'])
                    except FuelStation.DoesNotExist:
                        existing_station = None
                
                if existing_station and not update_existing:
                    self.stats['skipped'] += 1
                    continue
                
                # Geocode location if not skipping
                latitude = None
                longitude = None
                
                if not skip_geocoding:
                    latitude, longitude = self.geocode_station(
                        station_data['city'], 
                        station_data['state'],
                        geocode_delay
                    )
                
                # Create or update station
                if existing_station and update_existing:
                    # Update existing
                    existing_station.name = station_data['name']
                    existing_station.address = station_data['address']
                    existing_station.city = station_data['city']
                    existing_station.state = station_data['state']
                    existing_station.retail_price = station_data['retail_price']
                    if latitude is not None:
                        existing_station.latitude = latitude
                        existing_station.longitude = longitude
                    existing_station.save()
                    self.stats['updated'] += 1
                else:
                    # Create new station
                    FuelStation.objects.create(
                        name=station_data['name'],
                        address=station_data['address'],
                        city=station_data['city'],
                        state=station_data['state'],
                        rack_id=station_data['rack_id'],
                        retail_price=station_data['retail_price'],
                        latitude=latitude,
                        longitude=longitude
                    )
                    self.stats['created'] += 1
                
                # Progress indicator
                if self.stats['processed'] % 50 == 0:
                    self.stdout.write(f'Processed {self.stats["processed"]} records...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing station {station_data["name"]}: {e}')
                )
                self.stats['skipped'] += 1

    def geocode_station(self, city, state, delay=0.1):
        """Geocode a station location with caching and error handling"""
        if not city or not state or city == 'Unknown' or state == 'XX':
            return None, None
        
        # Create cache key
        location_key = f"{city.strip()}, {state.strip()}"
        
        # Check cache first
        if location_key in self.geocode_cache:
            return self.geocode_cache[location_key]
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(delay)
            
            # Geocode with country bias
            location_query = f"{city}, {state}, USA"
            location = self.geolocator.geocode(location_query, timeout=10)
            
            if location:
                coords = (location.latitude, location.longitude)
                self.geocode_cache[location_key] = coords
                self.stats['geocoded'] += 1
                
                if self.stats['geocoded'] % 10 == 0:
                    self.stdout.write(f'Geocoded {self.stats["geocoded"]} locations...')
                
                return coords
            else:
                self.geocode_cache[location_key] = (None, None)
                self.stats['geocode_failed'] += 1
                return None, None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.stdout.write(
                self.style.WARNING(f'Geocoding failed for {location_key}: {e}')
            )
            self.geocode_cache[location_key] = (None, None)
            self.stats['geocode_failed'] += 1
            return None, None
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected geocoding error for {location_key}: {e}')
            )
            self.geocode_cache[location_key] = (None, None)
            self.stats['geocode_failed'] += 1
            return None, None

    def print_final_stats(self):
        """Print final processing statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('FUEL STATION DATA LOADING COMPLETE'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'Records processed: {self.stats["processed"]}')
        self.stdout.write(f'Stations created: {self.stats["created"]}')
        self.stdout.write(f'Stations updated: {self.stats["updated"]}')
        self.stdout.write(f'Records skipped: {self.stats["skipped"]}')
        self.stdout.write(f'Locations geocoded: {self.stats["geocoded"]}')
        self.stdout.write(f'Geocoding failures: {self.stats["geocode_failed"]}')
        
        total_stations = FuelStation.objects.count()
        stations_with_coords = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        
        self.stdout.write(f'\nTotal stations in database: {total_stations}')
        self.stdout.write(f'Stations with coordinates: {stations_with_coords}')
        
        if total_stations > 0:
            coord_percentage = (stations_with_coords / total_stations) * 100
            self.stdout.write(f'Geocoding success rate: {coord_percentage:.1f}%')
        
        self.stdout.write('\n' + self.style.SUCCESS('Ready to use fuel route API!'))
        self.stdout.write('='*50)