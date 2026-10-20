from django.utils import timezone
from django.db import transaction
from django.conf import settings
from apps.attendance.models import AttendanceRecord
from apps.audit.services import log_audit_entry
from .models import CorrectionRequest

def submit_correction_request(
    record: AttendanceRecord,
    new_status: str,
    reason: str,
    user
) -> CorrectionRequest:
    """
    Implements the Hybrid Correction Model:
    1. Faculty may directly correct attendance within 24 hours of creation.
    2. Older or restricted corrections create a formal PENDING request requiring HOD approval.
    """
    if not reason.strip():
        raise ValueError("A justification reason is mandatory for attendance corrections.")

    new_status = new_status.upper()
    if new_status not in ['PRESENT', 'ABSENT']:
        raise ValueError("Target status must be either PRESENT or ABSENT.")

    if record.status == new_status:
        raise ValueError("Target status is identical to current attendance status.")

    window_hours = getattr(settings, 'FACULTY_CORRECTION_WINDOW_HOURS', 24)
    elapsed_seconds = (timezone.now() - record.created_at).total_seconds()
    is_within_window = elapsed_seconds <= (window_hours * 3600)
    is_author = (user == record.marked_by or user == record.session.faculty)

    with transaction.atomic():
        if (is_within_window and is_author) or user.role in ['HOD', 'ADMIN'] or user.is_superuser:
            # Auto-applied under 24-hour faculty grace window or direct HOD action
            orig_status = record.status
            record.status = new_status
            record.save(update_fields=['status', 'updated_at'])

            req = CorrectionRequest.objects.create(
                attendance_record=record,
                requested_by=user,
                original_status=orig_status,
                new_status=new_status,
                reason=reason.strip(),
                status='AUTO_APPLIED',
                reviewed_by=user,
                reviewed_at=timezone.now(),
                review_remarks="Auto-applied under 24-hour faculty correction grace policy."
            )

            # Record in immutable audit log
            log_audit_entry(
                actor=user,
                action_type='CORRECT',
                entity_name='AttendanceRecord',
                entity_id=record.id,
                old_values={'status': orig_status},
                new_values={'status': new_status},
                reason=reason.strip()
            )

            # Re-evaluate threshold warnings
            from apps.notifications.services import evaluate_threshold_for_division
            evaluate_threshold_for_division(record.session.division, record.session.subject)

            return req
        else:
            # Requires HOD Review
            req = CorrectionRequest.objects.create(
                attendance_record=record,
                requested_by=user,
                original_status=record.status,
                new_status=new_status,
                reason=reason.strip(),
                status='PENDING'
            )
            return req

def review_correction_request(
    correction: CorrectionRequest,
    approved: bool,
    reviewer,
    remarks: str = ""
) -> CorrectionRequest:
    """
    HOD/Admin review of a pending attendance correction request.
    """
    if correction.status != 'PENDING':
        raise ValueError(f"Correction request is already {correction.status}.")

    with transaction.atomic():
        correction.reviewed_by = reviewer
        correction.reviewed_at = timezone.now()
        correction.review_remarks = remarks.strip()

        if approved:
            correction.status = 'APPROVED'
            record = correction.attendance_record
            orig_status = record.status
            record.status = correction.new_status
            record.save(update_fields=['status', 'updated_at'])

            log_audit_entry(
                actor=reviewer,
                action_type='APPROVE_CORRECTION',
                entity_name='AttendanceRecord',
                entity_id=record.id,
                old_values={'status': orig_status},
                new_values={'status': correction.new_status},
                reason=f"Approved by {reviewer.full_name}. Remarks: {remarks}"
            )

            from apps.notifications.services import evaluate_threshold_for_division
            evaluate_threshold_for_division(record.session.division, record.session.subject)
        else:
            correction.status = 'REJECTED'
            log_audit_entry(
                actor=reviewer,
                action_type='REJECT_CORRECTION',
                entity_name='AttendanceRecord',
                entity_id=correction.attendance_record_id,
                old_values={'status': correction.original_status},
                new_values={'status': correction.original_status},
                reason=f"Rejected by {reviewer.full_name}. Remarks: {remarks}"
            )

        correction.save()
        return correction
