from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView
from django.views import View
from datetime import datetime
from django.urls import reverse_lazy
from .forms import *
from .models import User, StudentProfile, OtpCode
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib import messages

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('verify_account', email='')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return redirect(f"/auth/{user.email}/verify/?next={next_url}")
        return redirect('verify_account', email=user.email)


class VerifyAccountView(View):
    template_name = 'account/verify.html'

    def get(self, request, email):
        form = VerifyEmailForm()

        if request.user.is_authenticated:
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form, 'email': email})

    def post(self, request, email):
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            
            try:
                otp_record = OtpCode.objects.filter(
                    user__email=email, 
                    code=entered_code, 
                    expired_at__gte=timezone.now()
                ).latest('created_at')

                if otp_record:
                    user = get_object_or_404(User, email=email)
                    user.is_authed = True
                    user.save()

                    login(request, user=user)

                    next_url = request.GET.get('next') or request.POST.get('next')
                    if not hasattr(user, 'profile'):
                        return redirect('profile_setup')
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard')
                
            except OtpCode.DoesNotExist:
                form.add_error('code', 'Неверный или просроченный код подтверждения.')

        return render(request, self.template_name, {'form': form, 'email': email})


class LoginUserView(LoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        if hasattr(self.request.user, 'profile'):
            return reverse_lazy('dashboard')
        return reverse_lazy('profile_setup')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


class ProfileSetupView(LoginRequiredMixin, View):
    template_name = 'account/profile_setup.html'

    def get(self, request):
        if hasattr(request.user, 'profile'):
            return redirect('dashboard')
        form = ProfileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if hasattr(request.user, 'profile'):
            return redirect('dashboard')
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            from study.models import StreakRecord, XPEvent
            StreakRecord.objects.get_or_create(student=profile)
            XPEvent.objects.create(student=profile, points=50, reason='Создание профиля')
            return redirect('university_list')
        return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'account/profile.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')
        form = ProfileForm(instance=profile)
        return render(request, self.template_name, {'profile': profile, 'form': form})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        return render(request, self.template_name, {'profile': profile, 'form': form})


class StudentVerificationView(LoginRequiredMixin, View):
    template_name = 'account/student_verify.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')
        form = StudentVerificationForm(instance=profile)
        return render(request, self.template_name, {'profile': profile, 'form': form})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')
        form = StudentVerificationForm(request.POST, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            prof.verification_status = 'pending'
            prof.is_verified_student = False
            prof.save()
            messages.info(request, 'Ваша заявка на статус студента отправлена на проверку модераторам.')
            return redirect('student_verify')
        return render(request, self.template_name, {'profile': profile, 'form': form})


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return redirect('home')
