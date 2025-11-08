"""
Base HTTP client for external API integrations.
"""

import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for external API clients with retry logic and error handling."""

    def __init__(self, base_url: str, timeout: int = 30, api_key: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get request headers.

        Args:
            additional_headers: Optional additional headers to include

        Returns:
            Dictionary of headers
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Optional query parameters
            headers: Optional additional headers

        Returns:
            Response object

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)
        
        logger.info(f"GET request to {url}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )
            logger.info(f"GET {url} - Status: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"GET {url} failed: {str(e)}")
            raise

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint (will be appended to base_url)
            data: Optional request body data
            headers: Optional additional headers

        Returns:
            Response object

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)
        
        logger.info(f"POST request to {url}")
        
        try:
            response = self.session.post(
                url,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            logger.info(f"POST {url} - Status: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"POST {url} failed: {str(e)}")
            raise
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint (will be appended to base_url)
            data: Optional request body data
            headers: Optional additional headers

        Returns:
            Response object

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)
        
        logger.info(f"PUT request to {url}")
        
        try:
            response = self.session.put(
                url,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            logger.info(f"PUT {url} - Status: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"PUT {url} failed: {str(e)}")
            raise

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
