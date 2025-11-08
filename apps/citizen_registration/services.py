"""
Service for forwarding registration requests to external centralizer.

CORE FUNCTIONALITY #2: Forward registration to external API (proxy).
"""

import logging
from django.utils import timezone

from .models import CitizenRegistrationTrace
from infrastructure.external_apis.govcarpeta_client import get_govcarpeta_client

logger = logging.getLogger(__name__)


class CitizenRegistrationService:
    """
    Service for forwarding citizen registration to external centralizer.
    
    This service does NOT register citizens locally, it only:
    1. Receives auth.user.registered event
    2. Forwards to external centralizer API
    3. Tracks the communication (traceability)
    """
    
    def __init__(self):
        self.api_client = get_govcarpeta_client()
    
    def process_auth_registration_event(
        self,
        message_id: str,
        id_citizen: int,
        name: str,
        email: str,
        timestamp: str
    ) -> CitizenRegistrationTrace:
        """
        Forward registration request to external centralizer.
        
        Args:
            message_id: Event ID (for idempotency)
            id_citizen: Citizen ID
            name: Citizen name (forwarded to external API)
            email: Citizen email (forwarded to external API)
            timestamp: Registration timestamp
            
        Returns:
            CitizenRegistrationTrace: Communication trace record
        """
        logger.info(f"Forwarding registration for citizen {id_citizen} to centralizer")
        
        # Idempotency check
        existing = CitizenRegistrationTrace.objects.filter(message_id=message_id).first()
        if existing:
            logger.info(f"Event {message_id} already processed, status: {existing.status}")
            return existing
        
        # Create trace record
        trace = CitizenRegistrationTrace.objects.create(
            message_id=message_id,
            id_citizen=id_citizen,
            status='PENDING'
        )
        
        try:
            logger.info(f"Sending registration request to centralizer for citizen {id_citizen}")
            
            # Call external API to register citizen in centralizer
            api_response = self.api_client.register_citizen(
                id_citizen=id_citizen,
                name=name,
                email=email
            )
            
            # Mark as sent with actual API response
            if api_response.get('success'):
                trace.mark_as_sent(
                    status_code=api_response.get('status_code', 201),
                    response_data=api_response.get('data')
                )
                logger.info(f"✅ Citizen {id_citizen} registered successfully in centralizer")
            else:
                trace.mark_as_error(
                    error_message=api_response.get('message', 'Registration failed')
                )
                logger.error(f"❌ Failed to register citizen {id_citizen}: {api_response.get('message')}")
            
            return trace
            
        except Exception as e:
            logger.error(f"Error forwarding registration for citizen {id_citizen}: {str(e)}", exc_info=True)
            trace.mark_as_error(error_message=str(e))
            raise
