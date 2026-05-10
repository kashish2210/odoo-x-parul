from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View

from trips.models import Stop, StopActivity

from .models import Activity


class ActivitySearchView(LoginRequiredMixin, ListView):
    template_name = 'destinations/activity_search.html'
    context_object_name = 'activities'

    def get_queryset(self):
        queryset = Activity.objects.select_related('city').all()
        params = self.request.GET

        query = params.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(city__name__icontains=query)
                | Q(city__country__icontains=query)
                | Q(city__region__icontains=query)
            )

        category = params.get('category', '').strip()
        if category:
            queryset = queryset.filter(category=category)

        country = params.get('country', '').strip()
        if country:
            queryset = queryset.filter(city__country__iexact=country)

        region = params.get('region', '').strip()
        if region:
            queryset = queryset.filter(city__region__iexact=region)

        min_cost = params.get('min_cost', '').strip()
        if min_cost:
            queryset = queryset.filter(estimated_cost__gte=min_cost)

        max_cost = params.get('max_cost', '').strip()
        if max_cost:
            queryset = queryset.filter(estimated_cost__lte=max_cost)

        min_duration = params.get('min_duration', '').strip()
        if min_duration:
            queryset = queryset.filter(duration_minutes__gte=min_duration)

        max_duration = params.get('max_duration', '').strip()
        if max_duration:
            queryset = queryset.filter(duration_minutes__lte=max_duration)

        sort = params.get('sort', 'popularity')
        sort_map = {
            'popularity': ['-city__popularity_score', 'name'],
            'cost_low': ['estimated_cost', 'name'],
            'cost_high': ['-estimated_cost', 'name'],
            'duration_short': ['duration_minutes', 'name'],
            'duration_long': ['-duration_minutes', 'name'],
            'name': ['name'],
        }
        queryset = queryset.order_by(*sort_map.get(sort, sort_map['popularity']))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET
        stop_id = params.get('stop')
        selected_stop = None

        if stop_id:
            selected_stop = get_object_or_404(
                Stop.objects.select_related('trip', 'city'),
                pk=stop_id,
                trip__user=self.request.user,
            )

        existing_activity_ids = set()
        if selected_stop:
            existing_activity_ids = set(
                selected_stop.stop_activities.values_list('activity_id', flat=True)
            )

        context['selected_stop'] = selected_stop
        context['selected_trip'] = selected_stop.trip if selected_stop else None
        context['existing_activity_ids'] = existing_activity_ids
        context['filters'] = {
            'q': params.get('q', ''),
            'category': params.get('category', ''),
            'country': params.get('country', ''),
            'region': params.get('region', ''),
            'min_cost': params.get('min_cost', ''),
            'max_cost': params.get('max_cost', ''),
            'min_duration': params.get('min_duration', ''),
            'max_duration': params.get('max_duration', ''),
            'sort': params.get('sort', 'popularity'),
        }
        context['category_choices'] = Activity.CATEGORY_CHOICES
        context['sort_options'] = [
            ('popularity', 'Popularity'),
            ('cost_low', 'Lowest cost'),
            ('cost_high', 'Highest cost'),
            ('duration_short', 'Shortest duration'),
            ('duration_long', 'Longest duration'),
            ('name', 'Name'),
        ]
        return context


class AddActivityToStopView(LoginRequiredMixin, View):
    def post(self, request):
        stop = get_object_or_404(Stop, pk=request.POST.get('stop_id'), trip__user=request.user)
        activity = get_object_or_404(Activity, pk=request.POST.get('activity_id'))

        StopActivity.objects.get_or_create(stop=stop, activity=activity)
        messages.success(request, f'Added {activity.name} to {stop.city.name}.')
        return redirect(request.POST.get('next') or reverse_lazy('destinations:activity-search'))


class RemoveActivityFromStopView(LoginRequiredMixin, View):
    def post(self, request):
        stop = get_object_or_404(Stop, pk=request.POST.get('stop_id'), trip__user=request.user)
        activity = get_object_or_404(Activity, pk=request.POST.get('activity_id'))

        deleted, _ = StopActivity.objects.filter(stop=stop, activity=activity).delete()
        if deleted:
            messages.info(request, f'Removed {activity.name} from {stop.city.name}.')
        else:
            messages.info(request, f'{activity.name} was not added to this stop yet.')
        return redirect(request.POST.get('next') or reverse_lazy('destinations:activity-search'))