from rest_framework import viewsets
from apps.common.permissions import IsHODOrAdminRole
from .models import AuditEntry
from .serializers import AuditEntrySerializer

class AuditEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditEntry.objects.all().select_related('actor')
    serializer_class = AuditEntrySerializer
    permission_classes = [IsHODOrAdminRole]
    filterset_fields = ['action_type', 'entity_name', 'actor']
    search_fields = ['reason', 'entity_id']
