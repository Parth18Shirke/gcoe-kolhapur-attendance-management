from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsAdminRole
from .models import User, UserToken
from .serializers import UserSerializer, OTPRequestSerializer, OTPVerifySerializer
from .services import get_auth_provider

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=OTPRequestSerializer, responses={200: dict, 400: dict})
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        client_ip = get_client_ip(request)

        provider = get_auth_provider()
        success, message = provider.request_challenge(email, client_ip)

        if success:
            return Response({
                'success': True,
                'message': message,
                'expires_in_seconds': 600
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'OTP_REQUEST_FAILED',
                    'message': message
                }
            }, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=OTPVerifySerializer, responses={200: dict, 401: dict})
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        provider = get_auth_provider()
        success, user, token_or_err = provider.verify_challenge(email, otp)

        if success and user:
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'token': token_or_err,
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'OTP_VERIFICATION_FAILED',
                    'message': token_or_err or 'Invalid OTP challenge.'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response({
            'success': True,
            'user': UserSerializer(request.user).data
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request, 'auth') and isinstance(request.auth, UserToken):
            request.auth.delete()
        return Response({'success': True, 'message': 'Logged out successfully.'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('department')
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['full_name', 'email']
