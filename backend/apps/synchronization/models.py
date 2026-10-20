import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class SyncIdempotencyLog(TimeStampedModel):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sync_operations'
    )
    session = models.ForeignKey(
        'timetable.LectureSession',
        on_delete=models.CASCADE,
        related_name='sync_operations'
    )
    status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('CONFLICT', 'Conflict'), ('REJECTED', 'Rejected')],
        default='SUCCESS'
    )
    response_payload = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sync {self.idempotency_key} by {self.user.full_name} -> {self.status}"
