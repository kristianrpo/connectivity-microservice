"""
External API for auth-microservice integration.

CORE FUNCTIONALITY #1: Validate citizen existence for auth-microservice.
"""

import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from infrastructure.auth import require_client_credentials
from infrastructure.external_apis.govcarpeta_client import get_govcarpeta_client

logger = logging.getLogger(__name__)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='idCitizen',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Citizen ID to verify',
            required=True
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        204: None,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    description="Check if citizen exists in centralizer (for auth-microservice)",
    tags=['External API']
)
@api_view(['GET'])
@require_client_credentials
def check_citizen_exists(request, idCitizen):
    """
    Validate citizen existence in centralizer.
    
    Called by auth-microservice before user registration.
    
    Returns:
        200: Citizen EXISTS (reject registration)
        204: Citizen DOES NOT exist (allow registration)
    """
    logger.info(f"Validation request from '{request.oauth_client_id}' for citizen {idCitizen}")
    
    try:
        citizen_id_int = int(idCitizen)
        if citizen_id_int <= 0:
            raise ValueError("Invalid ID")
    except (ValueError, TypeError):
        logger.warning(f"Invalid citizen ID: {idCitizen}")
        return Response(
            {'error': 'Invalid citizen ID'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        api_client = get_govcarpeta_client()
        result = api_client.validate_citizen(str(citizen_id_int))
        
        if result['exists']:
            logger.info(f"Citizen {idCitizen} EXISTS in centralizer")
            return Response({'exists': True}, status=status.HTTP_200_OK)
        else:
            logger.info(f"Citizen {idCitizen} NOT in centralizer")
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        logger.error(f"Error validating citizen {idCitizen}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

