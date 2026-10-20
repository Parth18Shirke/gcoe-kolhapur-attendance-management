from rest_framework import serializers
from .models import Department, Program, AcademicYear, Semester, Division, Subject

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Program
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = Semester
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    semester_info = serializers.CharField(source='semester.__str__', read_only=True)

    class Meta:
        model = Division
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    semester_info = serializers.CharField(source='semester.__str__', read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'
