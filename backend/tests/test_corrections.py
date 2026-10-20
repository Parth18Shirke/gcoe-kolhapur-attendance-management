import pytest
from datetime import date, time, timedelta
from django.utils import timezone
from apps.timetable.models import LectureSession
from apps.attendance.models import AttendanceRecord
from apps.corrections.services import submit_correction_request, review_correction_request
from apps.audit.models import AuditEntry

@pytest.fixture
def sample_record(db, academic_setup, faculty_user):
    sess = LectureSession.objects.create(
        division=academic_setup['division'],
        subject=academic_setup['subject_theory'],
        faculty=faculty_user,
        room=academic_setup['room_class'],
        session_date=date(2026, 10, 10),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='CONDUCTED'
    )
    rec = AttendanceRecord.objects.create(
        session=sess,
        student=academic_setup['students'][0],
        status='ABSENT',
        marked_by=faculty_user
    )
    return rec

@pytest.mark.django_db
def test_faculty_correction_within_24h_is_auto_applied(sample_record, faculty_user):
    assert sample_record.status == 'ABSENT'

    # Correction requested immediately (within 24h window)
    req = submit_correction_request(
        record=sample_record,
        new_status='PRESENT',
        reason="Student was late due to college bus delay, permitted to attend.",
        user=faculty_user
    )

    assert req.status == 'AUTO_APPLIED'
    sample_record.refresh_from_db()
    assert sample_record.status == 'PRESENT'

    # Audit entry must be created
    audit = AuditEntry.objects.filter(entity_name='AttendanceRecord', entity_id=str(sample_record.id)).first()
    assert audit is not None
    assert audit.action_type == 'CORRECT'

@pytest.mark.django_db
def test_faculty_correction_older_than_24h_requires_hod_approval(sample_record, faculty_user, hod_user):
    # Simulate record created 48 hours ago
    sample_record.created_at = timezone.now() - timedelta(hours=48)
    sample_record.save(update_fields=['created_at'])

    req = submit_correction_request(
        record=sample_record,
        new_status='PRESENT',
        reason="Administrative reconciliation after paper roster verification.",
        user=faculty_user
    )

    # Must be routed to HOD
    assert req.status == 'PENDING'
    sample_record.refresh_from_db()
    assert sample_record.status == 'ABSENT' # Not updated yet!

    # HOD reviews and approves
    reviewed = review_correction_request(
        correction=req,
        approved=True,
        reviewer=hod_user,
        remarks="Verified against paper sign-in sheet."
    )
    assert reviewed.status == 'APPROVED'
    sample_record.refresh_from_db()
    assert sample_record.status == 'PRESENT'
