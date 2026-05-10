from django import forms
from .models import CommunityPost, PostComment


class CommunityPostForm(forms.ModelForm):
    """Form for creating/editing a community post."""
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'category', 'trip', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your post a title...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your experience, tips, or questions...',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'trip': forms.Select(attrs={
                'class': 'form-control',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trip'].required = False
        self.fields['trip'].empty_label = 'Not linked to a trip'
        if user:
            from trips.models import Trip
            self.fields['trip'].queryset = Trip.objects.filter(user=user)


class CommentForm(forms.ModelForm):
    """Inline form for adding a comment."""
    class Meta:
        model = PostComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add a comment...',
            }),
        }
