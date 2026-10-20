from rest_framework import serializers
from .models import AttendanceRecord, AttendanceSessionState

class AttendanceRecordItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['PRESENT', 'ABSENT'])

class SubmitAttendanceSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(
        choices=['MODE_1_ALL_PRESENT', 'MODE_2_ALL_ABSENT'],
        default='MODE_1_ALL_PRESENT'
    )
    records = AttendanceRecordItemSerializer(many=True)
    finalize = serializers.BooleanField(default=False)
    structured_topic = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
    free_text_notes = serializers.CharField(required=False, allow_blank=True, default="")

class AttendanceRecordDetailSerializer(serializers.ModelSerializer):
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    student_display = serializers.CharField(source='student.classroom_display', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'session', 'student', 'student_roll', 'student_display', 'status', 'marked_by_name', 'created_at', 'updated_at']

class AttendanceCalculationSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    roll_number = serializers.CharField()
    classroom_display = serializers.CharField()
    full_name = serializers.CharField()
    total_conducted = serializers.IntegerField()
    total_attended = serializers.IntegerField()
    total_absent = serializers.IntegerField()
    overall_percentage = serializers.FloatField()
    theory_conducted = serializers.IntegerField()
    theory_attended = serializers.IntegerField()
    theory_percentage = serializers.FloatField()
    lab_conducted = serializers.IntegerField()
    lab_attended = serializers.IntegerField()
    lab_percentage = serializers.FloatField()
    is_deficient = serializers.BooleanField()
    statutory_threshold = serializers.FloatField()
