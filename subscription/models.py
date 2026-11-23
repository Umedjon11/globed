from django.db import models
from django.conf import settings

class Plan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    discount_percent = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({self.duration_months} mo - ${self.price})"

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'active'),
        ('expired', 'expired')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES, default='active', max_length=20)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('paid', 'paid'),
        ('failed', 'failed')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=50, default='Alif / Card')
    provider_ref = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_CHOICES, default='paid', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"
