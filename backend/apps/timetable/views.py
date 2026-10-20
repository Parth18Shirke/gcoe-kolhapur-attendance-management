from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsHODOrAdminRole, IsFacultyOrHODOrAdminRole
from .models import TimetableSlot, LectureSession, LectureTopic
from .serializers import (
    TimetableSlotSerializer, LectureSessionSerializer,
    CancelSessionSerializer, RescheduleSessionSerializer, LectureTopicSerializer
)
from .services import find_timetable_conflicts, cancel_lecture_session, reschedule_lecture_session

class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all().select_related(
        'division', 'subject', 'faculty', 'room', 'academic_year'
    )
    serializer_class = TimetableSlotSerializer
    filterset_fields = ['division', 'subject', 'faculty', 'room', 'day_of_week', 'is_active']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHODOrAdminRole()]
        return [permissions.IsAuthenticated()]

class LectureSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LectureSessionSerializer
    filterset_fields = ['division', 'subject', 'faculty', 'room', 'session_date', 'status', 'session_type']
    search_fields = ['subject__name', 'subject__code', 'faculty__full_name']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        qs = LectureSession.objects.all().select_related(
            'division', 'subject', 'faculty', 'room', 'topic_log'
        )
        if user and getattr(user, 'role', None) == 'FACULTY':
            return qs.filter(faculty=user)
        return qs

    def get_permissions(self):
        return [IsFacultyOrHODOrAdminRole()]

    @extend_schema(request=CancelSessionSerializer, responses={200: dict, 400: dict, 403: dict})
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        session = self.get_object()
        user = request.user

        # Faculty can cancel their own sessions; HOD/Admin can cancel any
        if user.role == 'FACULTY' and session.faculty != user:
            return Response({
                'success': False,
                'error': {'code': 'PERMISSION_DENIED', 'message': 'Faculty can only cancel their own sessions.'}
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CancelSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data['reason']

        cancelled_session = cancel_lecture_session(session, user, reason)
        return Response({
            'success': True,
            'message': 'Lecture session cancelled successfully.',
            'session': LectureSessionSerializer(cancelled_session).data
        })

    @extend_schema(request=RescheduleSessionSerializer, responses={200: dict, 409: dict})
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        session = self.get_object()
        user = request.user

        if user.role == 'FACULTY' and session.faculty != user:
            return Response({
                'success': False,
                'error': {'code': 'PERMISSION_DENIED', 'message': 'Faculty can only reschedule their own sessions.'}
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = RescheduleSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Check for scheduling collisions
        conflicts = find_timetable_conflicts(
            session_date=data['new_date'],
            start_time=data['new_start_time'],
            end_time=data['new_end_time'],
            faculty_id=session.faculty_id,
            division_id=session.division_id,
            room_id=data.get('new_room_id') or session.room_id,
            exclude_session_id=session.id
        )

        override = data.get('override_conflicts', False)
        if conflicts and not (override and (user.role in ['HOD', 'ADMIN'] or user.is_superuser)):
            return Response({
                'success': False,
                'error': {
                    'code': 'TIMETABLE_CONFLICT',
                    'message': 'Cannot reschedule due to scheduling collisions.',
                    'conflicts': conflicts
                }
            }, status=status.HTTP_409_CONFLICT)

        new_session = reschedule_lecture_session(
            original_session=session,
            new_date=data['new_date'],
            new_start_time=data['new_start_time'],
            new_end_time=data['new_end_time'],
            user=user,
            new_room_id=data.get('new_room_id'),
            reason=data.get('reason', '')
        )

        return Response({
            'success': True,
            'message': 'Lecture session rescheduled successfully.',
            'new_session': LectureSessionSerializer(new_session).data
        })

    @extend_schema(request=LectureTopicSerializer, responses={200: dict})
    @action(detail=True, methods=['post'])
    def topic(self, request, pk=None):
        session = self.get_object()
        user = request.user

        if user.role == 'FACULTY' and session.faculty != user:
            return Response({
                'success': False,
                'error': {'code': 'PERMISSION_DENIED', 'message': 'Faculty can only update topics for their own sessions.'}
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = LectureTopicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topic_log, _ = LectureTopic.objects.update_or_create(
            session=session,
            defaults=serializer.validated_data
        )

        return Response({
            'success': True,
            'topic_log': LectureTopicSerializer(topic_log).data
        })
