import logging
import smtplib
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from apps.academics.models import Division, Subject
from apps.students.models import Student
from .models import NotificationState, NotificationOutbox

logger = logging.getLogger(__name__)

class BaseEmailProvider(ABC):
    @abstractmethod
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        pass

class ConsoleEmailProvider(BaseEmailProvider):
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        logger.info("[Console Email] TO: %s | SUBJECT: %s\n%s", to_email, subject, body)
        return True

class SMTPEmailProvider(BaseEmailProvider):
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'ams-alerts@college.edu')
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error("SMTP delivery failed for %s: %s", to_email, str(e))
            raise e

_email_service: Optional[BaseEmailProvider] = None

def get_email_service() -> BaseEmailProvider:
    global _email_service
    if _email_service is None:
        provider_name = getattr(settings, 'EMAIL_PROVIDER', 'console').lower()
        if provider_name == 'smtp':
            _email_service = SMTPEmailProvider()
        else:
            _email_service = ConsoleEmailProvider()
    return _email_service

def evaluate_threshold_for_division(division: Division, subject: Optional[Subject] = None):
    """
    Evaluates attendance percentages against the statutory 75% threshold for all active students.
    1. Triggers immediate alert when a student drops below 75%.
    2. Enforces a 7-day cooldown before repeating reminders.
    3. Resets state cleanly when student attendance recovers >= 75.00%.
    """
    from apps.attendance.services import calculate_student_attendance

    students = Student.objects.filter(division=division, status='ACTIVE')
    threshold = getattr(settings, 'STATUTORY_ATTENDANCE_THRESHOLD', 75.00)
    cooldown_days = getattr(settings, 'NOTIFICATION_COOLDOWN_DAYS', 7)

    subjects = [subject] if subject else Subject.objects.filter(semester=division.semester, is_active=True)

    for sub in subjects:
        for st in students:
            metrics = calculate_student_attendance(st, subject_id=sub.id)
            overall_pct = metrics['overall_percentage']
            is_deficient = overall_pct < threshold

            state, _ = NotificationState.objects.get_or_create(
                student=st,
                subject=sub,
                defaults={'last_percentage': overall_pct, 'is_currently_deficient': False}
            )

            now = timezone.now()

            if is_deficient:
                should_alert = False
                subject_line = f"ATTENDANCE WARNING: {sub.code} Attendance Below 75% ({overall_pct}%)"
                body = (
                    f"Dear {st.full_name} ({st.classroom_display}),\n\n"
                    f"This is an official institutional notice from the College Attendance Cell.\n"
                    f"Your current attendance in '{sub.name} ({sub.code})' is {overall_pct}%, "
                    f"which has fallen below the statutory minimum requirement of 75.00%.\n\n"
                    f"Details:\n"
                    f"  - Lectures Conducted: {metrics['total_conducted']}\n"
                    f"  - Lectures Attended:  {metrics['total_attended']}\n"
                    f"  - Shortfall:          {metrics['total_absent']} missed lecture(s)\n\n"
                    f"Please contact your subject faculty and attend all upcoming sessions to prevent academic debarment.\n\n"
                    f"Office of Academic Affairs"
                )

                if not state.is_currently_deficient:
                    # Dropped below 75% for the first time or after recovery
                    should_alert = True
                    state.is_currently_deficient = True
                    state.first_notified_at = now
                    state.last_reminded_at = now
                    state.reminder_count = 1
                else:
                    # Already deficient, check cooldown
                    if state.last_reminded_at and (now - state.last_reminded_at) >= timedelta(days=cooldown_days):
                        should_alert = True
                        state.last_reminded_at = now
                        state.reminder_count += 1
                        subject_line = f"REPEAT ATTENDANCE WARNING #{state.reminder_count}: {sub.code} ({overall_pct}%)"

                if should_alert:
                    NotificationOutbox.objects.create(
                        recipient_email=st.official_email,
                        student=st,
                        subject_line=subject_line,
                        body_text=body,
                        notification_type='THRESHOLD_75_WARNING',
                        status='PENDING'
                    )

            else:
                # Student recovered or compliant
                if state.is_currently_deficient:
                    # State recovery: Reset deficiency flag and allow future fresh warning cycle
                    state.is_currently_deficient = False
                    state.first_notified_at = None
                    state.last_reminded_at = None
                    state.reminder_count = 0

            state.last_percentage = overall_pct
            state.save()

def process_outbox_queue(batch_size: int = 50, max_retries: int = 3) -> int:
    """
    Background worker function to dispatch pending emails from the outbox.
    Can be run via cron, Celery, or management command without Redis.
    """
    pending = NotificationOutbox.objects.filter(
        status__in=['PENDING', 'FAILED'],
        retry_count__lt=max_retries
    ).order_by('created_at')[:batch_size]

    email_service = get_email_service()
    dispatched_count = 0

    for outbox_item in pending:
        try:
            success = email_service.send_email(
                to_email=outbox_item.recipient_email,
                subject=outbox_item.subject_line,
                body=outbox_item.body_text
            )
            if success:
                outbox_item.status = 'SENT'
                outbox_item.sent_at = timezone.now()
                outbox_item.error_message = ""
                outbox_item.save(update_fields=['status', 'sent_at', 'error_message', 'updated_at'])
                dispatched_count += 1
        except Exception as e:
            outbox_item.retry_count += 1
            outbox_item.status = 'FAILED'
            outbox_item.error_message = str(e)[:500]
            outbox_item.save(update_fields=['retry_count', 'status', 'error_message', 'updated_at'])

    return dispatched_count
