"""
Traceability models for external API communications.

CORE FUNCTIONALITY #2: Track registration requests to external centralizer.
"""

from django.db import models
from django.utils import timezone


class CitizenRegistrationTrace(models.Model):
    """
    Traceability for citizen registration requests to external centralizer.
    
    This microservice does NOT register citizens, it only forwards the request
    to the external centralizer and tracks the communication.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent to Centralizer'),
        ('FAILED', 'Failed'),
        ('ERROR', 'Error'),
    ]
    
    # Event tracking (idempotency)
    message_id = models.UUIDField(unique=True, db_index=True)
    
    # Minimal citizen info (only for traceability)
    id_citizen = models.BigIntegerField(db_index=True)
    
    # Communication status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # External API communication trace
    external_api_status_code = models.IntegerField(null=True, blank=True)
    external_api_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'citizen_registration_traces'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['id_citizen', '-received_at']),
        ]
        verbose_name = 'Registration Trace'
        verbose_name_plural = 'Registration Traces'
    
    def __str__(self):
        return f"Trace - Citizen {self.id_citizen} - {self.status}"
    
    def mark_as_sent(self, status_code: int, response_data: dict = None):
        """Mark as successfully sent to centralizer."""
        self.status = 'SENT'
        self.external_api_status_code = status_code
        self.external_api_response = response_data
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_error(self, error_message: str):
        """Mark as error."""
        self.status = 'ERROR'
        self.error_message = error_message
        self.sent_at = timezone.now()
        self.save()
