"""
Authentication infrastructure for OAuth2 integration.
"""

from .oauth2_validator import (
    OAuth2ClientCredentialsValidator,
    get_oauth2_validator,
    require_client_credentials,
)

__all__ = [
    'OAuth2ClientCredentialsValidator',
    'get_oauth2_validator',
    'require_client_credentials',
]
