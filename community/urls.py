from django.urls import path
from .views import *

urlpatterns = [
    path('community/', PostListView.as_view(), name='post_list'),
    path('community/new/', PostCreateView.as_view(), name='post_create'),
    path('community/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('community/<int:pk>/like/', LikePostView.as_view(), name='like_post'),
    path('community/<int:pk>/report/', ReportPostView.as_view(), name='report_post'),
]
