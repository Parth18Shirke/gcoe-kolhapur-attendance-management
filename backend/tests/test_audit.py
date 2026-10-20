import pytest
from django.core.exceptions import PermissionDenied
from apps.audit.models import AuditEntry
from apps.audit.services import log_audit_entry

@pytest.mark.django_db
def test_audit_entry_logging_and_immutability(admin_user):
    # 1. Log an entry
    entry = log_audit_entry(
        actor=admin_user,
        action_type='CREATE',
        entity_name='Subject',
        entity_id='101',
        new_values={'name': 'Advanced Algorithms'},
        reason='New curriculum addition'
    )
    assert entry.id is not None
    assert entry.actor == admin_user

    # 2. Immutability: Update must raise PermissionDenied
    with pytest.raises(PermissionDenied):
        entry.reason = "Modified reason"
        entry.save()

    # 3. Immutability: Delete must raise PermissionDenied
    with pytest.raises(PermissionDenied):
        entry.delete()
