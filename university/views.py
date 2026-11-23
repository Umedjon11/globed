from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import University, TargetUniversity

class UniversityListView(View):
    template_name = 'university/list.html'

    def get(self, request):
        universities = University.objects.filter(is_published=True)
        query = (request.GET.get('q') or '').strip()
        country = (request.GET.get('country') or '').strip()

        alias_map = {
            'гарвард': 'Harvard',
            'стенфорд': 'Stanford',
            'стэнфорд': 'Stanford',
            'мит': 'MIT',
            'оксфорд': 'Oxford',
            'кембридж': 'Cambridge',
            'торонто': 'Toronto',
            'сша': 'USA',
            'америка': 'USA',
            'англия': 'UK',
            'великобритания': 'UK',
            'канада': 'Canada',
        }

        if query:
            q = query.lower()
            mapped = alias_map.get(q, query)
            universities = universities.filter(
                Q(name__icontains=query) |
                Q(name__icontains=mapped) |
                Q(country__icontains=query) |
                Q(country__icontains=mapped) |
                Q(city__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query)
            )

        if country:
            country_clean = country.lower()
            country_mapped = alias_map.get(country_clean, country)
            universities = universities.filter(
                Q(country__iexact=country) |
                Q(country__iexact=country_mapped) |
                Q(country__icontains=country)
            )

        countries_raw = University.objects.filter(is_published=True).values_list('country', flat=True).distinct()
        countries = sorted([c for c in countries_raw if c])

        target_ids = []
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            target_ids = list(TargetUniversity.objects.filter(student_profile=request.user.profile).values_list('university_id', flat=True))

        context = {
            'universities': universities.distinct(),
            'countries': countries,
            'selected_country': country,
            'query': query,
            'target_ids': target_ids
        }
        return render(request, self.template_name, context)


class UniversityDetailView(View):
    template_name = 'university/detail.html'

    def get(self, request, pk):
        university = get_object_or_404(University, pk=pk)
        is_targeted = False
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            is_targeted = TargetUniversity.objects.filter(
                student_profile=request.user.profile,
                university=university
            ).exists()

        context = {
            'university': university,
            'is_targeted': is_targeted
        }
        return render(request, self.template_name, context)


class ToggleTargetUniversityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        university = get_object_or_404(University, pk=pk)
        target = TargetUniversity.objects.filter(student_profile=profile, university=university).first()

        if target:
            target.delete()
            messages.info(request, f'{university.name} удален из целевых вузов.')
        else:
            TargetUniversity.objects.create(student_profile=profile, university=university)
            messages.success(request, f'{university.name} добавлен в целевые вузы!')

        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'university_list'
        return redirect(next_url)
