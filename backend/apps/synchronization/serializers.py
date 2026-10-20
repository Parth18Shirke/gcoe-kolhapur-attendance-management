import uuid
from rest_framework import serializers
from apps.attendance.serializers import AttendanceRecordItemSerializer

class OfflineSyncPayloadSerializer(serializers.Serializer):
    idempotency_key = serializers.UUIDField(default=uuid.uuid4)
    session_id = serializers.IntegerField()
    records = AttendanceRecordItemSerializer(many=True)
    mode = serializers.ChoiceField(
        choices=['MODE_1_ALL_PRESENT', 'MODE_2_ALL_ABSENT'],
        default='MODE_1_ALL_PRESENT'
    )
    structured_topic = serializers.CharField(required=False, allow_blank=True, default="")
    free_text_notes = serializers.CharField(required=False, allow_blank=True, default="")
    finalize = serializers.BooleanField(default=True)
    client_timestamp = serializers.DateTimeField(required=False)
