from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription, Payment

class PricingView(View):
    template_name = 'subscription/pricing.html'

    def get(self, request):
        plans = Plan.objects.filter(is_active=True).order_by('duration_months')
        if not plans.exists():
            default_plans = [
                {
                    'name': 'Pro 1 месяц',
                    'duration_months': 1,
                    'price': 9.99,
                    'discount_percent': 0,
                    'features': [
                        'Неограниченные уроки от ИИ',
                        'Полный доступ к ИИ-ассистенту 24/7',
                        'Доступ ко всей библиотеке SAT/IELTS',
                        'Персональный разбор эссе'
                    ]
                },
                {
                    'name': 'Pro 3 месяца',
                    'duration_months': 3,
                    'price': 24.99,
                    'discount_percent': 15,
                    'features': [
                        'Все функции Pro',
                        'Скидка 15%',
                        'Приоритетная проверка эссе',
                        'Детальный план поступления'
                    ]
                },
                {
                    'name': 'Pro 12 месяцев (Годовой)',
                    'duration_months': 12,
                    'price': 79.99,
                    'discount_percent': 35,
                    'features': [
                        'Все функции Pro на весь год',
                        'Максимальная выгода - скидка 35%',
                        'Личный трекер дедлайнов вузов',
                        'Сертификат готовности к экзаменам'
                    ]
                }
            ]
            for p_data in default_plans:
                Plan.objects.create(**p_data)
            plans = Plan.objects.filter(is_active=True).order_by('duration_months')

        user_sub = None
        if request.user.is_authenticated:
            user_sub = Subscription.objects.filter(
                user=request.user,
                status='active',
                ends_at__gte=timezone.now()
            ).first()

        return render(request, self.template_name, {
            'plans': list(plans),
            'user_sub': user_sub
        })


class CheckoutView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        now = timezone.now()
        ends_at = now + timedelta(days=plan.duration_months * 30)

        Payment.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price,
            provider='Alif / Card',
            provider_ref=f'INV-{request.user.id}-{int(now.timestamp())}',
            status='paid'
        )

        sub, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'starts_at': now, 'ends_at': ends_at, 'status': 'active'}
        )
        if not created:
            sub.plan = plan
            sub.starts_at = now
            sub.ends_at = ends_at
            sub.status = 'active'
            sub.save()

        messages.success(request, f'Поздравляем! Подписка "{plan.name}" успешно активирована до {ends_at.strftime("%d.%m.%Y")}.')
        return redirect('pricing')
