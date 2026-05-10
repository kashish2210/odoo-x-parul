from django import forms
from .models import Trip, Stop
from destinations.models import City


class TripForm(forms.ModelForm):
    """Form for creating/editing a trip."""
    class Meta:
        model = Trip
        fields = ['name', 'description', 'cover_photo', 'start_date', 'end_date', 'accommodation_per_day', 'transport_per_day', 'is_public']
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
            'accommodation_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'e.g. 120.00',
            }),
            'transport_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'e.g. 35.00',
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
        return city
