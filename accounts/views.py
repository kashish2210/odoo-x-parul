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

