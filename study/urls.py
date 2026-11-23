from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('diagnostic/', DiagnosticStartView.as_view(), name='diagnostic_start'),
    path('diagnostic/session/', DiagnosticSessionView.as_view(), name='diagnostic_session'),
    path('diagnostic/result/<int:session_id>/', DiagnosticResultView.as_view(), name='diagnostic_result'),
    path('lessons/', LessonListView.as_view(), name='lesson_list'),
    path('lessons/generate/', GenerateLessonView.as_view(), name='generate_lesson'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('chat/', AIChatView.as_view(), name='chat'),
    path('chat/<int:session_id>/', AIChatView.as_view(), name='chat_session'),
    path('chat/create/', CreateChatSessionView.as_view(), name='create_chat_session'),
]
