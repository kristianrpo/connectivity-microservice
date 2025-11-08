"""
Govcarpeta API client for citizen validation.
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class GovcarpetaAPIClient(BaseAPIClient):
    """Client for interacting with Govcarpeta API."""

    def __init__(self):
        """Initialize the Govcarpeta API client with settings from Django config."""
        base_url = settings.EXTERNAL_GOVCARPETA_API_URL
        api_key = settings.EXTERNAL_GOVCARPETA_API_KEY
        timeout = settings.EXTERNAL_API_TIMEOUT
        
        super().__init__(base_url=base_url, timeout=timeout, api_key=api_key)

    def validate_citizen(self, citizen_id: str) -> Dict[str, Any]:
        """
        Validate if a citizen exists in the system.

        Args:
            citizen_id: The citizen's identification number

        Returns:
            Dictionary with validation result:
            {
                'exists': bool,
                'citizen_data': dict or None,
                'message': str
            }

        Raises:
            requests.RequestException: If the API call fails
        """
        endpoint = f"apis/validateCitizen/{citizen_id}"
        
        logger.info(f"Validating citizen with ID: {citizen_id}")
        
        try:
            response = self.get(endpoint)
            
            # Status 200: Citizen exists
            if response.status_code == 200:
                citizen_data = response.json()
                logger.info(f"Citizen {citizen_id} found")
                return {
                    'exists': True,
                    'citizen_data': citizen_data,
                    'message': 'Citizen found successfully',
                    'status_code': 200
                }
            
            # Status 204: Citizen does not exist
            elif response.status_code == 204:
                logger.info(f"Citizen {citizen_id} not found (204 No Content)")
                return {
                    'exists': False,
                    'citizen_data': None,
                    'message': 'Citizen does not exist in the system',
                    'status_code': 204
                }
            
            # Other status codes
            else:
                logger.warning(f"Unexpected status code {response.status_code} for citizen {citizen_id}")
                return {
                    'exists': False,
                    'citizen_data': None,
                    'message': f'Unexpected response from external API: {response.status_code}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error validating citizen {citizen_id}: {str(e)}")
            raise
    
    def register_citizen(
        self,
        id_citizen: int,
        name: str,
        email: str,
        address: str = "Cra 44 # 45 - 67",
        operator_name: str = "Coordenador Ciudadano"
    ) -> Dict[str, Any]:
        """
        Register a citizen in the external centralizer.
        
        Args:
            id_citizen: Citizen identification number
            name: Citizen full name
            email: Citizen email
            address: Citizen address (optional)
            operator_name: Operator name (optional)
            
        Returns:
            Dictionary with registration result
            
        Raises:
            requests.RequestException: If the API call fails
        """
        endpoint = "apis/registerCitizen"
        
        payload = {
            "id": id_citizen,
            "name": name,
            "address": address,
            "email": email,
            "operatorName": operator_name
        }
        
        logger.info(f"Registering citizen {id_citizen} in centralizer")
        
        try:
            response = self.post(endpoint, data=payload)
            
            if response.status_code == 201:
                logger.info(f"Citizen {id_citizen} registered successfully")
                return {
                    'success': True,
                    'status_code': 201,
                    'message': 'Citizen registered successfully',
                    'data': response.json() if response.text else None
                }
            else:
                logger.warning(f"Failed to register citizen {id_citizen}: Status {response.status_code}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': f'Registration failed: {response.status_code}',
                    'data': response.json() if response.text else None
                }
                
        except Exception as e:
            logger.error(f"Error registering citizen {id_citizen}: {str(e)}", exc_info=True)
            raise
    
    def authenticate_document(
        self,
        id_citizen: int,
        url_document: str,
        document_title: str
    ) -> Dict[str, Any]:
        """
        Authenticate a document through the Govcarpeta API.
        
        Args:
            id_citizen: Citizen identification number
            url_document: URL to the document (S3 URL)
            document_title: Title/type of the document
            
        Returns:
            Dictionary with authentication result:
            {
                'success': bool,
                'status_code': int,
                'message': str,
                'data': dict or None
            }
            
        Raises:
            requests.RequestException: If the API call fails
        """
        endpoint = "apis/authenticateDocument"
        
        payload = {
            "idCitizen": id_citizen,
            "UrlDocument": url_document,
            "documentTitle": document_title
        }
        
        logger.info(
            f"Authenticating document for citizen {id_citizen}: {document_title}"
        )
        
        try:
            response = self.put(endpoint, data=payload)
            
            # Status 200: Document authenticated successfully
            if response.status_code == 200:
                logger.info(f"Document authenticated successfully for citizen {id_citizen}")
                response_data = None
                try:
                    if response.text:
                        response_data = response.json()
                except ValueError:
                    response_data = {'raw_response': response.text}
                
                return {
                    'success': True,
                    'status_code': 200,
                    'message': 'Document authenticated successfully',
                    'data': response_data
                }
            
            # Other status codes
            else:
                logger.warning(
                    f"Document authentication failed for citizen {id_citizen}: "
                    f"Status {response.status_code}"
                )
                response_data = None
                try:
                    if response.text:
                        response_data = response.json()
                except ValueError:
                    response_data = {'raw_response': response.text}
                
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': f'Document authentication failed: {response.status_code}',
                    'data': response_data
                }
                
        except Exception as e:
            logger.error(
                f"Error authenticating document for citizen {id_citizen}: {str(e)}",
                exc_info=True
            )
            raise


# Singleton instance
_govcarpeta_client = None


def get_govcarpeta_client() -> GovcarpetaAPIClient:
    """
    Get or create a singleton instance of the Govcarpeta API client.

    Returns:
        GovcarpetaAPIClient instance
    """
    global _govcarpeta_client
    
    if _govcarpeta_client is None:
        _govcarpeta_client = GovcarpetaAPIClient()
    
    return _govcarpeta_client
