from django.contrib import admin
from .models import CitizenRegistrationTrace


@admin.register(CitizenRegistrationTrace)
class CitizenRegistrationTraceAdmin(admin.ModelAdmin):
    """Admin for registration communication traces."""
    
    list_display = ['id_citizen', 'status', 'received_at', 'sent_at', 'external_api_status_code']
    list_filter = ['status', 'received_at']
    search_fields = ['id_citizen', 'message_id']
    readonly_fields = ['message_id', 'id_citizen', 'status', 'received_at', 'sent_at',
                      'external_api_status_code', 'external_api_response', 'error_message']
    ordering = ['-received_at']
