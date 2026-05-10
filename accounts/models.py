from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for Traveloop travelers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    language_preference = models.CharField(max_length=50, blank=True, default='English')
    saved_cities = models.ManyToManyField('destinations.City', blank=True, related_name='saved_by_profiles')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
