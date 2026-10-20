from typing import Dict, Any, List, Optional
import uuid
from django.db import transaction
from django.utils import timezone
from apps.timetable.models import LectureSession, LectureTopic
from apps.attendance.models import AttendanceSessionState
from apps.attendance.services import record_roster_attendance
from apps.audit.services import log_audit_entry
from .models import SyncIdempotencyLog

class SyncConflictError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}

def process_offline_sync(
    idempotency_key: uuid.UUID,
    session_id: int,
    records: List[Dict[str, Any]],
    user,
    structured_topic: str = "",
    free_text_notes: str = "",
    mode: str = "MODE_1_ALL_PRESENT",
    finalize: bool = True
) -> Dict[str, Any]:
    """
    Server-Authoritative Offline Attendance Synchronization:
    1. Idempotency Check: if idempotency_key was already processed, returns cached response immediately.
    2. Session & Authorization Checks.
    3. Conflict Detection: checks if session was locked/finalized or cancelled.
    4. Ingestion & conservative finalization evaluation.
    """
    # 1. Idempotency Check
    existing_log = SyncIdempotencyLog.objects.filter(idempotency_key=idempotency_key).first()
    if existing_log:
        return existing_log.response_payload

    # 2. Session Validation
    try:
        session = LectureSession.objects.select_related('division', 'faculty', 'subject').get(id=session_id)
    except LectureSession.DoesNotExist:
        raise ValueError("Target lecture session does not exist.")

    # Authorization Check
    if user.role == 'FACULTY' and session.faculty != user:
        raise PermissionError("You are not authorized to sync attendance for this session.")

    # 3. Conflict Detection
    if session.is_cancelled:
        raise SyncConflictError(
            "Conflict: This lecture session has been cancelled and cannot accept attendance.",
            details={'session_id': session.id, 'status': 'CANCELLED', 'cancellation_reason': session.cancellation_reason}
        )

    state, _ = AttendanceSessionState.objects.get_or_create(session=session)
    if state.status == 'FINALIZED' and user.role == 'FACULTY':
        raise SyncConflictError(
            "Conflict: This session has already been finalized and locked on the server.",
            details={'session_id': session.id, 'finalized_at': str(state.finalized_at)}
        )

    with transaction.atomic():
        # Update topic log if provided
        if structured_topic.strip() or free_text_notes.strip():
            LectureTopic.objects.update_or_create(
                session=session,
                defaults={
                    'structured_topic': structured_topic.strip(),
                    'free_text_notes': free_text_notes.strip()
                }
            )

        # Ingest marks
        res = record_roster_attendance(
            session=session,
            records_data=records,
            user=user,
            mode=mode,
            finalize=finalize
        )

        response_data = {
            'success': res.get('success', False),
            'idempotency_key': str(idempotency_key),
            'session_id': session.id,
            'state': res.get('state'),
            'total_marked': res.get('total_marked', 0),
            'unmarked_count': res.get('unmarked_count', 0),
            'message': res.get('message', 'Attendance successfully synchronized.')
        }

        # Log audit entry
        log_audit_entry(
            actor=user,
            action_type='SYNC_ATTENDANCE',
            entity_name='LectureSession',
            entity_id=session.id,
            new_values={'idempotency_key': str(idempotency_key), 'records_count': len(records), 'finalize': finalize},
            reason="Offline synchronization ingestion"
        )

        # Cache outcome for idempotency
        SyncIdempotencyLog.objects.create(
            idempotency_key=idempotency_key,
            user=user,
            session=session,
            status='SUCCESS' if response_data['success'] else 'CONFLICT',
            response_payload=response_data
        )

        return response_data
