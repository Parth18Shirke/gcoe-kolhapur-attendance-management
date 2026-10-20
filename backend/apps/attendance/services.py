from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from apps.timetable.models import LectureSession
from apps.students.models import Student
from .models import AttendanceSessionState, AttendanceRecord

def record_roster_attendance(
    session: LectureSession,
    records_data: List[Dict[str, Any]],
    user,
    mode: str = 'MODE_1_ALL_PRESENT',
    finalize: bool = False
) -> Dict[str, Any]:
    """
    Submits attendance records for a session and manages session state.
    Enforces the Conservative Auto-Finalization Rule:
    NEVER GUESS UNMARKED STUDENTS. If unmarked students exist on finalize, flag as INCOMPLETE_RECORDS.
    """
    if session.is_cancelled:
        raise ValueError("Cannot record attendance for a cancelled lecture session.")

    state, _ = AttendanceSessionState.objects.get_or_create(session=session)

    if state.status == 'FINALIZED' and user.role == 'FACULTY':
        raise ValueError("Session is already finalized. Further edits require formal correction requests.")

    # All active enrolled students in division
    active_students = list(Student.objects.filter(division=session.division, status='ACTIVE'))
    active_student_ids = {s.id for s in active_students}

    with transaction.atomic():
        state.mode = mode

        # Record / upsert attendance marks
        marked_student_ids = set()
        for item in records_data:
            s_id = item['student_id']
            status_val = item['status'].upper()
            if status_val not in ['PRESENT', 'ABSENT']:
                status_val = 'PRESENT'

            if s_id in active_student_ids:
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student_id=s_id,
                    defaults={
                        'status': status_val,
                        'marked_by': user
                    }
                )
                marked_student_ids.add(s_id)

        # Check total recorded records for this session
        total_recorded = AttendanceRecord.objects.filter(session=session).count()
        unmarked_count = len(active_student_ids) - total_recorded

        if finalize:
            if unmarked_count > 0:
                # Conservative rule: Do NOT guess unrecorded students!
                state.status = 'INCOMPLETE_RECORDS'
                state.save(update_fields=['status', 'mode', 'updated_at'])
                return {
                    'success': False,
                    'code': 'INCOMPLETE_RECORDS',
                    'message': f"Cannot finalize session: {unmarked_count} student(s) remain unmarked. System will not guess attendance.",
                    'unmarked_count': unmarked_count,
                    'recorded_count': total_recorded
                }
            else:
                state.status = 'FINALIZED'
                state.finalized_by = user
                state.finalized_at = timezone.now()
                state.save()

                # Mark session conducted
                session.status = 'CONDUCTED'
                session.save(update_fields=['status', 'updated_at'])

                # Evaluate threshold warnings for any student dropping below 75%
                from apps.notifications.services import evaluate_threshold_for_division
                evaluate_threshold_for_division(session.division, session.subject)
        else:
            state.status = 'DRAFT'
            state.save(update_fields=['status', 'mode', 'updated_at'])

    return {
        'success': True,
        'state': state.status,
        'total_marked': total_recorded,
        'unmarked_count': max(0, unmarked_count)
    }

def calculate_student_attendance(student: Student, subject_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Server-authoritative attendance percentage calculation.
    Statutory rule: exactly 75.00% is compliant; < 75.00% is deficient.
    Cancelled sessions are excluded from both numerator and denominator.
    """
    division = student.division

    # Sessions conducted for this division
    base_sessions = LectureSession.objects.filter(
        division=division,
        status='CONDUCTED'
    )
    if subject_id:
        base_sessions = base_sessions.filter(subject_id=subject_id)

    total_conducted = base_sessions.count()

    # Attendance records where student was present
    records_qs = AttendanceRecord.objects.filter(
        student=student,
        session__in=base_sessions
    )
    attended_count = records_qs.filter(status='PRESENT').count()

    # Theory breakdown
    theory_sessions = base_sessions.filter(session_type='THEORY')
    theory_conducted = theory_sessions.count()
    theory_attended = records_qs.filter(session__session_type='THEORY', status='PRESENT').count()
    theory_percentage = round((theory_attended / theory_conducted) * 100, 2) if theory_conducted > 0 else 100.00

    # Lab breakdown
    lab_sessions = base_sessions.filter(session_type='LAB')
    lab_conducted = lab_sessions.count()
    lab_attended = records_qs.filter(session__session_type='LAB', status='PRESENT').count()
    lab_percentage = round((lab_attended / lab_conducted) * 100, 2) if lab_conducted > 0 else 100.00

    # Overall percentage
    overall_percentage = round((attended_count / total_conducted) * 100, 2) if total_conducted > 0 else 100.00
    is_deficient = overall_percentage < 75.00

    return {
        'student_id': student.id,
        'roll_number': student.roll_number,
        'classroom_display': student.classroom_display,
        'full_name': student.full_name,
        'official_email': student.official_email,
        'total_conducted': total_conducted,
        'total_attended': attended_count,
        'total_absent': total_conducted - attended_count,
        'overall_percentage': overall_percentage,
        'theory_conducted': theory_conducted,
        'theory_attended': theory_attended,
        'theory_percentage': theory_percentage,
        'lab_conducted': lab_conducted,
        'lab_attended': lab_attended,
        'lab_percentage': lab_percentage,
        'is_deficient': is_deficient,
        'statutory_threshold': 75.00
    }
