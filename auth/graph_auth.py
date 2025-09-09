"""
Microsoft Graph API authentication module for DCRI MCP Tools.

This module handles authentication with Microsoft Graph API using the
client credentials flow to access SharePoint resources.
"""

import os
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Container for access token information."""
    access_token: str
    expires_at: datetime
    token_type: str = "Bearer"
    scope: str = ""


class GraphAuthClient:
    """
    Microsoft Graph API authentication client.
    
    Handles OAuth2 client credentials flow for accessing Microsoft Graph API
    and SharePoint resources. Includes automatic token refresh and caching.
    """
    
    DEFAULT_SCOPE = "https://graph.microsoft.com/.default"
    TOKEN_ENDPOINT_TEMPLATE = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
    
    def __init__(
        self, 
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None
    ):
        """
        Initialize the Graph authentication client.
        
        Args:
            tenant_id: Azure AD tenant ID (defaults to env var AZURE_TENANT_ID)
            client_id: Application client ID (defaults to env var AZURE_CLIENT_ID)
            client_secret: Application client secret (defaults to env var AZURE_CLIENT_SECRET)
            scope: OAuth scope (defaults to Microsoft Graph default scope)
        """
        self.tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        self.client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
        self.scope = scope or self.DEFAULT_SCOPE
        
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required configuration. Please provide tenant_id, "
                "client_id, and client_secret either as parameters or environment variables."
            )
        
        self.token_endpoint = self.TOKEN_ENDPOINT_TEMPLATE.format(self.tenant_id)
        self._token_info: Optional[TokenInfo] = None
        self._session = requests.Session()
        
    def _request_token(self) -> TokenInfo:
        """
        Request a new access token from Azure AD.
        
        Returns:
            TokenInfo object containing the access token and expiration
            
        Raises:
            RequestException: If the token request fails
        """
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = self._session.post(
                self.token_endpoint,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Calculate token expiration (subtract buffer for safety)
            expires_in = data.get('expires_in', 3600)
            buffer_seconds = 300  # 5 minute buffer
            expires_at = datetime.now() + timedelta(seconds=expires_in - buffer_seconds)
            
            token_info = TokenInfo(
                access_token=data['access_token'],
                expires_at=expires_at,
                token_type=data.get('token_type', 'Bearer'),
                scope=data.get('scope', self.scope)
            )
            
            logger.info(f"Successfully obtained access token, expires at {expires_at}")
            return token_info
            
        except RequestException as e:
            logger.error(f"Failed to obtain access token: {str(e)}")
            raise
            
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Valid access token string
            
        Raises:
            RequestException: If unable to obtain a valid token
        """
        # Check if we need a new token
        if force_refresh or self._token_info is None or datetime.now() >= self._token_info.expires_at:
            logger.info("Refreshing access token...")
            self._token_info = self._request_token()
            
        return self._token_info.access_token
    
    def get_authorization_header(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Get the authorization header for API requests.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Dictionary containing the Authorization header
        """
        token = self.get_access_token(force_refresh)
        return {'Authorization': f'Bearer {token}'}
    
    def make_graph_request(
        self, 
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an authenticated request to the Microsoft Graph API.
        
        Automatically includes authentication header and handles token refresh
        on 401 responses.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL for the Graph API endpoint
            headers: Additional headers to include
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object from the API
            
        Raises:
            RequestException: If the request fails after retry
        """
        # Prepare headers
        auth_header = self.get_authorization_header()
        if headers:
            headers.update(auth_header)
        else:
            headers = auth_header
            
        # Make initial request
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )
        
        # Handle token expiration
        if response.status_code == 401:
            logger.info("Received 401, refreshing token and retrying...")
            auth_header = self.get_authorization_header(force_refresh=True)
            headers.update(auth_header)
            
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
        return response
    
    def test_connection(self) -> bool:
        """
        Test the connection and authentication to Microsoft Graph.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        try:
            # Try to get a token
            token = self.get_access_token()
            
            # Make a simple request to validate the token
            response = self.make_graph_request(
                method='GET',
                url='https://graph.microsoft.com/v1.0/me',
                timeout=10
            )
            
            # For app-only auth, /me won't work, so check for appropriate error
            if response.status_code == 400:  # Bad request is expected for app-only auth
                logger.info("Authentication successful (app-only context)")
                return True
            elif response.status_code == 200:
                logger.info("Authentication successful (delegated context)")
                return True
            else:
                logger.error(f"Authentication test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication test failed: {str(e)}")
            return False
    
    def close(self):
        """Close the session and clean up resources."""
        if self._session:
            self._session.close()
            
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance for module-level usage
_default_client: Optional[GraphAuthClient] = None


def get_default_client() -> GraphAuthClient:
    """
    Get or create the default Graph authentication client.
    
    Returns:
        GraphAuthClient instance
        
    Raises:
        ValueError: If required configuration is missing
    """
    global _default_client
    
    if _default_client is None:
        _default_client = GraphAuthClient()
        
    return _default_client


def get_access_token() -> str:
    """
    Convenience function to get an access token using the default client.
    
    Returns:
        Valid access token string
    """
    client = get_default_client()
    return client.get_access_token()


def get_authorization_header() -> Dict[str, str]:
    """
    Convenience function to get authorization header using the default client.
    
    Returns:
        Dictionary containing the Authorization header
    """
    client = get_default_client()
    return client.get_authorization_header()