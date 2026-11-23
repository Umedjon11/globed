from django.contrib import admin
from .models import (
    AssessmentSession, SubjectLevel, Lesson,
    LessonProgress, StreakRecord, XPEvent,
    ChatSession, ChatMessage, UsageCounter
)

@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'language', 'status', 'created_at')
    list_filter = ('status', 'language')

@admin.register(SubjectLevel)
class SubjectLevelAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'level', 'score', 'updated_at')
    list_filter = ('level', 'subject')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'student', 'status', 'xp_reward', 'created_at')
    list_filter = ('subject', 'status')
    search_fields = ('title', 'description')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'status', 'score', 'completed_at')
    list_filter = ('status',)

@admin.register(StreakRecord)
class StreakRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'current_streak', 'longest_streak', 'last_active_date')

@admin.register(XPEvent)
class XPEventAdmin(admin.ModelAdmin):
    list_display = ('student', 'points', 'reason', 'created_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at')

@admin.register(UsageCounter)
class UsageCounterAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'ai_messages', 'ai_lessons')
