from django.contrib import admin
from .models import University, TargetUniversity

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'ranking', 'is_published', 'created_at')
    list_filter = ('country', 'is_published')
    search_fields = ('name', 'country', 'description')

@admin.register(TargetUniversity)
class TargetUniversityAdmin(admin.ModelAdmin):
    list_display = ('student_profile', 'university', 'priority', 'created_at')
    list_filter = ('university__country',)
    search_fields = ('student_profile__full_name', 'university__name')
