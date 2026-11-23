from django.contrib import admin
from .models import TipPost, AuthorTrust, PostReport

@admin.register(TipPost)
class TipPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'university', 'status', 'likes_count', 'created_at')
    list_filter = ('status', 'language', 'university')
    search_fields = ('title', 'body', 'author__email')

@admin.register(AuthorTrust)
class AuthorTrustAdmin(admin.ModelAdmin):
    list_display = ('author', 'approved_posts_count', 'is_trusted')

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'status', 'created_at')
    list_filter = ('status',)
