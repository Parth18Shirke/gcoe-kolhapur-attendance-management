from django.contrib import admin
from .models import AuditEntry

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'action_type', 'entity_name', 'entity_id', 'actor', 'created_at']
    list_filter = ['action_type', 'entity_name', 'created_at']
    search_fields = ['reason', 'entity_id']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
