from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class TimetableSlot(TimeStampedModel):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    SESSION_TYPES = [
        ('THEORY', 'Theory Lecture'),
        ('LAB', 'Lab / Practical Session'),
    ]

    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT, related_name='slots')
    division = models.ForeignKey('academics.Division', on_delete=models.PROTECT, related_name='slots')
    subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='slots')
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='slots')
    room = models.ForeignKey('rooms.Room', on_delete=models.PROTECT, related_name='slots')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES, db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='THEORY')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} | {self.subject.code} ({self.division.name})"

class LectureSession(TimeStampedModel):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONDUCTED', 'Conducted'),
        ('CANCELLED', 'Cancelled'),
    ]
    SESSION_TYPES = [
        ('THEORY', 'Theory Lecture'),
        ('LAB', 'Lab / Practical Session'),
    ]

    slot = models.ForeignKey(TimetableSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    division = models.ForeignKey('academics.Division', on_delete=models.PROTECT, related_name='sessions')
    subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='sessions')
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sessions')
    room = models.ForeignKey('rooms.Room', on_delete=models.PROTECT, related_name='sessions')
    session_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Duration in minutes (e.g. 60m for theory, 120m for lab)")
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='THEORY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', db_index=True)

    # Rescheduling Lineage: preserves original scheduled event
    rescheduled_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_occurrences'
    )

    # Cancellation Metadata: cancelled sessions are never deleted
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancellations_initiated'
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['session_date', 'start_time']
        indexes = [
            models.Index(fields=['session_date', 'faculty']),
            models.Index(fields=['session_date', 'division']),
        ]

    def __str__(self):
        return f"{self.session_date} {self.start_time.strftime('%H:%M')} | {self.subject.code} - {self.division.name} ({self.status})"

    @property
    def is_cancelled(self) -> bool:
        return self.status == 'CANCELLED'

    @property
    def is_conducted(self) -> bool:
        return self.status == 'CONDUCTED'

class LectureTopic(TimeStampedModel):
    session = models.OneToOneField(LectureSession, on_delete=models.CASCADE, related_name='topic_log')
    structured_topic = models.CharField(max_length=255, blank=True, help_text="Syllabus unit or curriculum point")
    free_text_notes = models.TextField(blank=True, help_text="Actual pedagogical delivery notes")

    def __str__(self):
        return f"Topics for Session #{self.session_id}: {self.structured_topic or 'General Notes'}"
