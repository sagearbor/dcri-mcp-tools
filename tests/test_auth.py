"""
Tests for the Microsoft Graph API authentication module.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException, HTTPError

from auth.graph_auth import (
    GraphAuthClient,
    TokenInfo,
    get_default_client,
    get_access_token,
    get_authorization_header
)


class TestTokenInfo:
    """Test the TokenInfo dataclass."""
    
    def test_token_info_creation(self):
        """Test creating a TokenInfo instance."""
        expires_at = datetime.now() + timedelta(hours=1)
        token_info = TokenInfo(
            access_token="test_token",
            expires_at=expires_at,
            token_type="Bearer",
            scope="test_scope"
        )
        
        assert token_info.access_token == "test_token"
        assert token_info.expires_at == expires_at
        assert token_info.token_type == "Bearer"
        assert token_info.scope == "test_scope"
    
    def test_token_info_defaults(self):
        """Test TokenInfo default values."""
        expires_at = datetime.now()
        token_info = TokenInfo(
            access_token="test_token",
            expires_at=expires_at
        )
        
        assert token_info.token_type == "Bearer"
        assert token_info.scope == ""


class TestGraphAuthClient:
    """Test the GraphAuthClient class."""
    
    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Set up mock environment variables."""
        monkeypatch.setenv('AZURE_TENANT_ID', 'test-tenant-id')
        monkeypatch.setenv('AZURE_CLIENT_ID', 'test-client-id')
        monkeypatch.setenv('AZURE_CLIENT_SECRET', 'test-client-secret')
    
    @pytest.fixture
    def client(self):
        """Create a test client with explicit credentials."""
        return GraphAuthClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret"
        )
    
    def test_client_initialization_with_params(self):
        """Test client initialization with explicit parameters."""
        client = GraphAuthClient(
            tenant_id="tenant123",
            client_id="client456",
            client_secret="secret789",
            scope="custom_scope"
        )
        
        assert client.tenant_id == "tenant123"
        assert client.client_id == "client456"
        assert client.client_secret == "secret789"
        assert client.scope == "custom_scope"
        assert client.token_endpoint == "https://login.microsoftonline.com/tenant123/oauth2/v2.0/token"
    
    def test_client_initialization_from_env(self, mock_env_vars):
        """Test client initialization from environment variables."""
        client = GraphAuthClient()
        
        assert client.tenant_id == "test-tenant-id"
        assert client.client_id == "test-client-id"
        assert client.client_secret == "test-client-secret"
        assert client.scope == GraphAuthClient.DEFAULT_SCOPE
    
    def test_client_initialization_missing_credentials(self):
        """Test client initialization with missing credentials."""
        with pytest.raises(ValueError) as exc_info:
            GraphAuthClient(tenant_id="test")
        
        assert "Missing required configuration" in str(exc_info.value)
    
    @patch('auth.graph_auth.requests.Session')
    def test_request_token_success(self, mock_session_class, client):
        """Test successful token request."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600,
            'token_type': 'Bearer',
            'scope': 'test_scope'
        }
        mock_session.post.return_value = mock_response
        
        # Create new client to use mocked session
        client = GraphAuthClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret"
        )
        
        token_info = client._request_token()
        
        assert token_info.access_token == 'test_access_token'
        assert token_info.token_type == 'Bearer'
        assert token_info.scope == 'test_scope'
        assert isinstance(token_info.expires_at, datetime)
        
        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == client.token_endpoint
        assert call_args[1]['data']['client_id'] == 'test-client'
        assert call_args[1]['data']['client_secret'] == 'test-secret'
        assert call_args[1]['data']['grant_type'] == 'client_credentials'
    
    @patch('auth.graph_auth.requests.Session')
    def test_request_token_failure(self, mock_session_class, client):
        """Test failed token request."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        mock_session.post.return_value = mock_response
        
        # Create new client to use mocked session
        client = GraphAuthClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret"
        )
        
        with pytest.raises(HTTPError):
            client._request_token()
    
    def test_get_access_token_cached(self, client):
        """Test getting cached access token."""
        # Set up cached token
        future_time = datetime.now() + timedelta(hours=1)
        client._token_info = TokenInfo(
            access_token="cached_token",
            expires_at=future_time
        )
        
        token = client.get_access_token()
        assert token == "cached_token"
    
    @patch.object(GraphAuthClient, '_request_token')
    def test_get_access_token_expired(self, mock_request_token, client):
        """Test getting new token when cached token is expired."""
        # Set up expired token
        past_time = datetime.now() - timedelta(hours=1)
        client._token_info = TokenInfo(
            access_token="expired_token",
            expires_at=past_time
        )
        
        # Mock new token request
        future_time = datetime.now() + timedelta(hours=1)
        mock_request_token.return_value = TokenInfo(
            access_token="new_token",
            expires_at=future_time
        )
        
        token = client.get_access_token()
        
        assert token == "new_token"
        mock_request_token.assert_called_once()
    
    @patch.object(GraphAuthClient, '_request_token')
    def test_get_access_token_force_refresh(self, mock_request_token, client):
        """Test forcing token refresh."""
        # Set up valid cached token
        future_time = datetime.now() + timedelta(hours=1)
        client._token_info = TokenInfo(
            access_token="cached_token",
            expires_at=future_time
        )
        
        # Mock new token request
        mock_request_token.return_value = TokenInfo(
            access_token="refreshed_token",
            expires_at=future_time
        )
        
        token = client.get_access_token(force_refresh=True)
        
        assert token == "refreshed_token"
        mock_request_token.assert_called_once()
    
    def test_get_authorization_header(self, client):
        """Test getting authorization header."""
        # Set up cached token
        future_time = datetime.now() + timedelta(hours=1)
        client._token_info = TokenInfo(
            access_token="test_token",
            expires_at=future_time
        )
        
        header = client.get_authorization_header()
        
        assert header == {'Authorization': 'Bearer test_token'}
    
    @patch.object(GraphAuthClient, 'get_authorization_header')
    def test_make_graph_request_success(self, mock_get_header, client):
        """Test successful Graph API request."""
        mock_get_header.return_value = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        
        with patch.object(client._session, 'request', return_value=mock_response):
            response = client.make_graph_request(
                method='GET',
                url='https://graph.microsoft.com/v1.0/users'
            )
        
        assert response.status_code == 200
        assert response.json() == {'data': 'test'}
    
    @patch.object(GraphAuthClient, 'get_authorization_header')
    def test_make_graph_request_retry_on_401(self, mock_get_header, client):
        """Test retry on 401 response."""
        # First call returns old token, second returns new token
        mock_get_header.side_effect = [
            {'Authorization': 'Bearer old_token'},
            {'Authorization': 'Bearer new_token'}
        ]
        
        # First response is 401, second is 200
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'data': 'success'}
        
        with patch.object(client._session, 'request', side_effect=[mock_response_401, mock_response_200]):
            response = client.make_graph_request(
                method='GET',
                url='https://graph.microsoft.com/v1.0/users'
            )
        
        assert response.status_code == 200
        assert mock_get_header.call_count == 2
        assert mock_get_header.call_args_list[1][1]['force_refresh'] is True
    
    @patch.object(GraphAuthClient, 'make_graph_request')
    @patch.object(GraphAuthClient, 'get_access_token')
    def test_test_connection_app_only(self, mock_get_token, mock_make_request, client):
        """Test connection test for app-only authentication."""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 400  # Expected for app-only auth on /me endpoint
        mock_make_request.return_value = mock_response
        
        result = client.test_connection()
        
        assert result is True
        mock_get_token.assert_called_once()
        mock_make_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/me',
            timeout=10
        )
    
    @patch.object(GraphAuthClient, 'make_graph_request')
    @patch.object(GraphAuthClient, 'get_access_token')
    def test_test_connection_delegated(self, mock_get_token, mock_make_request, client):
        """Test connection test for delegated authentication."""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_make_request.return_value = mock_response
        
        result = client.test_connection()
        
        assert result is True
    
    @patch.object(GraphAuthClient, 'make_graph_request')
    @patch.object(GraphAuthClient, 'get_access_token')
    def test_test_connection_failure(self, mock_get_token, mock_make_request, client):
        """Test connection test failure."""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_make_request.return_value = mock_response
        
        result = client.test_connection()
        
        assert result is False
    
    @patch.object(GraphAuthClient, 'get_access_token')
    def test_test_connection_exception(self, mock_get_token, client):
        """Test connection test with exception."""
        mock_get_token.side_effect = Exception("Connection error")
        
        result = client.test_connection()
        
        assert result is False
    
    def test_context_manager(self, client):
        """Test using client as context manager."""
        with client as ctx_client:
            assert ctx_client is client
            assert client._session is not None
        
        # Session should be closed after exiting context
        # Note: We can't directly test if session is closed,
        # but we can verify the close method was callable
    
    def test_close_session(self, client):
        """Test closing the session."""
        mock_session = Mock()
        client._session = mock_session
        
        client.close()
        
        mock_session.close.assert_called_once()


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    @pytest.fixture
    def reset_default_client(self):
        """Reset the default client before and after tests."""
        import auth.graph_auth
        auth.graph_auth._default_client = None
        yield
        auth.graph_auth._default_client = None
    
    @patch('auth.graph_auth.GraphAuthClient')
    def test_get_default_client(self, mock_client_class, reset_default_client):
        """Test getting the default client."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # First call creates client
        client1 = get_default_client()
        assert client1 is mock_client
        mock_client_class.assert_called_once()
        
        # Second call returns same client
        client2 = get_default_client()
        assert client2 is client1
        assert mock_client_class.call_count == 1  # Still only called once
    
    @patch('auth.graph_auth.get_default_client')
    def test_get_access_token_convenience(self, mock_get_default):
        """Test the convenience function for getting access token."""
        mock_client = Mock()
        mock_client.get_access_token.return_value = "convenience_token"
        mock_get_default.return_value = mock_client
        
        token = get_access_token()
        
        assert token == "convenience_token"
        mock_get_default.assert_called_once()
        mock_client.get_access_token.assert_called_once()
    
    @patch('auth.graph_auth.get_default_client')
    def test_get_authorization_header_convenience(self, mock_get_default):
        """Test the convenience function for getting authorization header."""
        mock_client = Mock()
        mock_client.get_authorization_header.return_value = {'Authorization': 'Bearer convenience_token'}
        mock_get_default.return_value = mock_client
        
        header = get_authorization_header()
        
        assert header == {'Authorization': 'Bearer convenience_token'}
        mock_get_default.assert_called_once()
        mock_client.get_authorization_header.assert_called_once()


class TestIntegration:
    """Integration tests that test multiple components together."""
    
    @pytest.mark.integration
    @patch('auth.graph_auth.requests.Session')
    def test_full_token_flow(self, mock_session_class):
        """Test the complete token acquisition and usage flow."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            'access_token': 'integration_token',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        
        # Mock API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {'users': ['user1', 'user2']}
        
        mock_session.post.return_value = mock_token_response
        mock_session.request.return_value = mock_api_response
        
        # Create client and make request
        client = GraphAuthClient(
            tenant_id="int-tenant",
            client_id="int-client",
            client_secret="int-secret"
        )
        
        response = client.make_graph_request(
            method='GET',
            url='https://graph.microsoft.com/v1.0/users'
        )
        
        assert response.status_code == 200
        assert response.json() == {'users': ['user1', 'user2']}
        
        # Verify token was requested
        assert mock_session.post.called
        
        # Verify API call included authorization
        api_call_args = mock_session.request.call_args
        assert 'Authorization' in api_call_args[1]['headers']
        assert api_call_args[1]['headers']['Authorization'] == 'Bearer integration_token'