from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied

class AuditEntry(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete / Archive Record'),
        ('FINALIZE', 'Finalize Attendance Session'),
        ('CORRECT', 'Direct Attendance Correction'),
        ('APPROVE_CORRECTION', 'Approve Correction Request'),
        ('REJECT_CORRECTION', 'Reject Correction Request'),
        ('CANCEL_SESSION', 'Cancel Lecture Session'),
        ('RESCHEDULE_SESSION', 'Reschedule Lecture Session'),
        ('SYNC_ATTENDANCE', 'Offline Ingestion Sync'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions'
    )
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, db_index=True)
    entity_name = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=64, db_index=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)
    client_ip = models.CharField(max_length=45, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Entry'
        verbose_name_plural = 'Audit Entries'

    def __str__(self):
        actor_name = self.actor.full_name if self.actor else 'SYSTEM'
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {actor_name} -> {self.action_type} on {self.entity_name}#{self.entity_id}"

    def save(self, *args, **kwargs):
        # Enforce immutability: once created, an audit record cannot be modified
        if self.pk:
            raise PermissionDenied("Audit records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Enforce immutability: audit records cannot be deleted
        raise PermissionDenied("Audit records are immutable institutional records and cannot be deleted.")
