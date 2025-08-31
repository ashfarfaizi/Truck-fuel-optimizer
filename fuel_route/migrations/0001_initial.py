# Generated manually for initial FuelStation model

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuelStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the fuel station', max_length=200)),
                ('address', models.CharField(help_text='Street address or location description', max_length=500)),
                ('city', models.CharField(help_text='City name', max_length=100)),
                ('state', models.CharField(help_text='Two-letter state code (e.g., CA, NY)', max_length=2)),
                ('rack_id', models.IntegerField(help_text='Unique rack identifier', unique=True)),
                ('retail_price', models.DecimalField(decimal_places=3, help_text='Retail fuel price per gallon in USD', max_digits=5, validators=[django.core.validators.MinValueValidator(0.001), django.core.validators.MaxValueValidator(99.999)])),
                ('latitude', models.FloatField(blank=True, help_text='Latitude coordinate', null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('longitude', models.FloatField(blank=True, help_text='Longitude coordinate', null=True, validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Fuel Station',
                'verbose_name_plural': 'Fuel Stations',
                'db_table': 'fuel_stations',
                'ordering': ['state', 'city', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='fuelstation',
            index=models.Index(fields=['latitude', 'longitude'], name='location_idx'),
        ),
        migrations.AddIndex(
            model_name='fuelstation',
            index=models.Index(fields=['state', 'city'], name='state_city_idx'),
        ),
        migrations.AddIndex(
            model_name='fuelstation',
            index=models.Index(fields=['retail_price'], name='price_idx'),
        ),
    ]
