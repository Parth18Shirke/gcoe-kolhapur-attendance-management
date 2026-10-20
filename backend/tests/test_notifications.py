import pytest
from datetime import date, time
from apps.timetable.models import LectureSession
from apps.attendance.models import AttendanceRecord
from apps.notifications.models import NotificationOutbox, NotificationState
from apps.notifications.services import evaluate_threshold_for_division, process_outbox_queue

@pytest.mark.django_db
def test_notification_threshold_crossing_and_recovery(academic_setup, faculty_user):
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']
    student = academic_setup['students'][0]

    # Create 4 conducted sessions: student attended 2, absent in 2 -> 50% (< 75%)
    for i in range(4):
        sess = LectureSession.objects.create(
            division=div,
            subject=sub,
            faculty=faculty_user,
            room=room,
            session_date=date(2026, 10, i + 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status='CONDUCTED'
        )
        AttendanceRecord.objects.create(
            session=sess,
            student=student,
            status='PRESENT' if i < 2 else 'ABSENT',
            marked_by=faculty_user
        )

    # 1. Trigger threshold evaluation
    evaluate_threshold_for_division(div, sub)

    # Should create outbox alert
    outbox_item = NotificationOutbox.objects.filter(student=student, status='PENDING').first()
    assert outbox_item is not None
    assert "ATTENDANCE WARNING" in outbox_item.subject_line
    assert outbox_item.recipient_email == student.official_email

    state = NotificationState.objects.get(student=student, subject=sub)
    assert state.is_currently_deficient is True
    assert state.reminder_count == 1

    # 2. Process outbox queue
    dispatched = process_outbox_queue()
    assert dispatched >= 1
    outbox_item.refresh_from_db()
    assert outbox_item.status == 'SENT'

    # 3. Simulate Student Recovery: Student attends 6 consecutive lectures -> 8/10 = 80.00% (>= 75%)
    for i in range(4, 10):
        sess = LectureSession.objects.create(
            division=div,
            subject=sub,
            faculty=faculty_user,
            room=room,
            session_date=date(2026, 10, i + 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status='CONDUCTED'
        )
        AttendanceRecord.objects.create(
            session=sess,
            student=student,
            status='PRESENT',
            marked_by=faculty_user
        )

    # Re-evaluate
    evaluate_threshold_for_division(div, sub)

    state.refresh_from_db()
    assert state.is_currently_deficient is False # Reset!
    assert state.reminder_count == 0
