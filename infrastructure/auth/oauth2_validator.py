"""
OAuth2 Client Credentials validator for auth-microservice integration.

Validates JWT tokens locally using shared secret key.
"""

import logging
import jwt
from typing import Optional, Dict, Any
from django.conf import settings
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class OAuth2ClientCredentialsValidator:
    """
    Validates OAuth2 Client Credentials JWT tokens from auth-microservice.
    
    Uses local JWT validation with shared secret key for performance.
    """
    
    def __init__(self):
        self.jwt_secret = getattr(
            settings, 
            'AUTH_SERVICE_JWT_SECRET', 
            settings.SECRET_KEY  # Fallback to Django secret
        )
        self.jwt_algorithm = getattr(settings, 'AUTH_SERVICE_JWT_ALGORITHM', 'HS256')
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT access token locally.
        
        Args:
            token: JWT Bearer token to validate
            
        Returns:
            Dictionary with validation result:
            {
                'valid': bool,
                'client_id': str or None,
                'scope': str or None,
                'exp': int or None,
                'error': str or None
            }
        """
        if not token:
            return {
                'valid': False,
                'error': 'No token provided'
            }
        
        try:
            # Decode and validate JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'require': ['exp', 'client_id']
                }
            )
            
            # Extract token information
            client_id = payload.get('client_id')
            scope = payload.get('scope', '')
            exp = payload.get('exp')
            grant_type = payload.get('grant_type')
            
            # Verify it's a client_credentials token
            if grant_type and grant_type != 'client_credentials':
                logger.warning(
                    f"Token is not client_credentials type: {grant_type}"
                )
                return {
                    'valid': False,
                    'error': 'Token is not a client_credentials grant type'
                }
            
            logger.info(
                f"Token validated successfully for client: {client_id}"
            )
            
            return {
                'valid': True,
                'client_id': client_id,
                'scope': scope,
                'exp': exp,
                'error': None
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return {
                'valid': False,
                'error': 'Token has expired'
            }
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return {
                'valid': False,
                'error': f'Invalid token: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}", exc_info=True)
            return {
                'valid': False,
                'error': f'Token validation error: {str(e)}'
            }
    
    def extract_token_from_header(self, authorization_header: Optional[str]) -> Optional[str]:
        """
        Extract Bearer token from Authorization header.
        
        Args:
            authorization_header: Authorization header value
            
        Returns:
            Token string or None
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


# Singleton instance
_validator = None


def get_oauth2_validator() -> OAuth2ClientCredentialsValidator:
    """Get or create singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = OAuth2ClientCredentialsValidator()
    return _validator


def require_client_credentials(view_func):
    """
    Decorator to require valid OAuth2 Client Credentials token.
    
    Usage:
        @require_client_credentials
        def my_view(request):
            # Access validated client info
            client_id = request.oauth_client_id
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        validator = get_oauth2_validator()
        
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        token = validator.extract_token_from_header(auth_header)
        
        if not token:
            logger.warning("Missing or invalid Authorization header")
            return Response(
                {
                    'error': 'Unauthorized',
                    'message': 'Valid Bearer token required'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Validate token
        validation_result = validator.validate_token(token)
        
        if not validation_result['valid']:
            logger.warning(
                f"Token validation failed: {validation_result.get('error')}"
            )
            return Response(
                {
                    'error': 'Unauthorized',
                    'message': validation_result.get('error', 'Invalid token')
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Attach client info to request
        request.oauth_client_id = validation_result.get('client_id')
        request.oauth_scope = validation_result.get('scope')
        
        logger.info(
            f"Request authenticated for client: {request.oauth_client_id}"
        )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
