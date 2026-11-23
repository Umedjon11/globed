from django.forms import ModelForm, Form
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import OtpCode, StudentProfile
from random import randint
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
            'placeholder': 'name@example.com'
        }),
        label="Email или имя пользователя"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
            'placeholder': 'Введите пароль'
        }),
        label="Пароль"
    )

class RegisterForm(ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
            'placeholder': 'New Password'
        }),
        label="Password",
        help_text="Password must be at least 8 chars."
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
            'placeholder': 'Repit Password'
        }),
        label="Confirm Passwords"
    )

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'example@mail.com'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        if User.objects.filter(email = email).exists():
            return ValidationError('This email is already used!')

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords does not matched!')
            else:
                validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data.get('password'))

        email = self.cleaned_data.get('email')
        code = randint(100000, 999999)
        now = timezone.now()
        expires_minute = timedelta(minutes=10)
        expired_at = now + expires_minute

        if commit:
            user.save()
        
        OtpCode.objects.create(
            user = user,
            code = code,
            expired_at = expired_at
        )


        message = f"""
        <!DOCTYPE html>
        <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Подтверждение email — Globed.ai</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script>
                    tailwind.config = {{
                        theme: {{
                            extend: {{
                                colors: {{
                                    lightBg: '#ffffff',
                                    cardBg: '#fafafa',
                                    borderLight: '#e5e5e5',
                                }}
                            }}
                        }}
                    }}
                </script>
            </head>
            <body class="bg-lightBg text-neutral-900 font-sans antialiased selection:bg-black selection:text-white flex flex-col min-h-screen">

                <header class="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-borderLight">
                    <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <a href="#" class="text-2xl font-black tracking-tight text-black">Globed<span class="text-neutral-400">.ai</span></a>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="text-sm text-neutral-600">Не получили код?</span>
                            <a href="#" class="text-sm font-medium text-black underline hover:text-neutral-700 transition">Отправить снова</a>
                        </div>
                    </div>
                </header>

                <main class="flex-grow flex items-center justify-center px-4 py-16">
                    <div class="w-full max-w-md bg-cardBg border border-borderLight p-8 sm:p-10 rounded-3xl shadow-xl shadow-black/5 text-center">
                        <div class="w-12 h-12 bg-neutral-100 border border-borderLight rounded-2xl flex items-center justify-center text-xl font-bold mx-auto mb-6 shadow-sm">✉️</div>

                        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight mb-2 text-black">Введите код подтверждения</h1>
                        <p class="text-sm text-neutral-600 mb-8">Мы отправили 6-значный одноразовый код (OTP) на ваш адрес электронной почты. Срок действия кода ограничен[cite: 1].</p>

                        <div class="bg-white border border-borderLight rounded-2xl p-6 mb-6 shadow-sm">
                            <span class="text-xs font-semibold text-neutral-400 uppercase tracking-wider block mb-1">Ваш одноразовый код:</span>
                            <span class="text-3xl font-mono font-black tracking-widest text-black">{code}</span>
                        </div>

                        <p class="text-xs text-neutral-500">
                            Введите этот код на сайте для завершения регистрации. Если вы не запрашивали регистрацию, просто проигнорируйте это письмо.
                        </p>
                    </div>
                </main>

                <footer class="py-8 bg-lightBg text-xs text-neutral-500 border-t border-borderLight text-center">
                    &copy; 2026 Globed.ai[cite: 1]. Все права защищены.
                </footer>

            </body>
        </html>
        """

        send_mail(
            subject=f'Ваш код подтверждения: {code}',
            message=message,
            html_message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True
        )

        return user


class VerifyEmailForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-center tracking-widest text-lg font-mono focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
            'placeholder': '123456',
            'autocomplete': 'one-time-code'
        }),
        label="Код подтверждения",
        help_text="Введите код, отправленный на вашу электронную почту."
    )


class ProfileForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['username', 'full_name', 'country', 'grade', 'avatar_url']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'umedjon_student'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'Умеджон Назаров'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'Таджикистан'
            }),
            'grade': forms.NumberInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': '11',
                'min': '7',
                'max': '16'
            }),
            'avatar_url': forms.FileInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3 text-neutral-900 text-sm focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-neutral-100 file:text-black hover:file:bg-neutral-200'
            })
        }
        labels = {
            'username': 'Имя пользователя',
            'full_name': 'Полное имя',
            'country': 'Страна',
            'grade': 'Класс или курс',
            'avatar_url': 'Аватар (фото)'
        }


class StudentVerificationForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['verified_university', 'university_email', 'student_id_card']
        widgets = {
            'verified_university': forms.Select(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'required': 'required'
            }),
            'university_email': forms.EmailInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'student@harvard.edu'
            }),
            'student_id_card': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'ID студенческого билета'
            })
        }
        labels = {
            'verified_university': 'Университет, в котором вы учитесь',
            'university_email': 'Университетская почта (.edu / официальный email вуза)',
            'student_id_card': 'Номер студенческого билета или ID'
        }
