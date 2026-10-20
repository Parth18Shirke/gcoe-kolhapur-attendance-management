from django.contrib import admin
from .models import AttendanceRecord, AttendanceSessionState

@admin.register(AttendanceSessionState)
class AttendanceSessionStateAdmin(admin.ModelAdmin):
    list_display = ['session', 'status', 'mode', 'finalized_by', 'finalized_at']
    list_filter = ['status', 'mode']

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'status', 'marked_by', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__full_name', 'student__roll_number', 'session__subject__name']
