from django.contrib import admin
from .models import CitizenValidationTrace


@admin.register(CitizenValidationTrace)
class CitizenValidationTraceAdmin(admin.ModelAdmin):
    """Admin for validation communication traces."""
    
    list_display = ['citizen_id', 'status', 'requested_at', 'external_api_status_code']
    list_filter = ['status', 'requested_at']
    search_fields = ['citizen_id']
    readonly_fields = ['citizen_id', 'status', 'requested_at', 
                      'external_api_status_code', 'error_message']
    ordering = ['-requested_at']
