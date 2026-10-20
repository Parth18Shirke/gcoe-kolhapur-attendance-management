from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from .serializers import OfflineSyncPayloadSerializer
from .services import process_offline_sync, SyncConflictError

class OfflineSyncAttendanceView(APIView):
    """
    Ingests attendance submissions from offline clients.
    Guarantees idempotency via `idempotency_key` and rejects submissions conflicting with server state.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=OfflineSyncPayloadSerializer, responses={200: dict, 409: dict, 400: dict})
    def post(self, request):
        serializer = OfflineSyncPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = process_offline_sync(
                idempotency_key=data['idempotency_key'],
                session_id=data['session_id'],
                records=data['records'],
                user=request.user,
                structured_topic=data.get('structured_topic', ''),
                free_text_notes=data.get('free_text_notes', ''),
                mode=data.get('mode', 'MODE_1_ALL_PRESENT'),
                finalize=data.get('finalize', True)
            )
            return Response(result, status=status.HTTP_200_OK)
        except SyncConflictError as sce:
            return Response({
                'success': False,
                'error': {
                    'code': 'SYNC_CONFLICT',
                    'message': str(sce),
                    'details': sce.details
                }
            }, status=status.HTTP_409_CONFLICT)
        except PermissionError as pe:
            return Response({
                'success': False,
                'error': {'code': 'PERMISSION_DENIED', 'message': str(pe)}
            }, status=status.HTTP_403_FORBIDDEN)
        except ValueError as ve:
            return Response({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}
            }, status=status.HTTP_400_BAD_REQUEST)
