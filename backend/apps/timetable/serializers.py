from rest_framework import serializers
from .models import TimetableSlot, LectureSession, LectureTopic

class LectureTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureTopic
        fields = ['id', 'structured_topic', 'free_text_notes', 'created_at', 'updated_at']

class TimetableSlotSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = TimetableSlot
        fields = '__all__'

class LectureSessionSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    topic_log = LectureTopicSerializer(read_only=True)
    session_state = serializers.SerializerMethodField()

    class Meta:
        model = LectureSession
        fields = '__all__'

    def get_session_state(self, obj):
        if hasattr(obj, 'lifecycle_state'):
            return obj.lifecycle_state.status
        return 'DRAFT'

class CancelSessionSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=3, max_length=500)

class RescheduleSessionSerializer(serializers.Serializer):
    new_date = serializers.DateField()
    new_start_time = serializers.TimeField()
    new_end_time = serializers.TimeField()
    new_room_id = serializers.IntegerField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="")
    override_conflicts = serializers.BooleanField(required=False, default=False)
