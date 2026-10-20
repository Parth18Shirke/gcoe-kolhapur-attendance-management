from rest_framework import viewsets, permissions
from apps.common.permissions import IsHODOrAdminRole
from .models import FacultyAssignment
from .serializers import FacultyAssignmentSerializer

class FacultyAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = FacultyAssignmentSerializer
    filterset_fields = ['faculty', 'subject', 'division', 'academic_year', 'is_primary']

    def get_queryset(self):
        user = self.request.user
        qs = FacultyAssignment.objects.all().select_related(
            'faculty', 'subject', 'division', 'academic_year'
        )
        if user.role == 'FACULTY':
            # Faculty can view their own assignments
            return qs.filter(faculty=user)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHODOrAdminRole()]
        return [permissions.IsAuthenticated()]
