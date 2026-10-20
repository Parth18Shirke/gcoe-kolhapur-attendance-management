from django.db import models
from apps.common.models import TimeStampedModel

class NotificationState(TimeStampedModel):
    """
    Maintains the threshold compliance state machine per student per subject:
    1. Triggers immediate alert when crossing below 75%.
    2. Enforces non-aggressive cooldown before reminders.
    3. Resets state cleanly when student attendance recovers >= 75.00%.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='notification_states'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='notification_states'
    )
    is_currently_deficient = models.BooleanField(default=False, db_index=True)
    last_percentage = models.FloatField(default=100.0)
    first_notified_at = models.DateTimeField(null=True, blank=True)
    last_reminded_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'subject')
        ordering = ['student', 'subject']

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code} [{'DEFICIENT' if self.is_currently_deficient else 'COMPLIANT'}]"

class NotificationOutbox(TimeStampedModel):
    TYPE_CHOICES = [
        ('THRESHOLD_75_WARNING', 'Threshold 75% Warning'),
        ('ATTENDANCE_CORRECTION', 'Attendance Correction Notice'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Transmission'),
        ('SENT', 'Transmitted Successfully'),
        ('FAILED', 'Transmission Failed'),
    ]

    recipient_email = models.EmailField(db_index=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_received'
    )
    subject_line = models.CharField(max_length=255)
    body_text = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='THRESHOLD_75_WARNING')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Outbox #{self.id} -> {self.recipient_email} [{self.status}]"
