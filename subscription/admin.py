from django.contrib import admin
from .models import Plan, Subscription, Payment

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_months', 'price', 'currency', 'discount_percent', 'is_active')
    list_filter = ('is_active',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'starts_at', 'ends_at')
    list_filter = ('status', 'plan')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'provider', 'status', 'created_at')
    list_filter = ('status', 'provider')
