from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'language', 'page_count', 'is_published')
    list_filter = ('category', 'language', 'is_published')
    search_fields = ('title', 'author', 'description')
