import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User, EmailOTP, UserToken, OTPRateLimit
from apps.notifications.services import get_email_service

logger = logging.getLogger(__name__)

class BaseAuthProvider(ABC):
    @abstractmethod
    def request_challenge(self, identifier: str, client_ip: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def verify_challenge(self, identifier: str, challenge: str) -> Tuple[bool, Optional[User], Optional[str]]:
        pass

class EmailOTPAuthProvider(BaseAuthProvider):
    def request_challenge(self, identifier: str, client_ip: str) -> Tuple[bool, str]:
        email = identifier.strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            return False, "Invalid email address format."

        # Check rate limiting per email and per client IP
        if not OTPRateLimit.check_and_record(email, limit=3, window_minutes=15):
            return False, "Too many OTP requests for this email. Please wait 15 minutes."
        if client_ip and not OTPRateLimit.check_and_record(f"ip:{client_ip}", limit=10, window_minutes=15):
            return False, "Too many requests from your IP address. Please wait."

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # For security, do not expose whether user exists, but report success
            logger.info("OTP requested for unregistered/inactive email: %s", email)
            return True, "If this email is registered, a one-time password has been sent."

        # Generate OTP
        plain_otp = EmailOTP.create_for_user(user, lifespan_minutes=10)

        # Transmit OTP via Email Service
        email_service = get_email_service()
        subject = f"Your AMS Login Code: {plain_otp}"
        body = (
            f"Dear {user.full_name},\n\n"
            f"Your one-time authentication code for the College Attendance Management System is:\n\n"
            f"    {plain_otp}\n\n"
            f"This code is single-use and will expire in exactly 10 minutes.\n"
            f"If you did not initiate this login request, please contact the IT Administrator immediately.\n\n"
            f"College Attendance Management Cell"
        )
        email_service.send_email(to_email=user.email, subject=subject, body=body)

        return True, "One-Time Password has been transmitted to your verified institutional email."

    def verify_challenge(self, identifier: str, challenge: str) -> Tuple[bool, Optional[User], Optional[str]]:
        email = identifier.strip().lower()
        plain_otp = challenge.strip()

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return False, None, "Invalid email or authentication code."

        # Find latest active OTP
        latest_otp = EmailOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
        if not latest_otp:
            return False, None, "No active login code found. Please request a new one."

        if latest_otp.verify(plain_otp):
            token = UserToken.generate(user, lifespan_days=30)
            return True, user, token.key
        else:
            remaining = latest_otp.attempts_remaining
            if remaining > 0:
                return False, None, f"Invalid code. {remaining} attempt(s) remaining."
            else:
                return False, None, "Maximum verification attempts exceeded. Code has been invalidated."

_auth_provider: Optional[BaseAuthProvider] = None

def get_auth_provider() -> BaseAuthProvider:
    global _auth_provider
    if _auth_provider is None:
        _auth_provider = EmailOTPAuthProvider()
    return _auth_provider
