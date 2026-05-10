from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from destinations.models import Activity, City

from .forms import StopForm, TripForm, StopEditForm
from .models import Stop, StopActivity, Trip


@login_required
def trip_list_view(request):
    """Screen 6: My Trips — grouped by Ongoing, Upcoming, Completed."""
    today = timezone.now().date()
    user_trips = Trip.objects.filter(user=request.user)

    ongoing = user_trips.filter(start_date__lte=today, end_date__gte=today)
    upcoming = user_trips.filter(start_date__gt=today)
    completed = user_trips.filter(end_date__lt=today)

    query = request.GET.get('q', '')
    if query:
        ongoing = ongoing.filter(name__icontains=query)
        upcoming = upcoming.filter(name__icontains=query)
        completed = completed.filter(name__icontains=query)

    return render(request, 'trips/trip_list.html', {
        'ongoing': ongoing,
        'upcoming': upcoming,
        'completed': completed,
        'query': query,
    })


@login_required
def trip_create_view(request):
    """Screen 4: Create a New Trip."""
    if request.method == 'POST':
        form = TripForm(request.POST, request.FILES)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            messages.success(request, f'Trip "{trip.name}" created!')
            return redirect('trip_itinerary', trip_id=trip.id)
    else:
        form = TripForm()

    # Suggested cities for the bottom section
    suggested_cities = City.objects.order_by('-popularity_score')[:6]

    return render(request, 'trips/trip_create.html', {
        'form': form,
        'suggested_cities': suggested_cities,
    })


@login_required
def trip_edit_view(request, trip_id):
    """Edit an existing trip."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == 'POST':
        form = TripForm(request.POST, request.FILES, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, f'Trip "{trip.name}" updated!')
            return redirect('trip_list')
    else:
        form = TripForm(instance=trip)

    return render(request, 'trips/trip_create.html', {
        'form': form,
        'editing': True,
        'trip': trip,
    })


@login_required
def trip_delete_view(request, trip_id):
    """Delete a trip."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    if request.method == 'POST':
        name = trip.name
        trip.delete()
        messages.success(request, f'Trip "{name}" deleted.')
    return redirect('trip_list')


@login_required
def trip_itinerary_view(request, trip_id):
    """Screen 5: Itinerary Builder — add/manage stops."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    stops = trip.stops.select_related('city').prefetch_related('stop_activities__activity')

    if request.method == 'POST':
        form = StopForm(request.POST)
        if form.is_valid():
            city = form.get_or_create_city()
            stop = Stop.objects.create(
                trip=trip,
                city=city,
                arrival_date=form.cleaned_data['arrival_date'],
                departure_date=form.cleaned_data['departure_date'],
                order=stops.count() + 1,
            )
            messages.success(request, f'Added {city.name}, {city.country} to your itinerary!')
            return redirect('trip_itinerary', trip_id=trip.id)
    else:
        form = StopForm()

    return render(request, 'trips/trip_itinerary.html', {
        'trip': trip,
        'stops': stops,
        'form': form,
    })


@login_required
def stop_delete_view(request, trip_id, stop_id):
    """Delete a stop from itinerary."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    stop = get_object_or_404(Stop, id=stop_id, trip=trip)
    if request.method == 'POST':
        stop.delete()
        # Re-order remaining stops
        for i, s in enumerate(trip.stops.order_by('order'), start=1):
            if s.order != i:
                s.order = i
                s.save(update_fields=['order'])
        messages.success(request, 'Stop removed from itinerary.')
    return redirect('trip_itinerary', trip_id=trip.id)


@login_required
def stop_edit_view(request, trip_id, stop_id):
    """Edit a stop's arrival and departure dates."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    stop = get_object_or_404(Stop, id=stop_id, trip=trip)

    if request.method == 'POST':
        form = StopEditForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dates updated for {stop.city.name}!')
            return redirect('trip_itinerary', trip_id=trip.id)
    else:
        form = StopEditForm(instance=stop)

    return render(request, 'trips/stop_edit.html', {
        'trip': trip,
        'stop': stop,
        'form': form,
    })


@login_required
def trip_detail_view(request, trip_id):
    """Screen 6 detail: View a single trip overview."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    stops = trip.stops.select_related('city').prefetch_related('stop_activities__activity')

    stay_rate = trip.accommodation_per_day or Decimal('0.00')
    transport_rate = trip.transport_per_day or Decimal('0.00')
    meal_rate = Decimal('25.00')

    total_stay = Decimal('0.00')
    total_activities = Decimal('0.00')
    total_meals = Decimal('0.00')
    total_transport = Decimal('0.00')
    total_days = 0
    per_stop = []

    for stop in stops:
        nights = max((stop.departure_date - stop.arrival_date).days, 1)
        total_days += nights

        stay_cost = stay_rate * Decimal(nights)
        activities_cost = sum((sa.activity.estimated_cost or Decimal('0.00')) for sa in stop.stop_activities.all())
        meals_cost = meal_rate * Decimal(nights)
        transport_cost = transport_rate * Decimal(nights)

        total_stay += stay_cost
        total_activities += Decimal(activities_cost)
        total_meals += meals_cost
        total_transport += transport_cost

        per_stop.append({
            'stop': stop,
            'nights': nights,
            'stay_cost': stay_cost,
            'activities_cost': Decimal(activities_cost),
            'meals_cost': meals_cost,
            'transport_cost': transport_cost,
            'total_cost': stay_cost + Decimal(activities_cost) + meals_cost + transport_cost,
        })

    trip_total = total_stay + total_activities + total_meals + total_transport
    avg_per_day = (trip_total / Decimal(total_days)) if total_days > 0 else trip_total
    over_budget_threshold = avg_per_day * Decimal('1.5') if total_days > 0 else trip_total
    over_budget_stops = [item for item in per_stop if item['total_cost'] > over_budget_threshold]

    # Build map data
    import json
    map_points = []
    for stop in stops:
        city = stop.city
        if city.latitude and city.longitude:
            map_points.append({
                'name': city.name,
                'country': city.country,
                'lat': city.latitude,
                'lng': city.longitude,
                'arrival': stop.arrival_date.strftime('%b %d'),
                'departure': stop.departure_date.strftime('%b %d'),
            })

    return render(request, 'trips/trip_detail.html', {
        'trip': trip,
        'stops': stops,
        'map_data': json.dumps(map_points),
        'budget_summary': {
            'stay_rate': stay_rate,
            'transport_rate': transport_rate,
            'meal_rate': meal_rate,
            'total_stay': total_stay,
            'total_activities': total_activities,
            'total_meals': total_meals,
            'total_transport': total_transport,
            'trip_total': trip_total,
            'avg_per_day': avg_per_day,
            'per_stop': per_stop,
            'over_budget_stops': over_budget_stops,
        },
    })


@login_required
def explore_view(request):
    """Explore page: public trips from everyone + your own trips."""
    from django.db.models import Q
    import json
    query = request.GET.get('q', '')

    trips = Trip.objects.filter(
        Q(is_public=True) | Q(user=request.user)
    ).select_related('user').distinct().order_by('-start_date')

    if query:
        trips = trips.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Build map data from all stops of visible trips
    all_stops = Stop.objects.filter(
        trip__in=trips
    ).select_related('city', 'trip')
    map_points = []
    seen = set()
    for stop in all_stops:
        city = stop.city
        if city.latitude and city.longitude and city.id not in seen:
            seen.add(city.id)
            map_points.append({
                'name': city.name,
                'country': city.country,
                'lat': city.latitude,
                'lng': city.longitude,
                'trips': stop.trip.name,
            })

    return render(request, 'trips/explore.html', {
        'trips': trips,
        'query': query,
        'map_data': json.dumps(map_points),
    })


def trip_public_view(request, trip_id):
    """Public trip view: shareable read-only view of a public trip."""
    trip = get_object_or_404(Trip, id=trip_id, is_public=True)
    stops = trip.stops.select_related('city').prefetch_related('stop_activities__activity')

    # Compute budget summary even for public view
    stay_rate = trip.accommodation_per_day or Decimal('0.00')
    transport_rate = trip.transport_per_day or Decimal('0.00')
    meal_rate = Decimal('25.00')

    total_stay = Decimal('0.00')
    total_activities = Decimal('0.00')
    total_meals = Decimal('0.00')
    total_transport = Decimal('0.00')
    total_days = 0
    per_stop = []

    for stop in stops:
        nights = max((stop.departure_date - stop.arrival_date).days, 1)
        total_days += nights

        stay_cost = stay_rate * Decimal(nights)
        activities_cost = sum((sa.activity.estimated_cost or Decimal('0.00')) for sa in stop.stop_activities.all())
        meals_cost = meal_rate * Decimal(nights)
        transport_cost = transport_rate * Decimal(nights)

        total_stay += stay_cost
        total_activities += Decimal(activities_cost)
        total_meals += meals_cost
        total_transport += transport_cost

        per_stop.append({
            'stop': stop,
            'nights': nights,
            'stay_cost': stay_cost,
            'activities_cost': Decimal(activities_cost),
            'meals_cost': meals_cost,
            'transport_cost': transport_cost,
            'total_cost': stay_cost + Decimal(activities_cost) + meals_cost + transport_cost,
        })

    trip_total = total_stay + total_activities + total_meals + total_transport
    avg_per_day = (trip_total / Decimal(total_days)) if total_days > 0 else trip_total

    return render(request, 'trips/trip_public.html', {
        'trip': trip,
        'stops': stops,
        'budget_summary': {
            'stay_rate': stay_rate,
            'transport_rate': transport_rate,
            'meal_rate': meal_rate,
            'total_stay': total_stay,
            'total_activities': total_activities,
            'total_meals': total_meals,
            'total_transport': total_transport,
            'trip_total': trip_total,
            'avg_per_day': avg_per_day,
            'per_stop': per_stop,
        },
    })


@login_required
def trip_copy_view(request, trip_id):
    """Copy a public trip to the current user's account."""
    from django.db import transaction
    
    source_trip = get_object_or_404(Trip, id=trip_id, is_public=True)

    with transaction.atomic():
        # Create new trip for the current user
        new_trip = Trip.objects.create(
            user=request.user,
            name=f"{source_trip.name} (Copy)",
            description=source_trip.description,
            start_date=source_trip.start_date,
            end_date=source_trip.end_date,
            accommodation_per_day=source_trip.accommodation_per_day,
            transport_per_day=source_trip.transport_per_day,
            is_public=False,
        )

        # Copy all stops and activities
        for stop in source_trip.stops.all():
            new_stop = Stop.objects.create(
                trip=new_trip,
                city=stop.city,
                arrival_date=stop.arrival_date,
                departure_date=stop.departure_date,
                order=stop.order,
            )
            # Copy activities
            for stop_activity in stop.stop_activities.all():
                StopActivity.objects.create(
                    stop=new_stop,
                    activity=stop_activity.activity,
                    scheduled_time=stop_activity.scheduled_time,
                )

    messages.success(request, f'Trip "{source_trip.name}" copied to your account!')
    return redirect('trip_detail', trip_id=new_trip.id)