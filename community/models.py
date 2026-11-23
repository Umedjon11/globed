from django.db import models
from django.conf import settings
from university.models import University

class TipPost(models.Model):
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
        ('hidden', 'hidden')
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tips')
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name='tips')
    title = models.CharField(max_length=250)
    body = models.TextField()
    language = models.CharField(max_length=10, default='ru')
    status = models.CharField(choices=STATUS_CHOICES, default='approved', max_length=20)
    likes_count = models.PositiveIntegerField(default=0)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tips')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class AuthorTrust(models.Model):
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_trust')
    approved_posts_count = models.PositiveIntegerField(default=0)
    is_trusted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.email} - Trusted: {self.is_trusted}"

class PostReport(models.Model):
    STATUS_CHOICES = (
        ('open', 'open'),
        ('resolved', 'resolved')
    )

    post = models.ForeignKey(TipPost, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_posts')
    reason = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, default='open', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.post.title}"
