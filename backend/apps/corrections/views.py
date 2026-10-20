from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsHODOrAdminRole
from apps.attendance.models import AttendanceRecord
from .models import CorrectionRequest
from .serializers import (
    SubmitCorrectionSerializer, ReviewCorrectionSerializer,
    CorrectionRequestSerializer
)
from .services import submit_correction_request, review_correction_request

class SubmitCorrectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SubmitCorrectionSerializer, responses={200: CorrectionRequestSerializer, 400: dict})
    def post(self, request):
        serializer = SubmitCorrectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            record = AttendanceRecord.objects.select_related('session__division', 'session__subject').get(
                id=data['attendance_record_id']
            )
        except AttendanceRecord.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Attendance record not found.'}}, status=status.HTTP_404_NOT_FOUND)

        try:
            req = submit_correction_request(
                record=record,
                new_status=data['new_status'],
                reason=data['reason'],
                user=request.user
            )
            return Response({
                'success': True,
                'message': 'Correction processed.' if req.status == 'AUTO_APPLIED' else 'Correction submitted for HOD review.',
                'correction': CorrectionRequestSerializer(req).data
            }, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}}, status=status.HTTP_400_BAD_REQUEST)

class CorrectionRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CorrectionRequestSerializer
    filterset_fields = ['status', 'requested_by']

    def get_queryset(self):
        user = self.request.user
        qs = CorrectionRequest.objects.all().select_related(
            'attendance_record__student', 'attendance_record__session',
            'requested_by', 'reviewed_by'
        )
        if user.role == 'FACULTY':
            return qs.filter(requested_by=user)
        return qs

class ReviewCorrectionView(APIView):
    permission_classes = [IsHODOrAdminRole]

    @extend_schema(request=ReviewCorrectionSerializer, responses={200: CorrectionRequestSerializer, 400: dict})
    def post(self, request, pk):
        try:
            correction = CorrectionRequest.objects.select_related(
                'attendance_record__session__division', 'attendance_record__session__subject'
            ).get(id=pk)
        except CorrectionRequest.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Correction request not found.'}}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewCorrectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = review_correction_request(
                correction=correction,
                approved=serializer.validated_data['approved'],
                reviewer=request.user,
                remarks=serializer.validated_data.get('remarks', '')
            )
            return Response({
                'success': True,
                'message': f"Correction request {updated.status.lower()}.",
                'correction': CorrectionRequestSerializer(updated).data
            })
        except ValueError as ve:
            return Response({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}}, status=status.HTTP_400_BAD_REQUEST)
