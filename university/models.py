from django.db import models
from django.conf import settings

class University(models.Model):
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(null=True, blank=True)
    requirements = models.TextField()
    website_url = models.URLField(max_length=250)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    ranking = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='created_universities', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Universities'
        ordering = ['ranking', 'name']

    def __str__(self):
        return f"{self.name} ({self.country})"

class TargetUniversity(models.Model):
    student_profile = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='student_universities')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='university_targets')
    priority = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student_profile', 'university')

    def __str__(self):
        return f"{self.student_profile.full_name} -> {self.university.name}"
