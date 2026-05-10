"""
Management command to geocode cities that don't have lat/lng.
Uses the free Nominatim (OpenStreetMap) geocoding API.

Usage:
    python manage.py geocode_cities
"""
import time
import urllib.request
import json

from django.core.management.base import BaseCommand
from destinations.models import City


class Command(BaseCommand):
    help = 'Geocode all cities that do not have latitude/longitude set.'

    def handle(self, *args, **options):
        cities = City.objects.filter(latitude__isnull=True)
        total = cities.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('All cities already geocoded!'))
            return

        self.stdout.write(f'Geocoding {total} cities...')

        for i, city in enumerate(cities, 1):
            query = f"{city.name}, {city.country}"
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"

            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Traveloop/1.0 (student project)'
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())

                if data:
                    city.latitude = float(data[0]['lat'])
                    city.longitude = float(data[0]['lon'])
                    city.save(update_fields=['latitude', 'longitude'])
                    self.stdout.write(
                        self.style.SUCCESS(f'  [{i}/{total}] {city.name} -> {city.latitude}, {city.longitude}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  [{i}/{total}] {city.name} -> NOT FOUND')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [{i}/{total}] {city.name} -> ERROR: {e}')
                )

            # Nominatim rate limit: 1 request per second
            time.sleep(1.1)

        self.stdout.write(self.style.SUCCESS('Done!'))
