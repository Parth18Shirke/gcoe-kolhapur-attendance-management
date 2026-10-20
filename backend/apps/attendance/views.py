from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from apps.timetable.models import LectureSession, LectureTopic
from apps.students.models import Student
from .models import AttendanceRecord, AttendanceSessionState
from .serializers import (
    SubmitAttendanceSerializer, AttendanceRecordDetailSerializer,
    AttendanceCalculationSerializer
)
from .services import record_roster_attendance, calculate_student_attendance

class SessionRosterView(APIView):
    """
    Returns the student roster for a session's division, along with any existing marks and topic logs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = LectureSession.objects.select_related(
                'division', 'subject', 'faculty', 'room'
            ).get(id=session_id)
        except LectureSession.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Lecture session not found.'}}, status=status.HTTP_404_NOT_FOUND)

        # Faculty can view their assigned sessions; HOD/Admin can view all
        if request.user.role == 'FACULTY' and session.faculty != request.user:
            return Response({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': 'You are not assigned to this session.'}}, status=status.HTTP_403_FORBIDDEN)

        state, _ = AttendanceSessionState.objects.get_or_create(session=session)
        students = Student.objects.filter(division=session.division, status='ACTIVE').order_by('roll_number')

        existing_marks = {
            r.student_id: r.status
            for r in AttendanceRecord.objects.filter(session=session)
        }

        roster = []
        for s in students:
            roster.append({
                'student_id': s.id,
                'roll_number': s.roll_number,
                'classroom_display': s.classroom_display,
                'last_4_prn': s.last_4_prn,
                'full_name': s.full_name,
                'status': existing_marks.get(s.id, 'PRESENT' if state.mode == 'MODE_1_ALL_PRESENT' else 'ABSENT'),
                'is_recorded': s.id in existing_marks
            })

        topic_data = {}
        if hasattr(session, 'topic_log'):
            topic_data = {
                'structured_topic': session.topic_log.structured_topic,
                'free_text_notes': session.topic_log.free_text_notes,
            }

        return Response({
            'success': True,
            'session': {
                'id': session.id,
                'session_date': session.session_date,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'subject_code': session.subject.code,
                'subject_name': session.subject.name,
                'division_name': session.division.name,
                'faculty_name': session.faculty.full_name,
                'room_name': session.room.name,
                'session_type': session.session_type,
                'status': session.status,
                'state': state.status,
                'mode': state.mode,
                'topic': topic_data
            },
            'total_students': len(roster),
            'roster': roster
        })

class SubmitSessionAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SubmitAttendanceSerializer, responses={200: dict, 400: dict})
    def post(self, request, session_id):
        try:
            session = LectureSession.objects.select_related('division', 'faculty').get(id=session_id)
        except LectureSession.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Lecture session not found.'}}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'FACULTY' and session.faculty != request.user:
            return Response({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': 'You are not authorized to mark attendance for this session.'}}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmitAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update topic log if provided
        structured_topic = data.get('structured_topic', '').strip()
        free_text = data.get('free_text_notes', '').strip()
        if structured_topic or free_text:
            LectureTopic.objects.update_or_create(
                session=session,
                defaults={
                    'structured_topic': structured_topic,
                    'free_text_notes': free_text
                }
            )

        try:
            res = record_roster_attendance(
                session=session,
                records_data=data['records'],
                user=request.user,
                mode=data.get('mode', 'MODE_1_ALL_PRESENT'),
                finalize=data.get('finalize', False)
            )
            return Response(res, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}
            }, status=status.HTTP_400_BAD_REQUEST)

class StudentAttendanceMetricView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: AttendanceCalculationSerializer})
    def get(self, request, student_id):
        try:
            student = Student.objects.select_related('division').get(id=student_id)
        except Student.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Student not found.'}}, status=status.HTTP_404_NOT_FOUND)

        subject_id = request.query_params.get('subject_id')
        metrics = calculate_student_attendance(student, subject_id=int(subject_id) if subject_id else None)
        return Response({'success': True, 'metrics': metrics})

class DivisionAttendanceSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, division_id):
        subject_id = request.query_params.get('subject_id')
        sub_id = int(subject_id) if subject_id else None

        students = Student.objects.filter(division_id=division_id, status='ACTIVE').order_by('roll_number')
        summaries = [
            calculate_student_attendance(s, subject_id=sub_id)
            for s in students
        ]
        deficient_count = sum(1 for m in summaries if m['is_deficient'])

        return Response({
            'success': True,
            'division_id': division_id,
            'subject_id': sub_id,
            'total_students': len(summaries),
            'deficient_students_count': deficient_count,
            'students': summaries
        })
