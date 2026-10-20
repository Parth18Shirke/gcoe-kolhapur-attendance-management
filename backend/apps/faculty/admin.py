from django.contrib import admin
from .models import FacultyAssignment

@admin.register(FacultyAssignment)
class FacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ['faculty', 'subject', 'division', 'academic_year', 'is_primary']
    list_filter = ['division', 'subject', 'academic_year', 'is_primary']
    search_fields = ['faculty__full_name', 'subject__name', 'division__name']
