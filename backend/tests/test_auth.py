import pytest
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import EmailOTP, UserToken, OTPRateLimit

@pytest.mark.django_db
def test_otp_request_and_verify_success(api_client, faculty_user):
    # 1. Request OTP
    resp = api_client.post('/api/v1/auth/otp/request/', {'email': faculty_user.email})
    assert resp.status_code == 200
    assert resp.data['success'] is True

    otp_obj = EmailOTP.objects.filter(user=faculty_user, is_used=False).first()
    assert otp_obj is not None
    assert otp_obj.attempts_remaining == 3

    # Generate a known OTP
    known_otp = EmailOTP.create_for_user(faculty_user)

    # 2. Verify OTP
    verify_resp = api_client.post('/api/v1/auth/otp/verify/', {
        'email': faculty_user.email,
        'otp': known_otp
    })
    assert verify_resp.status_code == 200
    assert verify_resp.data['success'] is True
    assert 'token' in verify_resp.data
    assert verify_resp.data['user']['email'] == faculty_user.email
    assert verify_resp.data['user']['role'] == 'FACULTY'

@pytest.mark.django_db
def test_otp_single_use(api_client, faculty_user):
    known_otp = EmailOTP.create_for_user(faculty_user)

    # First verify: success
    resp1 = api_client.post('/api/v1/auth/otp/verify/', {'email': faculty_user.email, 'otp': known_otp})
    assert resp1.status_code == 200

    # Second verify: must fail (single-use invariant)
    resp2 = api_client.post('/api/v1/auth/otp/verify/', {'email': faculty_user.email, 'otp': known_otp})
    assert resp2.status_code == 401
    assert resp2.data['success'] is False

@pytest.mark.django_db
def test_otp_brute_force_lockout(api_client, faculty_user):
    EmailOTP.create_for_user(faculty_user)

    # 3 invalid attempts
    for _ in range(3):
        resp = api_client.post('/api/v1/auth/otp/verify/', {'email': faculty_user.email, 'otp': '000000'})
        assert resp.status_code == 401

    # OTP should now be marked is_used / locked
    otp_obj = EmailOTP.objects.filter(user=faculty_user).order_by('-created_at').first()
    assert otp_obj.is_used is True
    assert otp_obj.attempts_remaining == 0

@pytest.mark.django_db
def test_otp_expired_fails(api_client, faculty_user):
    known_otp = EmailOTP.create_for_user(faculty_user)
    otp_obj = EmailOTP.objects.filter(user=faculty_user).order_by('-created_at').first()
    otp_obj.expires_at = timezone.now() - timedelta(minutes=1)
    otp_obj.save()

    resp = api_client.post('/api/v1/auth/otp/verify/', {'email': faculty_user.email, 'otp': known_otp})
    assert resp.status_code == 401

@pytest.mark.django_db
def test_otp_rate_limiting(api_client, faculty_user):
    for i in range(3):
        resp = api_client.post('/api/v1/auth/otp/request/', {'email': faculty_user.email})
        assert resp.status_code == 200

    # 4th request within 15 mins should be rejected
    blocked_resp = api_client.post('/api/v1/auth/otp/request/', {'email': faculty_user.email})
    assert blocked_resp.status_code == 400
    assert 'Too many OTP requests' in blocked_resp.data['error']['message']

@pytest.mark.django_db
def test_logout_revokes_token(auth_client_faculty, faculty_token):
    assert UserToken.objects.filter(key=faculty_token.key).exists()
    resp = auth_client_faculty.post('/api/v1/auth/logout/')
    assert resp.status_code == 200
    assert not UserToken.objects.filter(key=faculty_token.key).exists()
