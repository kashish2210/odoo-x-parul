from django import forms
from .models import Trip, Stop
from destinations.models import City


class TripForm(forms.ModelForm):
    """Form for creating/editing a trip."""
    class Meta:
        model = Trip
        fields = ['name', 'description', 'cover_photo', 'start_date', 'end_date', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. European Summer 2026',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your trip...',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'cover_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


class StopForm(forms.Form):
    """Form for adding a stop — type a city name and country, auto-creates City."""
    city_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Paris, Jaipur, Tokyo...',
            'autocomplete': 'off',
        }),
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. France, India, Japan...',
            'autocomplete': 'off',
        }),
    )
    arrival_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        arrival = cleaned.get('arrival_date')
        departure = cleaned.get('departure_date')
        if arrival and departure and departure < arrival:
            raise forms.ValidationError('Departure date must be after arrival date.')
        return cleaned

    def get_or_create_city(self):
        """Find existing city or create a new one automatically."""
        import urllib.request
        import urllib.parse
        import json

        name = self.cleaned_data['city_name'].strip().title()
        country = self.cleaned_data['country'].strip().title()
        city, created = City.objects.get_or_create(
            name=name,
            country=country,
            defaults={
                'region': '',
                'cost_index': 0,
                'popularity_score': 0,
            }
        )

        if not created:
            # Bump popularity every time someone adds this city to a trip
            city.popularity_score += 1
            city.save(update_fields=['popularity_score'])

        # Fetch coordinates if they are missing
        if city.latitude is None or city.longitude is None:
            try:
                query = urllib.parse.quote(f"{name}, {country}")
                url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=1"
                req = urllib.request.Request(url, headers={'User-Agent': 'Traveloop/1.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data:
                        city.latitude = data[0]['lat']
                        city.longitude = data[0]['lon']
                        city.save(update_fields=['latitude', 'longitude'])
            except Exception:
                pass # If it fails, just ignore and leave as null

        return city
