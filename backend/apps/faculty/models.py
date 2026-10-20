from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class FacultyAssignment(TimeStampedModel):
    """
    Represents an institutional workload assignment:
    Admin or HOD allocates a specific faculty member to teach a subject for a specific division.
    Faculty cannot arbitrarily allocate subjects to themselves.
    """
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_assignments'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.PROTECT,
        related_name='faculty_assignments'
    )
    division = models.ForeignKey(
        'academics.Division',
        on_delete=models.PROTECT,
        related_name='faculty_assignments'
    )
    academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.PROTECT,
        related_name='faculty_assignments'
    )
    is_primary = models.BooleanField(default=True, help_text="Designates the primary lead instructor")

    class Meta:
        unique_together = ('faculty', 'subject', 'division', 'academic_year')
        ordering = ['faculty__full_name', 'subject__name']

    def __str__(self):
        return f"{self.faculty.full_name} -> {self.subject.code} ({self.division.name})"
