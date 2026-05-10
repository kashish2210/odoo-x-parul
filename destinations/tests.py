from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from destinations.models import Activity, City
from trips.models import Stop, StopActivity, Trip


User = get_user_model()


class ActivitySearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='planner', password='testpass123')
        self.client.force_login(self.user)

        self.city_a = City.objects.create(
            name='Lisbon',
            country='Portugal',
            region='Europe',
            cost_index=Decimal('80.00'),
            popularity_score=80,
            description='Coastal city',
        )
        self.city_b = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            cost_index=Decimal('140.00'),
            popularity_score=90,
            description='Busy city',
        )

        self.activity_lisbon_food = Activity.objects.create(
            city=self.city_a,
            name='Lisbon Food Tour',
            description='Taste local pastries',
            category=Activity.CATEGORY_FOOD,
            estimated_cost=Decimal('35.00'),
            duration_minutes=90,
        )
        self.activity_lisbon_walk = Activity.objects.create(
            city=self.city_a,
            name='Lisbon Walking Tour',
            description='Walk the hills',
            category=Activity.CATEGORY_SIGHTSEEING,
            estimated_cost=Decimal('15.00'),
            duration_minutes=60,
        )
        self.activity_tokyo_adventure = Activity.objects.create(
            city=self.city_b,
            name='Tokyo Night Run',
            description='Run through neon streets',
            category=Activity.CATEGORY_ADVENTURE,
            estimated_cost=Decimal('45.00'),
            duration_minutes=120,
        )

    def test_filters_search_and_sort_results(self):
        response = self.client.get(
            reverse('destinations:activity-search'),
            {
                'q': 'Lisbon',
                'category': Activity.CATEGORY_FOOD,
                'country': 'Portugal',
                'region': 'Europe',
                'min_cost': '20',
                'max_cost': '40',
                'min_duration': '60',
                'max_duration': '120',
                'sort': 'cost_low',
            },
        )

        self.assertEqual(response.status_code, 200)
        activities = list(response.context['activities'])
        self.assertEqual(activities, [self.activity_lisbon_food])
        self.assertEqual(response.context['filters']['q'], 'Lisbon')
        self.assertEqual(response.context['filters']['sort'], 'cost_low')

    def test_selected_stop_only_shows_owned_stop(self):
        trip = Trip.objects.create(
            user=self.user,
            name='Portugal Trip',
            start_date='2026-06-01',
            end_date='2026-06-08',
        )
        stop = Stop.objects.create(
            trip=trip,
            city=self.city_a,
            arrival_date='2026-06-02',
            departure_date='2026-06-04',
            order=1,
        )

        response = self.client.get(reverse('destinations:activity-search'), {'stop': stop.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_stop'], stop)
        self.assertEqual(response.context['selected_trip'], trip)


class StopActivityFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')

        self.city = City.objects.create(
            name='Cape Town',
            country='South Africa',
            region='Africa',
            cost_index=Decimal('65.00'),
            popularity_score=78,
            description='Coastal city',
        )
        self.trip = Trip.objects.create(
            user=self.owner,
            name='Cape Trip',
            start_date='2026-07-01',
            end_date='2026-07-07',
        )
        self.stop = Stop.objects.create(
            trip=self.trip,
            city=self.city,
            arrival_date='2026-07-02',
            departure_date='2026-07-04',
            order=1,
        )
        self.activity = Activity.objects.create(
            city=self.city,
            name='Table Mountain Hike',
            description='Sunrise hike',
            category=Activity.CATEGORY_ADVENTURE,
            estimated_cost=Decimal('50.00'),
            duration_minutes=180,
        )

    def test_owner_can_add_and_remove_activity(self):
        self.client.force_login(self.owner)

        add_response = self.client.post(
            reverse('destinations:activity-add'),
            {
                'stop_id': self.stop.id,
                'activity_id': self.activity.id,
                'next': f"{reverse('destinations:activity-search')}?stop={self.stop.id}",
            },
        )
        self.assertEqual(add_response.status_code, 302)
        self.assertTrue(StopActivity.objects.filter(stop=self.stop, activity=self.activity).exists())

        remove_response = self.client.post(
            reverse('destinations:activity-remove'),
            {
                'stop_id': self.stop.id,
                'activity_id': self.activity.id,
                'next': f"{reverse('destinations:activity-search')}?stop={self.stop.id}",
            },
        )
        self.assertEqual(remove_response.status_code, 302)
        self.assertFalse(StopActivity.objects.filter(stop=self.stop, activity=self.activity).exists())

    def test_non_owner_gets_forbidden_for_modifications(self):
        self.client.force_login(self.other_user)

        add_response = self.client.post(
            reverse('destinations:activity-add'),
            {'stop_id': self.stop.id, 'activity_id': self.activity.id},
        )
        remove_response = self.client.post(
            reverse('destinations:activity-remove'),
            {'stop_id': self.stop.id, 'activity_id': self.activity.id},
        )

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(remove_response.status_code, 403)
        self.assertFalse(StopActivity.objects.filter(stop=self.stop, activity=self.activity).exists())

    def test_cannot_add_activity_from_different_city(self):
        other_city = City.objects.create(
            name='Reykjavik',
            country='Iceland',
            region='Europe',
            cost_index=Decimal('150.00'),
            popularity_score=75,
            description='Cold and scenic',
        )
        other_activity = Activity.objects.create(
            city=other_city,
            name='Northern Lights Tour',
            description='A chilly evening tour',
            category=Activity.CATEGORY_SIGHTSEEING,
            estimated_cost=Decimal('120.00'),
            duration_minutes=180,
        )

        self.client.force_login(self.owner)
        add_response = self.client.post(
            reverse('destinations:activity-add'),
            {'stop_id': self.stop.id, 'activity_id': other_activity.id},
        )

        # Should redirect back but not create the StopActivity
        self.assertEqual(add_response.status_code, 302)
        self.assertFalse(StopActivity.objects.filter(stop=self.stop, activity=other_activity).exists())
