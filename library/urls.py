from django.urls import path
from .views import *

urlpatterns = [
    path('library/', BookListView.as_view(), name='book_list'),
    path('library/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
]
