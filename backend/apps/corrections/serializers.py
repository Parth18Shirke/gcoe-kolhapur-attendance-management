from rest_framework import serializers
from .models import CorrectionRequest

class SubmitCorrectionSerializer(serializers.Serializer):
    attendance_record_id = serializers.IntegerField()
    new_status = serializers.ChoiceField(choices=['PRESENT', 'ABSENT'])
    reason = serializers.CharField(min_length=3, max_length=500)

class ReviewCorrectionSerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    remarks = serializers.CharField(required=False, allow_blank=True, default="")

class CorrectionRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.full_name', read_only=True)
    student_display = serializers.CharField(source='attendance_record.student.classroom_display', read_only=True)
    student_roll = serializers.CharField(source='attendance_record.student.roll_number', read_only=True)
    session_info = serializers.CharField(source='attendance_record.session.__str__', read_only=True)

    class Meta:
        model = CorrectionRequest
        fields = '__all__'
