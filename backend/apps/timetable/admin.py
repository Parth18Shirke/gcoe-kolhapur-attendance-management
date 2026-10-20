from django.contrib import admin
from .models import TimetableSlot, LectureSession, LectureTopic

@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'start_time', 'end_time', 'subject', 'division', 'faculty', 'room', 'session_type']
    list_filter = ['day_of_week', 'session_type', 'is_active', 'division']

@admin.register(LectureSession)
class LectureSessionAdmin(admin.ModelAdmin):
    list_display = ['session_date', 'start_time', 'subject', 'division', 'faculty', 'room', 'status', 'session_type']
    list_filter = ['session_date', 'status', 'session_type', 'division']
    search_fields = ['subject__code', 'subject__name', 'faculty__full_name']

@admin.register(LectureTopic)
class LectureTopicAdmin(admin.ModelAdmin):
    list_display = ['session', 'structured_topic', 'created_at']
