from django.db import models
from apps.common.models import TimeStampedModel

class Department(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class Program(TimeStampedModel):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='programs')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    duration_years = models.PositiveSmallIntegerField(default=4)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class AcademicYear(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. 2026-2027")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

class Semester(TimeStampedModel):
    TERM_CHOICES = [
        ('ODD', 'Odd Semester'),
        ('EVEN', 'Even Semester'),
    ]

    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='semesters')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='semesters')
    semester_number = models.PositiveSmallIntegerField(help_text="1 to 8")
    term_type = models.CharField(max_length=10, choices=TERM_CHOICES, default='ODD')
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ('program', 'academic_year', 'semester_number')
        ordering = ['program', 'semester_number']

    def __str__(self):
        return f"{self.program.code} - Sem {self.semester_number} ({self.academic_year.name})"

class Division(TimeStampedModel):
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name='divisions')
    name = models.CharField(max_length=50, help_text="e.g. Division A, Div 1")
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('semester', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.semester}"

class Subject(TimeStampedModel):
    TYPE_CHOICES = [
        ('THEORY', 'Theory Only'),
        ('LAB', 'Lab / Practical Only'),
        ('BOTH', 'Theory & Practical'),
    ]

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='subjects')
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name='subjects')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, db_index=True)
    subject_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='THEORY')
    weekly_theory_hours = models.PositiveSmallIntegerField(default=3)
    weekly_lab_hours = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('semester', 'code')
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.subject_type})"
