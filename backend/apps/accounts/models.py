import hashlib
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from apps.common.models import TimeStampedModel

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, role='FACULTY', password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is mandatory for user accounts.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name='System Administrator', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        if not password:
            raise ValueError('Superuser requires a non-empty password.')
        return self.create_user(email, full_name, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ROLE_CHOICES = [
        ('ADMIN', 'System Administrator'),
        ('HOD', 'Head of Department'),
        ('FACULTY', 'Teaching Faculty'),
    ]

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FACULTY', db_index=True)
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role} - {self.email})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_hod(self):
        return self.role == 'HOD'

    @property
    def is_faculty(self):
        return self.role == 'FACULTY'

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_hash = models.CharField(max_length=128)
    salt = models.CharField(max_length=32)
    attempts_remaining = models.PositiveSmallIntegerField(default=3)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def create_for_user(cls, user, lifespan_minutes=10):
        # Invalidate any pending OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        # Generate cryptographically secure 6-digit number
        digits = "0123456789"
        plain_otp = "".join(secrets.choice(digits) for _ in range(6))

        salt = secrets.token_hex(16)
        salted_val = f"{salt}:{plain_otp}".encode('utf-8')
        otp_hash = hashlib.sha256(salted_val).hexdigest()

        expires_at = timezone.now() + timedelta(minutes=lifespan_minutes)

        cls.objects.create(
            user=user,
            otp_hash=otp_hash,
            salt=salt,
            attempts_remaining=3,
            is_used=False,
            expires_at=expires_at
        )
        return plain_otp

    def verify(self, candidate_otp: str) -> bool:
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return False
        if self.attempts_remaining <= 0:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return False

        salted_val = f"{self.salt}:{candidate_otp}".encode('utf-8')
        candidate_hash = hashlib.sha256(salted_val).hexdigest()

        if secrets.compare_digest(self.otp_hash, candidate_hash):
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        else:
            self.attempts_remaining -= 1
            if self.attempts_remaining == 0:
                self.is_used = True
            self.save(update_fields=['attempts_remaining', 'is_used'])
            return False

class UserToken(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    @classmethod
    def generate(cls, user, lifespan_days=30):
        key = secrets.token_hex(32)
        expires_at = timezone.now() + timedelta(days=lifespan_days)
        return cls.objects.create(key=key, user=user, expires_at=expires_at)

    def is_valid(self):
        return timezone.now() < self.expires_at

class OTPRateLimit(models.Model):
    identifier = models.CharField(max_length=255, db_index=True)
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def check_and_record(cls, identifier: str, limit: int = 3, window_minutes: int = 15) -> bool:
        """
        Returns True if under rate limit and records request; returns False if rate limit exceeded.
        """
        cutoff = timezone.now() - timedelta(minutes=window_minutes)
        # Clean older records
        cls.objects.filter(identifier=identifier, requested_at__lt=cutoff).delete()
        count = cls.objects.filter(identifier=identifier, requested_at__gte=cutoff).count()
        if count >= limit:
            return False
        cls.objects.create(identifier=identifier)
        return True
