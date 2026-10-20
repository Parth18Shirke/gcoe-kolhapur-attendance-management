from rest_framework import serializers
from .models import AuditEntry

class AuditEntrySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.full_name', read_only=True)
    actor_email = serializers.CharField(source='actor.email', read_only=True)

    class Meta:
        model = AuditEntry
        fields = '__all__'
