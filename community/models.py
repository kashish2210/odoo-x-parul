from django.db import models
from django.conf import settings


class CommunityPost(models.Model):
    """A community post where users share trip experiences and tips."""
    CATEGORY_EXPERIENCE = 'experience'
    CATEGORY_TIP = 'tip'
    CATEGORY_QUESTION = 'question'
    CATEGORY_ITINERARY = 'itinerary'

    CATEGORY_CHOICES = [
        (CATEGORY_EXPERIENCE, 'Experience'),
        (CATEGORY_TIP, 'Travel Tip'),
        (CATEGORY_QUESTION, 'Question'),
        (CATEGORY_ITINERARY, 'Itinerary Share'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    trip = models.ForeignKey('trips.Trip', on_delete=models.SET_NULL, null=True, blank=True, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_EXPERIENCE)
    image = models.ImageField(upload_to='community/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.title} — @{self.user.username}"


class PostLike(models.Model):
    """Like on a community post."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"@{self.user.username} liked: {self.post.title}"


class PostComment(models.Model):
    """Comment on a community post."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_comments')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"@{self.user.username} on: {self.post.title}"
