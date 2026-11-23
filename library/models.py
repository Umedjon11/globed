from django.db import models
from django.conf import settings

class Book(models.Model):
    CATEGORY_CHOICES = (
        ('sat', 'SAT Preparation'),
        ('ielts', 'IELTS / TOEFL'),
        ('admissions', 'College Admissions Guides'),
        ('essays', 'Essay & Motivation Letters'),
        ('stem', 'Math & Science'),
        ('general', 'General Education')
    )

    title = models.CharField(max_length=250)
    author = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, default='sat', max_length=50)
    language = models.CharField(max_length=10, default='en')
    file_url = models.URLField(max_length=500, blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)
    page_count = models.PositiveIntegerField(default=150)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.author}"
