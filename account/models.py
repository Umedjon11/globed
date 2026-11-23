from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from university.models import University

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email is required!')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwrags):
        kwrags.setdefault('role', 'super_admin')
        kwrags.setdefault('is_superuser', True)
        kwrags.setdefault('is_authed', True)

        if kwrags.get('role') != 'super_admin':
            raise ValueError('Role must be super_admin!')
        
        if not kwrags.get('is_superuser'):
            raise ValueError('Is superuser must be true!')

        email = self.normalize_email(email)
        return self.create_user(email, password, **kwrags)

class User(AbstractBaseUser, PermissionsMixin):
    AUTH_PROVIDER = (
        ('google', 'Google'),
        ('email', 'Email')
    )

    ROLE = (
        ('student', 'student'),
        ('content_manager', 'content_manager'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
        ('super_admin', 'super_admin')
    )

    email = models.EmailField(unique=True, max_length=254)
    auth_provider = models.CharField(choices=AUTH_PROVIDER, default='email', max_length=50)
    role = models.CharField(choices=ROLE, default='student', max_length=50)
    language = models.CharField(default='ru', max_length=10)
    is_authed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def is_staff(self):
        return self.role in ['admin', 'super_admin', 'content_manager', 'moderator']

    def __str__(self):
        return self.email

class StudentProfile(models.Model):
    VERIFICATION_STATUS = (
        ('none', 'none'),
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(unique=True, max_length=150)
    full_name = models.CharField(max_length=100)
    avatar_url = models.ImageField(upload_to='avatar/', null=True, blank=True)
    country = models.CharField(max_length=100, default='Таджикистан')
    grade = models.PositiveIntegerField(default=10)
    timezone = models.CharField(max_length=50, default='Asia/Dushanbe')
    onboarding_completed = models.BooleanField(default=False)
    is_verified_student = models.BooleanField(default=False)
    verified_university = models.ForeignKey(University, on_delete=models.SET_NULL, related_name='university_students', null=True, blank=True)
    verification_status = models.CharField(choices=VERIFICATION_STATUS, default='none', max_length=20)
    student_id_card = models.CharField(max_length=100, blank=True, default='')
    university_email = models.EmailField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.full_name}"

class OtpCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"
