"""
Traceability models for external API communications.

CORE FUNCTIONALITY #3: Track document authentication requests.
"""

from django.db import models
from django.utils import timezone


class DocumentAuthenticationTrace(models.Model):
    """
    Traceability for document authentication requests to external centralizer.
    
    This microservice does NOT store documents, it only tracks:
    - Authentication requests
    - External API responses
    - Event publications
    
    IDEMPOTENCY: Uses message_id to prevent duplicate processing.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent to Centralizer'),
        ('FAILED', 'Failed'),
        ('ERROR', 'Error'),
    ]
    
    # Idempotency (from incoming event)
    message_id = models.CharField(max_length=255, unique=True, db_index=True)
    document_id = models.CharField(max_length=255, db_index=True)
    
    # Request info (minimal, only for traceability)
    id_citizen = models.BigIntegerField(db_index=True)
    document_title = models.CharField(max_length=200)
    
    # Communication status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    authenticated = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    
    # External API communication trace
    external_api_status_code = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    authenticated_at = models.DateTimeField(null=True, blank=True)
    event_published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_authentication_traces'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['id_citizen', '-received_at']),
        ]
        verbose_name = 'Authentication Trace'
        verbose_name_plural = 'Authentication Traces'
    
    def __str__(self):
        return f"Trace - Doc {self.document_id} - Citizen {self.id_citizen} - {self.status}"
    
    def mark_as_authenticated(self, status_code: int, success: bool, message: str = ''):
        """Mark as authenticated (sent to centralizer)."""
        self.status = 'SENT'
        self.authenticated = success
        self.message = message
        self.external_api_status_code = status_code
        self.authenticated_at = timezone.now()
        self.save()
    
    def mark_as_error(self, error_message: str):
        """Mark as error."""
        self.status = 'ERROR'
        self.authenticated = False
        self.message = error_message
        self.authenticated_at = timezone.now()
        self.save()
    
    def mark_event_published(self):
        """Mark result event published."""
        self.event_published_at = timezone.now()
        self.save(update_fields=['event_published_at'])
