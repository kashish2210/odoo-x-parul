from django import forms
from trips.models import Trip
from .models import Note


class NoteForm(forms.ModelForm):
    """Form for creating and editing a note, scoped to the logged-in user's trips."""
    class Meta:
        model = Note
        fields = ['trip', 'title', 'stop_name', 'day_label', 'content']
        widgets = {
            'trip': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_trip',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Note title...',
                'id': 'id_title',
                'autofocus': True,
            }),
            'stop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Rome stop (optional)',
                'id': 'id_stop_name',
            }),
            'day_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Day 3: June 14 2025 (optional)',
                'id': 'id_day_label',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your note here...',
                'rows': 5,
                'id': 'id_content',
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show trips belonging to this user
        self.fields['trip'].queryset = Trip.objects.filter(user=user)
        self.fields['trip'].empty_label = 'Select a trip...'
        self.fields['stop_name'].required = False
        self.fields['day_label'].required = False
