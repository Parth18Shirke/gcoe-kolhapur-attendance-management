from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsHODOrAdminRole, IsAdminRole
from .models import NotificationOutbox, NotificationState
from .serializers import NotificationOutboxSerializer, NotificationStateSerializer
from .services import process_outbox_queue

class NotificationOutboxViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationOutbox.objects.all().select_related('student')
    serializer_class = NotificationOutboxSerializer
    permission_classes = [IsHODOrAdminRole]
    filterset_fields = ['status', 'notification_type', 'recipient_email']

class ProcessOutboxView(APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(responses={200: dict})
    def post(self, request):
        count = process_outbox_queue(batch_size=50)
        return Response({
            'success': True,
            'message': f"Dispatched {count} notification(s).",
            'dispatched_count': count
        }, status=status.HTTP_200_OK)

class NotificationStateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationState.objects.all().select_related('student', 'subject')
    serializer_class = NotificationStateSerializer
    permission_classes = [IsHODOrAdminRole]
    filterset_fields = ['is_currently_deficient', 'subject', 'student']
