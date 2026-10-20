import uuid
import pytest
from datetime import date, time
from apps.timetable.models import LectureSession
from apps.attendance.models import AttendanceSessionState
from apps.synchronization.services import process_offline_sync, SyncConflictError
from apps.synchronization.models import SyncIdempotencyLog

@pytest.fixture
def scheduled_session(db, academic_setup, faculty_user):
    return LectureSession.objects.create(
        division=academic_setup['division'],
        subject=academic_setup['subject_theory'],
        faculty=faculty_user,
        room=academic_setup['room_class'],
        session_date=date(2026, 10, 20),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='SCHEDULED'
    )

@pytest.mark.django_db
def test_offline_sync_idempotency(scheduled_session, academic_setup, faculty_user):
    students = academic_setup['students']
    records = [{'student_id': s.id, 'status': 'PRESENT'} for s in students]
    idempotency_key = uuid.uuid4()

    # First Sync
    res1 = process_offline_sync(
        idempotency_key=idempotency_key,
        session_id=scheduled_session.id,
        records=records,
        user=faculty_user,
        structured_topic="Database Indexing Concepts",
        finalize=True
    )
    assert res1['success'] is True
    assert res1['state'] == 'FINALIZED'
    assert SyncIdempotencyLog.objects.filter(idempotency_key=idempotency_key).exists()

    # Second Sync with identical key (simulating network retry)
    res2 = process_offline_sync(
        idempotency_key=idempotency_key,
        session_id=scheduled_session.id,
        records=records,
        user=faculty_user,
        finalize=True
    )
    assert res2 == res1 # Returns cached response identical to first run!

@pytest.mark.django_db
def test_offline_sync_conflict_on_cancelled_session(scheduled_session, academic_setup, faculty_user):
    scheduled_session.status = 'CANCELLED'
    scheduled_session.cancellation_reason = "Holiday"
    scheduled_session.save()

    students = academic_setup['students']
    records = [{'student_id': s.id, 'status': 'PRESENT'} for s in students]

    with pytest.raises(SyncConflictError) as exc_info:
        process_offline_sync(
            idempotency_key=uuid.uuid4(),
            session_id=scheduled_session.id,
            records=records,
            user=faculty_user
        )
    assert "cancelled" in str(exc_info.value)
