from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class CorrectionRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending HOD Approval'),
        ('APPROVED', 'Approved & Applied'),
        ('REJECTED', 'Rejected'),
        ('AUTO_APPLIED', 'Auto-Applied (24h Faculty Window)'),
    ]

    attendance_record = models.ForeignKey(
        'attendance.AttendanceRecord',
        on_delete=models.PROTECT,
        related_name='correction_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submitted_corrections'
    )
    original_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    reason = models.TextField(help_text="Mandatory institutional justification for modifying an academic record")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING', db_index=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_corrections'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Correction #{self.id} for Record #{self.attendance_record_id} ({self.original_status} -> {self.new_status}) [{self.status}]"
