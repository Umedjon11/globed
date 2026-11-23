from django.urls import path
from .views import *

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/<str:email>/verify/', VerifyAccountView.as_view(), name='verify_account'),
    path('auth/login/', LoginUserView.as_view(), name='login'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),
    path('account/setup/', ProfileSetupView.as_view(), name='profile_setup'),
    path('account/profile/', ProfileView.as_view(), name='profile'),
    path('account/verify-student/', StudentVerificationView.as_view(), name='student_verify'),
    path('account/delete/', DeleteAccountView.as_view(), name='delete_account'),
]
