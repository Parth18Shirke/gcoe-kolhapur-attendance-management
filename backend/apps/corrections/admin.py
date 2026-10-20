from django.contrib import admin
from .models import CorrectionRequest

@admin.register(CorrectionRequest)
class CorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'attendance_record', 'original_status', 'new_status', 'status', 'requested_by', 'reviewed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reason', 'requested_by__full_name']
