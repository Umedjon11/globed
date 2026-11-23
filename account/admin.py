from django.contrib import admin
from .models import User, StudentProfile, OtpCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'auth_provider', 'is_authed', 'created_at')
    list_filter = ('role', 'auth_provider', 'is_authed')
    search_fields = ('email',)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'username', 'user', 'country', 'grade', 'verified_university', 'is_verified_student', 'verification_status', 'onboarding_completed')
    list_filter = ('is_verified_student', 'verification_status', 'country', 'grade')
    search_fields = ('full_name', 'username', 'user__email', 'university_email', 'student_id_card')
    actions = ['approve_verification', 'reject_verification']

    @admin.action(description='Одобрить верификацию студента вуза')
    def approve_verification(self, request, queryset):
        queryset.update(verification_status='approved', is_verified_student=True)

    @admin.action(description='Отклонить верификацию студента вуза')
    def reject_verification(self, request, queryset):
        queryset.update(verification_status='rejected', is_verified_student=False)

@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'expired_at', 'created_at')
    search_fields = ('user__email', 'code')
