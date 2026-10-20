from rest_framework import viewsets, permissions
from apps.common.permissions import IsHODOrAdminRole
from .models import Room
from .serializers import RoomSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filterset_fields = ['room_type', 'is_active', 'building']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHODOrAdminRole()]
        return [permissions.IsAuthenticated()]
