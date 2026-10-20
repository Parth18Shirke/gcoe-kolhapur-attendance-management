import pytest
from datetime import date, time
from apps.timetable.models import LectureSession
from apps.attendance.models import AttendanceRecord, AttendanceSessionState
from apps.attendance.services import record_roster_attendance

@pytest.fixture
def test_session(db, academic_setup, faculty_user):
    return LectureSession.objects.create(
        division=academic_setup['division'],
        subject=academic_setup['subject_theory'],
        faculty=faculty_user,
        room=academic_setup['room_class'],
        session_date=date(2026, 10, 18),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='SCHEDULED'
    )

@pytest.mark.django_db
def test_attendance_roster_view(auth_client_faculty, test_session, academic_setup):
    resp = auth_client_faculty.get(f'/api/v1/attendance/sessions/{test_session.id}/roster/')
    assert resp.status_code == 200
    assert resp.data['success'] is True
    assert resp.data['total_students'] == 4
    first_student = resp.data['roster'][0]
    assert first_student['classroom_display'] == '1001 — Student 1'
    assert 'prn' not in first_student

@pytest.mark.django_db
def test_conservative_finalization_refuses_to_guess_unrecorded(test_session, academic_setup, faculty_user):
    students = academic_setup['students'] # 4 students

    # Submit attendance for only 2 out of 4 students, with finalize=True
    partial_records = [
        {'student_id': students[0].id, 'status': 'PRESENT'},
        {'student_id': students[1].id, 'status': 'ABSENT'},
    ]

    res = record_roster_attendance(
        session=test_session,
        records_data=partial_records,
        user=faculty_user,
        finalize=True
    )

    # Invariant: Must NOT guess missing students!
    assert res['success'] is False
    assert res['code'] == 'INCOMPLETE_RECORDS'
    assert res['unmarked_count'] == 2

    state = AttendanceSessionState.objects.get(session=test_session)
    assert state.status == 'INCOMPLETE_RECORDS'
    test_session.refresh_from_db()
    assert test_session.status != 'CONDUCTED' # Session is not marked conducted

@pytest.mark.django_db
def test_full_finalization_marks_conducted(test_session, academic_setup, faculty_user):
    students = academic_setup['students'] # 4 students

    all_records = [
        {'student_id': students[0].id, 'status': 'PRESENT'},
        {'student_id': students[1].id, 'status': 'PRESENT'},
        {'student_id': students[2].id, 'status': 'PRESENT'},
        {'student_id': students[3].id, 'status': 'ABSENT'},
    ]

    res = record_roster_attendance(
        session=test_session,
        records_data=all_records,
        user=faculty_user,
        finalize=True
    )

    assert res['success'] is True
    assert res['state'] == 'FINALIZED'
    assert res['unmarked_count'] == 0

    state = AttendanceSessionState.objects.get(session=test_session)
    assert state.status == 'FINALIZED'
    assert state.finalized_by == faculty_user
    assert state.finalized_at is not None

    test_session.refresh_from_db()
    assert test_session.status == 'CONDUCTED'
