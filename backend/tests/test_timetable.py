import pytest
from datetime import date, time
from apps.timetable.models import LectureSession
from apps.timetable.services import (
    find_timetable_conflicts, cancel_lecture_session, reschedule_lecture_session
)

@pytest.mark.django_db
def test_timetable_conflict_detection(academic_setup, faculty_user, other_faculty_user):
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']
    sess_date = date(2026, 10, 12)

    # 1. Existing Session (10:00 - 11:00)
    sess1 = LectureSession.objects.create(
        division=div,
        subject=sub,
        faculty=faculty_user,
        room=room,
        session_date=sess_date,
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='SCHEDULED'
    )

    # 2. Check collision: Same faculty overlapping (10:30 - 11:30)
    conflicts_faculty = find_timetable_conflicts(
        session_date=sess_date,
        start_time=time(10, 30),
        end_time=time(11, 30),
        faculty_id=faculty_user.id,
        division_id=div.id + 999, # different division
        room_id=room.id + 999     # different room
    )
    assert len(conflicts_faculty) == 1
    assert conflicts_faculty[0]['type'] == 'FACULTY_CONFLICT'

    # 3. Check collision: Same room overlapping (09:30 - 10:30)
    conflicts_room = find_timetable_conflicts(
        session_date=sess_date,
        start_time=time(9, 30),
        end_time=time(10, 30),
        faculty_id=other_faculty_user.id,
        division_id=div.id + 999,
        room_id=room.id
    )
    assert len(conflicts_room) == 1
    assert conflicts_room[0]['type'] == 'ROOM_CONFLICT'

    # 4. Check collision: Same division overlapping (10:00 - 11:00)
    conflicts_div = find_timetable_conflicts(
        session_date=sess_date,
        start_time=time(10, 0),
        end_time=time(11, 0),
        faculty_id=other_faculty_user.id,
        division_id=div.id,
        room_id=room.id + 999
    )
    assert len(conflicts_div) == 1
    assert conflicts_div[0]['type'] == 'DIVISION_CONFLICT'

    # 5. Non-overlapping time slot (11:00 - 12:00) -> zero conflicts
    no_conflicts = find_timetable_conflicts(
        session_date=sess_date,
        start_time=time(11, 0),
        end_time=time(12, 0),
        faculty_id=faculty_user.id,
        division_id=div.id,
        room_id=room.id
    )
    assert len(no_conflicts) == 0

@pytest.mark.django_db
def test_lecture_cancellation_preserves_history(academic_setup, faculty_user):
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']

    sess = LectureSession.objects.create(
        division=div,
        subject=sub,
        faculty=faculty_user,
        room=room,
        session_date=date(2026, 10, 15),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='SCHEDULED'
    )

    # Empty reason must raise error
    with pytest.raises(ValueError):
        cancel_lecture_session(sess, faculty_user, "")

    # Cancel with reason
    reason = "Faculty attending mandatory university departmental meeting."
    cancelled = cancel_lecture_session(sess, faculty_user, reason)
    assert cancelled.status == 'CANCELLED'
    assert cancelled.cancellation_reason == reason
    assert cancelled.cancelled_by == faculty_user
    assert cancelled.cancelled_at is not None

    # Verify session remains in DB (never deleted)
    assert LectureSession.objects.filter(id=sess.id).exists()

@pytest.mark.django_db
def test_lecture_rescheduling_lineage(academic_setup, faculty_user):
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']

    orig_sess = LectureSession.objects.create(
        division=div,
        subject=sub,
        faculty=faculty_user,
        room=room,
        session_date=date(2026, 10, 16),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='SCHEDULED'
    )

    new_date = date(2026, 10, 17)
    new_sess = reschedule_lecture_session(
        original_session=orig_sess,
        new_date=new_date,
        new_start_time=time(14, 0),
        new_end_time=time(15, 0),
        user=faculty_user,
        reason="Rain holiday adjustment"
    )

    # Original session must be marked CANCELLED with reschedule reason
    orig_sess.refresh_from_db()
    assert orig_sess.status == 'CANCELLED'
    assert "Rescheduled to" in orig_sess.cancellation_reason

    # New session must point to original session
    assert new_sess.status == 'SCHEDULED'
    assert new_sess.session_date == new_date
    assert new_sess.rescheduled_from == orig_sess
