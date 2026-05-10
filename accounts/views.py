from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import LoginForm, SignupForm
from .models import UserProfile


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                city=form.cleaned_data.get('city', ''),
                country=form.cleaned_data.get('country', ''),
                bio=form.cleaned_data.get('bio', ''),
                photo=form.cleaned_data.get('photo'),
            )
            login(request, user)
            messages.success(request, 'Account created! Welcome to Traveloop!')
            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out. See you next trip!')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard after login — shows real trips and notes summary."""
    from trips.models import Trip
    from notes.models import Note

    trips = Trip.objects.filter(user=request.user).order_by('-start_date')[:6]
    notes_count = Note.objects.filter(user=request.user).count()
    recent_notes = Note.objects.filter(user=request.user).select_related('trip')[:3]

    return render(request, 'accounts/dashboard.html', {
        'trips': trips,
        'notes_count': notes_count,
        'recent_notes': recent_notes,
    })

@login_required
def profile_view(request):
    """User profile page with inline editing."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update User fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # Update Profile fields
        profile.phone = request.POST.get('phone', '')
        profile.city = request.POST.get('city', '')
        profile.country = request.POST.get('country', '')
        profile.bio = request.POST.get('bio', '')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'preplanned_trips': [],  # Will be populated when trips feature is built
        'previous_trips': [],    # Will be populated when trips feature is built
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth
import json


@staff_member_required
def admin_panel_login_view(request):
    """Password prompt for admin panel."""
    if request.session.get('admin_panel_unlocked'):
        return redirect('admin_panel')
        
    if request.method == 'POST':
        password = request.POST.get('admin_password')
        if password == '1000':
            request.session['admin_panel_unlocked'] = True
            messages.success(request, 'Admin panel unlocked.')
            return redirect('admin_panel')
        else:
            messages.error(request, 'Incorrect password.')
            
    return render(request, 'accounts/admin_login.html')


@staff_member_required
def admin_panel_view(request):
    """Custom admin panel — Screen 12 from wireframe."""
    if not request.session.get('admin_panel_unlocked'):
        return redirect('admin_panel_login')
    from trips.models import Trip, Stop
    from destinations.models import City, Activity
    from community.models import CommunityPost
    from budget.models import TripBudget

    tab = request.GET.get('tab', 'users')
    query = request.GET.get('q', '')

    context = {'tab': tab, 'query': query}

    # ── TAB 1: Manage Users ──
    if tab == 'users':
        users = User.objects.annotate(
            trip_count=Count('trips'),
            post_count=Count('community_posts'),
        ).order_by('-date_joined')
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query)
            )
        context['users'] = users
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(trips__isnull=False).distinct().count()

    # ── TAB 2: Popular Cities ──
    elif tab == 'cities':
        cities = City.objects.annotate(
            visit_count=Count('trip_stops'),
        ).order_by('-visit_count')[:20]
        if query:
            cities = City.objects.annotate(
                visit_count=Count('trip_stops'),
            ).filter(
                Q(name__icontains=query) | Q(country__icontains=query)
            ).order_by('-visit_count')[:20]
        context['cities'] = cities
        context['total_cities'] = City.objects.count()

    # ── TAB 3: Popular Activities ──
    elif tab == 'activities':
        activities = Activity.objects.annotate(
            booking_count=Count('scheduled_stops'),
        ).order_by('-booking_count')[:20]
        if query:
            activities = Activity.objects.annotate(
                booking_count=Count('scheduled_stops'),
            ).filter(
                Q(name__icontains=query) | Q(city__name__icontains=query)
            ).order_by('-booking_count')[:20]
        context['activities'] = activities
        context['total_activities'] = Activity.objects.count()

    # ── TAB 4: User Trends & Analytics ──
    elif tab == 'analytics':
        # Summary stats
        context['total_users'] = User.objects.count()
        context['total_trips'] = Trip.objects.count()
        context['total_stops'] = Stop.objects.count()
        context['total_posts'] = CommunityPost.objects.count()
        context['total_cities'] = City.objects.count()

        # Total budget across all trips
        budget_agg = TripBudget.objects.aggregate(
            total=Sum('total_budget'),
        )
        context['total_budget_all'] = budget_agg['total'] or 0

        # Trips per month (last 6 months) for line chart
        from django.utils import timezone
        import datetime
        six_months_ago = timezone.now().date() - datetime.timedelta(days=180)
        trips_per_month = (
            Trip.objects.filter(start_date__gte=six_months_ago)
            .annotate(month=TruncMonth('start_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        context['trips_chart_labels'] = json.dumps([
            t['month'].strftime('%b %Y') for t in trips_per_month
        ])
        context['trips_chart_data'] = json.dumps([
            t['count'] for t in trips_per_month
        ])

        # Category distribution for pie chart
        category_data = (
            CommunityPost.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        context['cat_labels'] = json.dumps([c['category'].title() for c in category_data])
        context['cat_data'] = json.dumps([c['count'] for c in category_data])

        # Top 5 cities for bar chart
        top_cities = City.objects.annotate(
            visits=Count('trip_stops')
        ).order_by('-visits')[:5]
        context['city_bar_labels'] = json.dumps([c.name for c in top_cities])
        context['city_bar_data'] = json.dumps([c.visits for c in top_cities])

    return render(request, 'accounts/admin_panel.html', context)


# ── STATIC / FOOTER PAGES ──

def about_view(request):
    return render(request, 'accounts/static_pages/about.html')

def contact_view(request):
    return render(request, 'accounts/static_pages/contact.html')

def careers_view(request):
    return render(request, 'accounts/static_pages/careers.html')

def help_view(request):
    return render(request, 'accounts/static_pages/help.html')

def privacy_view(request):
    return render(request, 'accounts/static_pages/privacy.html')

def terms_view(request):
    return render(request, 'accounts/static_pages/terms.html')

