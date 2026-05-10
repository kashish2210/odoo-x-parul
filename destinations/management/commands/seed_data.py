from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from django.db import transaction

from destinations.models import City, Activity


SAMPLE_CITIES = [
    {"name": "Paris", "country": "France", "region": "Europe", "cost_index": Decimal('120.00'), "popularity": 95, "description": "City of lights."},
    {"name": "Tokyo", "country": "Japan", "region": "Asia", "cost_index": Decimal('140.00'), "popularity": 92, "description": "Culture and neon."},
    {"name": "Bali", "country": "Indonesia", "region": "Asia", "cost_index": Decimal('70.00'), "popularity": 88, "description": "Beach paradise."},
    {"name": "New York", "country": "USA", "region": "North America", "cost_index": Decimal('130.00'), "popularity": 94, "description": "The big apple."},
    {"name": "Reykjavik", "country": "Iceland", "region": "Europe", "cost_index": Decimal('150.00'), "popularity": 75, "description": "Northern lights base."},
    {"name": "Cape Town", "country": "South Africa", "region": "Africa", "cost_index": Decimal('65.00'), "popularity": 78, "description": "Coasts and mountains."},
    {"name": "Sydney", "country": "Australia", "region": "Oceania", "cost_index": Decimal('110.00'), "popularity": 85, "description": "Harbour city."},
    {"name": "Lisbon", "country": "Portugal", "region": "Europe", "cost_index": Decimal('80.00'), "popularity": 80, "description": "Coastal charm."},
    {"name": "Marrakesh", "country": "Morocco", "region": "Africa", "cost_index": Decimal('45.00'), "popularity": 70, "description": "Markets and spice."},
    {"name": "Rio de Janeiro", "country": "Brazil", "region": "South America", "cost_index": Decimal('60.00'), "popularity": 82, "description": "Beaches and carnival."},
    {"name": "Vancouver", "country": "Canada", "region": "North America", "cost_index": Decimal('100.00'), "popularity": 77, "description": "Nature meets city."},
    {"name": "Bangkok", "country": "Thailand", "region": "Asia", "cost_index": Decimal('50.00'), "popularity": 90, "description": "Street food heaven."},
]

ACTIVITY_TEMPLATES = {
    'sightseeing': [
        'City walking tour of {}',
        'Historic landmarks tour in {}',
        'Museum & gallery pass for {}'
    ],
    'food': [
        'Street food tasting in {}',
        'Local cooking class in {}',
        'Wine & dine experience near {}'
    ],
    'adventure': [
        'Paragliding over {}',
        'Guided hike around {}',
        'Kayaking excursion near {}'
    ],
    'other': [
        'Photography walk in {}',
        'Relaxing picnic at popular park in {}'
    ],
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--cities', type=int, default=0, help='Number of cities to ensure (will extend sample list if larger).')
        parser.add_argument('--activities', type=int, default=6, help='Activities to create per city.')
        parser.add_argument('--force', action='store_true', help='If set, existing activities for seeded cities will be removed first.')

    @transaction.atomic
    def handle(self, *args, **options):
        want_cities = options.get('cities') or len(SAMPLE_CITIES)
        activities_per_city = options.get('activities')
        force = options.get('force')

        cities = list(SAMPLE_CITIES)
        idx = 1
        while len(cities) < want_cities:
            cities.append({
                'name': f'City{len(cities)+1}',
                'country': f'Country{idx}',
                'region': 'Global',
                'cost_index': Decimal(str(random.randint(30, 150))),
                'popularity': random.randint(30, 90),
                'description': 'Auto-generated city for local testing.',
            })
            idx += 1

        created_cities = 0
        created_activities = 0

        for c in cities[:want_cities]:
            city_obj, created = City.objects.get_or_create(
                name=c['name'], country=c['country'], defaults={
                    'region': c.get('region', ''),
                    'cost_index': c.get('cost_index', Decimal('0.00')),
                    'popularity_score': c.get('popularity', 0),
                    'description': c.get('description', ''),
                }
            )
            if created:
                created_cities += 1

            if force:
                Activity.objects.filter(city=city_obj).delete()

            for i in range(activities_per_city):
                category = random.choice(list(ACTIVITY_TEMPLATES.keys()))
                template = random.choice(ACTIVITY_TEMPLATES[category])
                name = template.format(city_obj.name)
                desc = f'{category.title()} activity in {city_obj.name}.'
                est_cost = Decimal(str(random.randint(10, 250)))
                duration = random.choice([30, 45, 60, 90, 120])

                activity_obj, acreated = Activity.objects.get_or_create(
                    city=city_obj,
                    name=name,
                    defaults={
                        'description': desc,
                        'category': category,
                        'estimated_cost': est_cost,
                        'duration_minutes': duration,
                    }
                )
                if acreated:
                    created_activities += 1

        self.stdout.write(self.style.SUCCESS(f'Cities ensured: {want_cities} (new {created_cities})'))
        self.stdout.write(self.style.SUCCESS(f'Activities created: {created_activities}'))
