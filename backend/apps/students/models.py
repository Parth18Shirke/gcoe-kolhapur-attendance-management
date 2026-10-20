from django.db import models
from apps.common.models import TimeStampedModel

class Student(TimeStampedModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ARCHIVED', 'Archived / Graduated'),
    ]

    prn = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Full University Permanent Registration Number (e.g. 23060361241234)"
    )
    roll_number = models.CharField(max_length=30, db_index=True, help_text="Class Roll No (e.g. IT-01)")
    full_name = models.CharField(max_length=200)
    official_email = models.EmailField(unique=True, db_index=True)
    division = models.ForeignKey(
        'academics.Division',
        on_delete=models.PROTECT,
        related_name='students'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)

    class Meta:
        ordering = ['roll_number', 'full_name']
        unique_together = ('division', 'roll_number')

    def __str__(self):
        return f"{self.classroom_display} ({self.division.name})"

    @property
    def last_4_prn(self) -> str:
        """Returns the last 4 digits of the PRN for classroom display privacy."""
        if len(self.prn) >= 4:
            return self.prn[-4:]
        return self.prn

    @property
    def classroom_display(self) -> str:
        """Formats the student display according to the institutional privacy mandate: 1234 — Rahul Sharma"""
        return f"{self.last_4_prn} — {self.full_name}"

class StudentImportLog(TimeStampedModel):
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_imports'
    )
    file_name = models.CharField(max_length=255)
    total_rows = models.PositiveIntegerField(default=0)
    imported_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    error_details = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Import {self.file_name} ({self.imported_count} imported, {self.error_count} errors)"
