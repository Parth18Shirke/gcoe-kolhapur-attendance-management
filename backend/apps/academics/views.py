from rest_framework import viewsets, permissions
from apps.common.permissions import IsHODOrAdminRole, IsAdminRole
from .models import Department, Program, AcademicYear, Semester, Division, Subject
from .serializers import (
    DepartmentSerializer, ProgramSerializer, AcademicYearSerializer,
    SemesterSerializer, DivisionSerializer, SubjectSerializer
)

class BaseAcademicViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHODOrAdminRole()]
        return [permissions.IsAuthenticated()]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

class ProgramViewSet(BaseAcademicViewSet):
    queryset = Program.objects.all().select_related('department')
    serializer_class = ProgramSerializer
    filterset_fields = ['department', 'is_active']

class AcademicYearViewSet(BaseAcademicViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer

class SemesterViewSet(BaseAcademicViewSet):
    queryset = Semester.objects.all().select_related('program', 'academic_year')
    serializer_class = SemesterSerializer
    filterset_fields = ['program', 'academic_year', 'term_type', 'is_current']

class DivisionViewSet(BaseAcademicViewSet):
    queryset = Division.objects.all().select_related('semester')
    serializer_class = DivisionSerializer
    filterset_fields = ['semester']

class SubjectViewSet(BaseAcademicViewSet):
    queryset = Subject.objects.all().select_related('department', 'semester')
    serializer_class = SubjectSerializer
    filterset_fields = ['department', 'semester', 'subject_type', 'is_active']
    search_fields = ['name', 'code']
