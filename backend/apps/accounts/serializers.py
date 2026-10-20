from rest_framework import serializers
from .models import User

class DepartmentBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)

class UserSerializer(serializers.ModelSerializer):
    department_details = DepartmentBriefSerializer(source='department', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'department', 'department_details', 'phone_number', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
