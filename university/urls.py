from django.urls import path
from .views import *

urlpatterns = [
    path('universities/', UniversityListView.as_view(), name='university_list'),
    path('universities/<int:pk>/', UniversityDetailView.as_view(), name='university_detail'),
    path('universities/<int:pk>/toggle-target/', ToggleTargetUniversityView.as_view(), name='toggle_target_university'),
]
