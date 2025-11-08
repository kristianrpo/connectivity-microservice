from django.contrib import admin
from .models import DocumentAuthenticationTrace


@admin.register(DocumentAuthenticationTrace)
class DocumentAuthenticationTraceAdmin(admin.ModelAdmin):
    """Admin for document authentication communication traces."""
    
    list_display = ['document_id', 'id_citizen', 'document_title', 'status', 'authenticated', 
                   'received_at', 'authenticated_at']
    list_filter = ['status', 'authenticated', 'received_at']
    search_fields = ['message_id', 'document_id', 'id_citizen', 'document_title']
    readonly_fields = ['message_id', 'document_id', 'id_citizen', 'document_title', 
                      'status', 'authenticated', 'message', 'received_at', 'authenticated_at', 
                      'event_published_at', 'external_api_status_code']
    ordering = ['-received_at']
