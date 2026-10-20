from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsAdminRole, IsHODOrAdminRole
from .models import Student, StudentImportLog
from .serializers import (
    ClassroomStudentSerializer, AdminStudentSerializer,
    StudentImportSerializer, StudentImportLogSerializer
)
from .services import parse_student_file

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().select_related('division')
    filterset_fields = ['division', 'status']
    search_fields = ['roll_number', 'full_name', 'prn']

    def get_serializer_class(self):
        # Faculty receives privacy-protected classroom serializer (no full PRN)
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'role', None) == 'FACULTY':
            return ClassroomStudentSerializer
        return AdminStudentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

class StudentImportView(APIView):
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=StudentImportSerializer, responses={200: dict, 400: dict})
    def post(self, request):
        serializer = StudentImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_obj = serializer.validated_data['file']
        division_id = serializer.validated_data.get('division_id')

        try:
            result = parse_student_file(
                file_obj=file_obj,
                default_division_id=division_id,
                uploaded_by=request.user
            )
            return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'IMPORT_FAILED',
                    'message': f"Failed to parse student roster: {str(e)}"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

class StudentImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentImportLog.objects.all().select_related('uploaded_by')
    serializer_class = StudentImportLogSerializer
    permission_classes = [IsHODOrAdminRole]
