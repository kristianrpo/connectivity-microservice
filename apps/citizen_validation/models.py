"""
Traceability models for external API communications.

CORE FUNCTIONALITY #1: Track validation requests to external centralizer.
"""

from django.db import models
from django.utils import timezone


class CitizenValidationTrace(models.Model):
    """
    Traceability for citizen validation requests to external centralizer.
    
    This microservice does NOT store citizen data, it only tracks:
    - Who requested validation
    - When it was requested
    - What the external API responded
    """
    
    STATUS_CHOICES = [
        ('EXISTS', 'Exists in Centralizer'),
        ('NOT_EXISTS', 'Does Not Exist'),
        ('ERROR', 'Error'),
    ]
    
    # Request info
    citizen_id = models.CharField(max_length=50, db_index=True)
    requested_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    # External API response
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    external_api_status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'citizen_validation_traces'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['citizen_id', '-requested_at']),
        ]
        verbose_name = 'Validation Trace'
        verbose_name_plural = 'Validation Traces'

    def __str__(self):
        return f"Trace - Citizen {self.citizen_id} - {self.status}"

    @property
    def is_eligible(self) -> bool:
        """True if citizen can be registered (not in centralizer)."""
        return self.status == 'NOT_EXISTS'

