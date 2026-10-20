from typing import Optional, Dict, Any
from .models import AuditEntry

def log_audit_entry(
    actor,
    action_type: str,
    entity_name: str,
    entity_id: Any,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    reason: str = "",
    client_ip: str = ""
) -> AuditEntry:
    """
    Appends an immutable audit entry to the institutional event trail.
    """
    return AuditEntry.objects.create(
        actor=actor,
        action_type=action_type,
        entity_name=entity_name,
        entity_id=str(entity_id),
        old_values=old_values or {},
        new_values=new_values or {},
        reason=reason or "",
        client_ip=client_ip or ""
    )
