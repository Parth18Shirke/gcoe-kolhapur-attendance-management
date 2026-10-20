from django.contrib import admin
from .models import NotificationState, NotificationOutbox

@admin.register(NotificationState)
class NotificationStateAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'is_currently_deficient', 'last_percentage', 'reminder_count', 'last_reminded_at']
    list_filter = ['is_currently_deficient', 'subject']

@admin.register(NotificationOutbox)
class NotificationOutboxAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_email', 'subject_line', 'notification_type', 'status', 'retry_count', 'created_at']
    list_filter = ['status', 'notification_type']
