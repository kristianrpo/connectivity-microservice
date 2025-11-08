"""
Service for forwarding document authentication to external centralizer.

CORE FUNCTIONALITY #3: Forward authentication requests (proxy).
"""

import logging
from django.utils import timezone

from .models import DocumentAuthenticationTrace
from infrastructure.external_apis.govcarpeta_client import get_govcarpeta_client
from infrastructure.rabbitmq.producer import get_rabbitmq_producer

logger = logging.getLogger(__name__)


class DocumentAuthenticationService:
    """
    Service for forwarding document authentication to external centralizer.
    
    This service does NOT store documents, it only:
    1. Receives authentication request
    2. Forwards to external centralizer API
    3. Publishes result event
    4. Tracks the communication (traceability)
    """
    
    def __init__(self):
        self.api_client = get_govcarpeta_client()
        self.rabbitmq_producer = get_rabbitmq_producer()
    
    def process_authentication_request(
        self,
        message_id: str,
        document_id: str,
        id_citizen: int,
        url_document: str,
        document_title: str
    ) -> DocumentAuthenticationTrace:
        """
        Forward document authentication to external centralizer.
        
        IDEMPOTENCY: Uses message_id to prevent duplicate processing.
        
        Workflow:
        1. Check idempotency (message_id)
        2. Create trace record
        3. Forward to external API
        4. Update trace
        5. Publish result event
        """
        logger.info(f"Processing authentication for document {document_id}, citizen {id_citizen}")
        
        # IDEMPOTENCY CHECK
        existing = DocumentAuthenticationTrace.objects.filter(message_id=message_id).first()
        if existing:
            logger.info(f"Message {message_id} already processed, status: {existing.status}")
            return existing
        
        # Create trace record
        trace = DocumentAuthenticationTrace.objects.create(
            message_id=message_id,
            document_id=document_id,
            id_citizen=id_citizen,
            document_title=document_title,
            status='PENDING'
        )
        
        try:
            api_response = self.api_client.authenticate_document(
                id_citizen=id_citizen,
                url_document=url_document,
                document_title=document_title
            )
            
            success = api_response['success'] and api_response['status_code'] == 200
            result_message = api_response.get('message', 'Authentication completed')
            
            trace.mark_as_authenticated(
                status_code=api_response['status_code'],
                success=success,
                message=result_message
            )
            
            logger.info(f"Document {document_id} authenticated, success: {success}")
            
            self._publish_result_event(trace)
            return trace
            
        except Exception as e:
            logger.error(f"Error authenticating document {document_id}: {str(e)}", exc_info=True)
            trace.mark_as_error(error_message=str(e))
            
            try:
                self._publish_result_event(trace)
            except Exception as publish_error:
                logger.error(f"Failed to publish error event: {str(publish_error)}")
            
            raise
    
    def _publish_result_event(self, trace: DocumentAuthenticationTrace):
        """
        Publish authentication result to RabbitMQ.
        
        Event format matches what document-management expects:
        {
            "messageId": "uuid",
            "documentId": "doc-123",
            "idCitizen": 12345678,
            "authenticated": true/false,
            "message": "Authentication result message",
            "authenticatedAt": "2025-11-07T18:28:36.788Z"
        }
        """
        event_data = {
            "messageId": trace.message_id,
            "documentId": trace.document_id,
            "idCitizen": trace.id_citizen,
            "authenticated": trace.authenticated,
            "message": trace.message or ("Authentication successful" if trace.authenticated else "Authentication failed"),
            "authenticatedAt": trace.authenticated_at.isoformat() if trace.authenticated_at else timezone.now().isoformat()
        }
        
        # Use single routing key for all results
        routing_key = 'document.authentication.completed'
        
        try:
            self.rabbitmq_producer.publish_event(
                routing_key=routing_key,
                event_data=event_data
            )
            trace.mark_event_published()
            logger.info(f"Published authentication result for document {trace.document_id}")
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}", exc_info=True)
            raise
