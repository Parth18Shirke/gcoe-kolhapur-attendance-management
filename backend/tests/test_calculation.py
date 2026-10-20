import pytest
from datetime import date, time
from apps.timetable.models import LectureSession
from apps.attendance.models import AttendanceRecord
from apps.attendance.services import calculate_student_attendance

@pytest.mark.django_db
def test_calculation_exact_75_percent_threshold(academic_setup, faculty_user):
    """
    Statutory Rule:
    attendance < 75% means below threshold.
    Exactly 75.00% is NOT below threshold.
    """
    student = academic_setup['students'][0]
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']

    # Create 4 conducted sessions: student attended 3, absent in 1 -> 3/4 = 75.00%
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
        status_val = 'PRESENT' if i < 3 else 'ABSENT'
        AttendanceRecord.objects.create(
            session=sess,
            student=student,
            status=status_val,
            marked_by=faculty_user
        )

    metrics = calculate_student_attendance(student, subject_id=sub.id)
    assert metrics['total_conducted'] == 4
    assert metrics['total_attended'] == 3
    assert metrics['overall_percentage'] == 75.00
    assert metrics['is_deficient'] is False # Exactly 75.00% is COMPLIANT

@pytest.mark.django_db
def test_calculation_strictly_below_75_percent(academic_setup, faculty_user):
    """
    If student attends 2 out of 4 sessions -> 50.00% -> strictly deficient (< 75%).
    """
    student = academic_setup['students'][0]
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']

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
        status_val = 'PRESENT' if i < 2 else 'ABSENT'
        AttendanceRecord.objects.create(
            session=sess,
            student=student,
            status=status_val,
            marked_by=faculty_user
        )

    metrics = calculate_student_attendance(student, subject_id=sub.id)
    assert metrics['total_conducted'] == 4
    assert metrics['total_attended'] == 2
    assert metrics['overall_percentage'] == 50.00
    assert metrics['is_deficient'] is True # Below 75%

@pytest.mark.django_db
def test_cancelled_sessions_excluded_from_denominator(academic_setup, faculty_user):
    student = academic_setup['students'][0]
    div = academic_setup['division']
    sub = academic_setup['subject_theory']
    room = academic_setup['room_class']

    # 2 Conducted sessions (student attended both)
    for i in range(2):
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

    # 1 CANCELLED session
    LectureSession.objects.create(
        division=div,
        subject=sub,
        faculty=faculty_user,
        room=room,
        session_date=date(2026, 10, 5),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='CANCELLED',
        cancellation_reason="College sports day"
    )

    # Denominator should be 2, not 3! Percentage should be 100%, not 66.6%
    metrics = calculate_student_attendance(student, subject_id=sub.id)
    assert metrics['total_conducted'] == 2
    assert metrics['total_attended'] == 2
    assert metrics['overall_percentage'] == 100.00
    assert metrics['is_deficient'] is False
