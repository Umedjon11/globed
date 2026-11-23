from django.urls import path
from .views import *

urlpatterns = [
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('subscription/checkout/<int:plan_id>/', CheckoutView.as_view(), name='checkout'),
]
