from django.contrib import admin
from .models import Student, StudentImportLog

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'full_name', 'last_4_prn', 'division', 'official_email', 'status']
    list_filter = ['division', 'status']
    search_fields = ['roll_number', 'full_name', 'prn', 'official_email']

@admin.register(StudentImportLog)
class StudentImportLogAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'uploaded_by', 'total_rows', 'imported_count', 'updated_count', 'error_count', 'created_at']
