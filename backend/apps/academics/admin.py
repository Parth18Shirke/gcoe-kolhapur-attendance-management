from django.contrib import admin
from .models import Department, Program, AcademicYear, Semester, Division, Subject

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'duration_years']

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['program', 'academic_year', 'semester_number', 'term_type', 'is_current']

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'subject_type', 'is_active']
    search_fields = ['code', 'name']
