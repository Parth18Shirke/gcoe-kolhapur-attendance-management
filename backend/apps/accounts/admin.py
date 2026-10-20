from django.contrib import admin
from .models import User, EmailOTP, UserToken, OTPRateLimit

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'department', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['email', 'full_name']

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'expires_at', 'attempts_remaining', 'is_used', 'created_at']
    list_filter = ['is_used']

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created_at', 'expires_at']
