from django.db import models
from django.conf import settings

class AssessmentSession(models.Model):
    STATUS_CHOICES = (
        ('generated', 'generated'),
        ('submitted', 'submitted'),
        ('evaluated', 'evaluated')
    )

    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='assessments')
    language = models.CharField(max_length=10, default='ru')
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    status = models.CharField(choices=STATUS_CHOICES, default='generated', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - Assessment #{self.id}"

class SubjectLevel(models.Model):
    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='subject_levels')
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=50, default='Intermediate')
    score = models.PositiveIntegerField(default=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.full_name}: {self.subject} ({self.level})"

class Lesson(models.Model):
    STATUS_CHOICES = (
        ('generating', 'generating'),
        ('ready', 'ready'),
        ('failed', 'failed')
    )

    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    content = models.JSONField(default=dict)
    language = models.CharField(max_length=10, default='ru')
    status = models.CharField(choices=STATUS_CHOICES, default='ready', max_length=20)
    xp_reward = models.PositiveIntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LessonProgress(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'not_started'),
        ('in_progress', 'in_progress'),
        ('completed', 'completed')
    )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='lesson_progresses')
    status = models.CharField(choices=STATUS_CHOICES, default='not_started', max_length=20)
    score = models.FloatField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('lesson', 'student')

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}: {self.status}"

class StreakRecord(models.Model):
    student = models.OneToOneField('account.StudentProfile', on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=1)
    longest_streak = models.PositiveIntegerField(default=1)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.full_name}: {self.current_streak} days"

class XPEvent(models.Model):
    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='xp_events')
    points = models.PositiveIntegerField()
    reason = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} +{self.points} XP ({self.reason})"

class ChatSession(models.Model):
    student = models.ForeignKey('account.StudentProfile', on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default='Новый диалог')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name}: {self.title}"

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'user'),
        ('assistant', 'assistant')
    )

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"

class UsageCounter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_counters')
    date = models.DateField()
    ai_messages = models.PositiveIntegerField(default=0)
    ai_lessons = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.email} [{self.date}]: msgs={self.ai_messages}, lessons={self.ai_lessons}"
