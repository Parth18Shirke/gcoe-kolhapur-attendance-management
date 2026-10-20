from typing import List, Dict, Any, Optional
from datetime import date, time
from django.utils import timezone
from django.db import transaction
from .models import LectureSession

def find_timetable_conflicts(
    session_date: date,
    start_time: time,
    end_time: time,
    faculty_id: int,
    division_id: int,
    room_id: int,
    exclude_session_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Detects scheduling collisions across Faculty, Division, and Room dimensions.
    Returns a list of conflict descriptors.
    """
    conflicts = []

    # Overlapping condition: (StartA < EndB) and (EndA > StartB)
    qs = LectureSession.objects.filter(
        session_date=session_date,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exclude(status='CANCELLED')

    if exclude_session_id:
        qs = qs.exclude(id=exclude_session_id)

    # 1. Faculty Conflict
    faculty_overlap = qs.filter(faculty_id=faculty_id).select_related('subject', 'division', 'room').first()
    if faculty_overlap:
        conflicts.append({
            'type': 'FACULTY_CONFLICT',
            'message': f"Faculty is already assigned to {faculty_overlap.subject.code} for {faculty_overlap.division.name} ({faculty_overlap.start_time.strftime('%H:%M')}-{faculty_overlap.end_time.strftime('%H:%M')})",
            'conflicting_session_id': faculty_overlap.id
        })

    # 2. Division Conflict
    div_overlap = qs.filter(division_id=division_id).select_related('subject', 'faculty', 'room').first()
    if div_overlap:
        conflicts.append({
            'type': 'DIVISION_CONFLICT',
            'message': f"Division {div_overlap.division.name} is already scheduled for {div_overlap.subject.code} with {div_overlap.faculty.full_name} ({div_overlap.start_time.strftime('%H:%M')}-{div_overlap.end_time.strftime('%H:%M')})",
            'conflicting_session_id': div_overlap.id
        })

    # 3. Room Conflict
    room_overlap = qs.filter(room_id=room_id).select_related('subject', 'division', 'faculty', 'room').first()
    if room_overlap:
        conflicts.append({
            'type': 'ROOM_CONFLICT',
            'message': f"Room {room_overlap.room.name} is already booked for {room_overlap.subject.code} ({room_overlap.start_time.strftime('%H:%M')}-{room_overlap.end_time.strftime('%H:%M')})",
            'conflicting_session_id': room_overlap.id
        })

    return conflicts

def cancel_lecture_session(session: LectureSession, user, reason: str) -> LectureSession:
    """
    Cancels a lecture session with mandatory reason and historical actor tracking.
    Never physically deletes the session.
    """
    if not reason.strip():
        raise ValueError("A clear, non-empty cancellation reason is mandatory.")

    session.status = 'CANCELLED'
    session.cancellation_reason = reason.strip()
    session.cancelled_by = user
    session.cancelled_at = timezone.now()
    session.save(update_fields=['status', 'cancellation_reason', 'cancelled_by', 'cancelled_at', 'updated_at'])
    return session

def reschedule_lecture_session(
    original_session: LectureSession,
    new_date: date,
    new_start_time: time,
    new_end_time: time,
    user,
    new_room_id: Optional[int] = None,
    reason: str = ""
) -> LectureSession:
    """
    Reschedules a session by preserving the original session in history
    and creating a linked new scheduled session occurrence.
    """
    with transaction.atomic():
        room_id = new_room_id or original_session.room_id

        # Cancel original with rescheduling reason
        resched_note = f"Rescheduled to {new_date} ({new_start_time.strftime('%H:%M')}-{new_end_time.strftime('%H:%M')}). Reason: {reason or 'Schedule adjustment'}"
        cancel_lecture_session(original_session, user, resched_note)

        # Compute duration
        duration = 60
        try:
            start_dt = timezone.datetime.combine(new_date, new_start_time)
            end_dt = timezone.datetime.combine(new_date, new_end_time)
            duration = int((end_dt - start_dt).total_seconds() / 60)
        except Exception:
            pass

        # Create new occurrence with link
        new_session = LectureSession.objects.create(
            slot=original_session.slot,
            division=original_session.division,
            subject=original_session.subject,
            faculty=original_session.faculty,
            room_id=room_id,
            session_date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            duration_minutes=duration,
            session_type=original_session.session_type,
            status='SCHEDULED',
            rescheduled_from=original_session
        )
        return new_session
