from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class AttendanceSessionState(TimeStampedModel):
    STATE_CHOICES = [
        ('DRAFT', 'Draft / In-Progress'),
        ('REVIEWED', 'Reviewed by Faculty'),
        ('FINALIZED', 'Finalized & Locked'),
        ('INCOMPLETE_RECORDS', 'Flagged: Incomplete Records'),
    ]
    MODE_CHOICES = [
        ('MODE_1_ALL_PRESENT', 'Mode 1: Default Present (Mark Absent)'),
        ('MODE_2_ALL_ABSENT', 'Mode 2: Default Absent (Mark Present)'),
    ]

    session = models.OneToOneField(
        'timetable.LectureSession',
        on_delete=models.CASCADE,
        related_name='lifecycle_state'
    )
    status = models.CharField(max_length=25, choices=STATE_CHOICES, default='DRAFT', db_index=True)
    mode = models.CharField(max_length=25, choices=MODE_CHOICES, default='MODE_1_ALL_PRESENT')
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finalized_sessions'
    )
    finalized_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session #{self.session_id} [{self.status}]"

class AttendanceRecord(TimeStampedModel):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    ]

    session = models.ForeignKey(
        'timetable.LectureSession',
        on_delete=models.PROTECT,
        related_name='attendance_records'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
        related_name='attendance_records'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT', db_index=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='marked_attendance_records'
    )

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['student__roll_number']
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['student', 'status']),
        ]

    def __str__(self):
        return f"{self.student.roll_number} - {self.session.subject.code}: {self.status}"
