from rest_framework import serializers
from .models import Student, StudentImportLog

class ClassroomStudentSerializer(serializers.ModelSerializer):
    """
    Roster-optimized serializer protecting full PRN privacy in the classroom.
    Exposes only last-4 digits + Student Name (e.g. '1234 — Rahul Sharma').
    """
    classroom_display = serializers.CharField(read_only=True)
    last_4_prn = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'classroom_display', 'last_4_prn', 'full_name', 'division', 'status']

class AdminStudentSerializer(serializers.ModelSerializer):
    """
    Full administrative serializer exposing university PRN and full profile.
    """
    classroom_display = serializers.CharField(read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

class StudentImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    division_id = serializers.IntegerField(required=False, allow_null=True)

class StudentImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentImportLog
        fields = '__all__'
