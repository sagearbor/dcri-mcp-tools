"""
Tests for the SharePoint client module.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
from requests.exceptions import RequestException

from sharepoint.sharepoint_client import (
    SharePointClient,
    SharePointFile,
    SharePointFolder
)


class TestSharePointFile:
    """Test the SharePointFile dataclass."""
    
    def test_sharepoint_file_creation(self):
        """Test creating a SharePointFile instance."""
        created_dt = datetime.now()
        modified_dt = datetime.now()
        
        file = SharePointFile(
            id="file123",
            name="test.docx",
            size=1024,
            created_datetime=created_dt,
            last_modified_datetime=modified_dt,
            web_url="https://sharepoint.com/test.docx",
            download_url="https://download.url",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            created_by="John Doe",
            modified_by="Jane Doe",
            parent_path="/documents"
        )
        
        assert file.id == "file123"
        assert file.name == "test.docx"
        assert file.size == 1024
        assert file.created_datetime == created_dt
        assert file.last_modified_datetime == modified_dt
        assert file.web_url == "https://sharepoint.com/test.docx"
        assert file.download_url == "https://download.url"
        assert file.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert file.created_by == "John Doe"
        assert file.modified_by == "Jane Doe"
        assert file.parent_path == "/documents"


class TestSharePointFolder:
    """Test the SharePointFolder dataclass."""
    
    def test_sharepoint_folder_creation(self):
        """Test creating a SharePointFolder instance."""
        created_dt = datetime.now()
        modified_dt = datetime.now()
        
        folder = SharePointFolder(
            id="folder456",
            name="Projects",
            created_datetime=created_dt,
            last_modified_datetime=modified_dt,
            web_url="https://sharepoint.com/Projects",
            child_count=5,
            created_by="John Doe",
            modified_by="Jane Doe",
            parent_path="/documents"
        )
        
        assert folder.id == "folder456"
        assert folder.name == "Projects"
        assert folder.created_datetime == created_dt
        assert folder.last_modified_datetime == modified_dt
        assert folder.web_url == "https://sharepoint.com/Projects"
        assert folder.child_count == 5
        assert folder.created_by == "John Doe"
        assert folder.modified_by == "Jane Doe"
        assert folder.parent_path == "/documents"


class TestSharePointClient:
    """Test the SharePointClient class."""
    
    @pytest.fixture
    def mock_auth_client(self):
        """Create a mock auth client."""
        mock = Mock()
        mock.make_graph_request = Mock()
        return mock
    
    @pytest.fixture
    def client(self, mock_auth_client):
        """Create a test client with explicit site ID."""
        return SharePointClient(
            site_id="test-site-id",
            auth_client=mock_auth_client
        )
    
    def test_client_initialization_with_site_id(self, mock_auth_client):
        """Test client initialization with site ID."""
        client = SharePointClient(
            site_id="site123",
            auth_client=mock_auth_client
        )
        
        assert client.site_id == "site123"
        assert client.auth_client == mock_auth_client
    
    @patch.object(SharePointClient, '_get_site_id_from_url')
    def test_client_initialization_with_site_url(self, mock_get_site_id, mock_auth_client):
        """Test client initialization with site URL."""
        mock_get_site_id.return_value = "resolved-site-id"
        
        client = SharePointClient(
            site_url="https://contoso.sharepoint.com/sites/TestSite",
            auth_client=mock_auth_client
        )
        
        assert client.site_url == "https://contoso.sharepoint.com/sites/TestSite"
        assert client.site_id == "resolved-site-id"
        mock_get_site_id.assert_called_once_with("https://contoso.sharepoint.com/sites/TestSite")
    
    def test_client_initialization_missing_config(self, mock_auth_client):
        """Test client initialization with missing configuration."""
        with pytest.raises(ValueError) as exc_info:
            SharePointClient(auth_client=mock_auth_client)
        
        assert "Either site_id or site_url must be provided" in str(exc_info.value)
    
    def test_get_site_id_from_url(self, client):
        """Test getting site ID from URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'site-id-from-url'}
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        site_id = client._get_site_id_from_url("https://contoso.sharepoint.com/sites/TestSite")
        
        assert site_id == 'site-id-from-url'
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/TestSite'
        )
    
    def test_parse_file_item(self, client):
        """Test parsing a file item from API response."""
        item = {
            'id': 'file789',
            'name': 'document.pdf',
            'size': 2048,
            'createdDateTime': '2024-01-01T10:00:00Z',
            'lastModifiedDateTime': '2024-01-02T15:30:00Z',
            'webUrl': 'https://sharepoint.com/document.pdf',
            '@microsoft.graph.downloadUrl': 'https://download.url/document.pdf',
            'file': {'mimeType': 'application/pdf'},
            'createdBy': {'user': {'displayName': 'Creator'}},
            'lastModifiedBy': {'user': {'displayName': 'Modifier'}},
            'parentReference': {'path': '/drive/root:/Documents'}
        }
        
        file = client._parse_file_item(item)
        
        assert file.id == 'file789'
        assert file.name == 'document.pdf'
        assert file.size == 2048
        assert file.web_url == 'https://sharepoint.com/document.pdf'
        assert file.download_url == 'https://download.url/document.pdf'
        assert file.mime_type == 'application/pdf'
        assert file.created_by == 'Creator'
        assert file.modified_by == 'Modifier'
        assert file.parent_path == '/drive/root:/Documents'
    
    def test_parse_folder_item(self, client):
        """Test parsing a folder item from API response."""
        item = {
            'id': 'folder789',
            'name': 'Reports',
            'createdDateTime': '2024-01-01T10:00:00Z',
            'lastModifiedDateTime': '2024-01-02T15:30:00Z',
            'webUrl': 'https://sharepoint.com/Reports',
            'folder': {'childCount': 10},
            'createdBy': {'user': {'displayName': 'Creator'}},
            'lastModifiedBy': {'user': {'displayName': 'Modifier'}},
            'parentReference': {'path': '/drive/root:/Documents'}
        }
        
        folder = client._parse_folder_item(item)
        
        assert folder.id == 'folder789'
        assert folder.name == 'Reports'
        assert folder.web_url == 'https://sharepoint.com/Reports'
        assert folder.child_count == 10
        assert folder.created_by == 'Creator'
        assert folder.modified_by == 'Modifier'
        assert folder.parent_path == '/drive/root:/Documents'
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_list_drive_items_root(self, mock_get_drive, client):
        """Test listing items in root folder."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {
                    'id': 'file1',
                    'name': 'file1.txt',
                    'size': 100,
                    'createdDateTime': '2024-01-01T10:00:00Z',
                    'lastModifiedDateTime': '2024-01-01T10:00:00Z',
                    'webUrl': 'https://sharepoint.com/file1.txt',
                    'file': {'mimeType': 'text/plain'}
                },
                {
                    'id': 'folder1',
                    'name': 'Folder1',
                    'createdDateTime': '2024-01-01T10:00:00Z',
                    'lastModifiedDateTime': '2024-01-01T10:00:00Z',
                    'webUrl': 'https://sharepoint.com/Folder1',
                    'folder': {'childCount': 3}
                }
            ]
        }
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client.list_drive_items()
        
        assert len(result['files']) == 1
        assert len(result['folders']) == 1
        assert result['files'][0].name == 'file1.txt'
        assert result['folders'][0].name == 'Folder1'
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root/children',
            params={'$expand': 'thumbnails', '$top': 1000}
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_list_drive_items_subfolder(self, mock_get_drive, client):
        """Test listing items in a subfolder."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': []}
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client.list_drive_items(folder_path='Documents/Reports')
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root:/Documents%2FReports:/children',
            params={'$expand': 'thumbnails', '$top': 1000}
        )
    
    def test_get_default_drive_id(self, client):
        """Test getting default drive ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'default-drive-id'}
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        drive_id = client.get_default_drive_id()
        
        assert drive_id == 'default-drive-id'
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drive'
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    @patch('sharepoint.sharepoint_client.requests.get')
    def test_download_file_with_download_url(self, mock_requests_get, mock_get_drive, client):
        """Test downloading a file using download URL."""
        mock_get_drive.return_value = 'drive123'
        
        # Mock metadata response
        mock_metadata_response = Mock()
        mock_metadata_response.status_code = 200
        mock_metadata_response.json.return_value = {
            '@microsoft.graph.downloadUrl': 'https://download.url/file.txt'
        }
        
        client.auth_client.make_graph_request.return_value = mock_metadata_response
        
        # Mock download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b'File content'
        mock_requests_get.return_value = mock_download_response
        
        content = client.download_file('Documents/file.txt')
        
        assert content == b'File content'
        mock_requests_get.assert_called_once_with('https://download.url/file.txt')
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_download_file_without_download_url(self, mock_get_drive, client):
        """Test downloading a file without download URL."""
        mock_get_drive.return_value = 'drive123'
        
        # Mock metadata response without download URL
        mock_metadata_response = Mock()
        mock_metadata_response.status_code = 200
        mock_metadata_response.json.return_value = {'id': 'file123'}
        
        # Mock content response
        mock_content_response = Mock()
        mock_content_response.status_code = 200
        mock_content_response.content = b'File content direct'
        
        client.auth_client.make_graph_request.side_effect = [
            mock_metadata_response,
            mock_content_response
        ]
        
        content = client.download_file('Documents/file.txt')
        
        assert content == b'File content direct'
        assert client.auth_client.make_graph_request.call_count == 2
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('sharepoint.sharepoint_client.requests.get')
    def test_download_file_to_local_path(self, mock_requests_get, mock_makedirs, mock_file, mock_get_drive, client):
        """Test downloading a file to local path."""
        mock_get_drive.return_value = 'drive123'
        
        # Mock metadata response
        mock_metadata_response = Mock()
        mock_metadata_response.status_code = 200
        mock_metadata_response.json.return_value = {
            '@microsoft.graph.downloadUrl': 'https://download.url/file.txt'
        }
        
        client.auth_client.make_graph_request.return_value = mock_metadata_response
        
        # Mock download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b'File content'
        mock_requests_get.return_value = mock_download_response
        
        result = client.download_file('Documents/file.txt', local_path='/tmp/file.txt')
        
        assert result == '/tmp/file.txt'
        mock_makedirs.assert_called_once_with('/tmp', exist_ok=True)
        mock_file().write.assert_called_once_with(b'File content')
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    @patch.object(SharePointClient, '_simple_upload')
    @patch('os.path.getsize')
    def test_upload_small_file(self, mock_getsize, mock_simple_upload, mock_get_drive, client):
        """Test uploading a small file."""
        mock_get_drive.return_value = 'drive123'
        mock_getsize.return_value = 1024  # 1KB
        
        mock_file = Mock(spec=SharePointFile)
        mock_simple_upload.return_value = mock_file
        
        result = client.upload_file('/local/file.txt', 'Documents/file.txt')
        
        assert result == mock_file
        mock_simple_upload.assert_called_once_with(
            '/local/file.txt',
            'Documents/file.txt',
            'drive123',
            'rename'
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    @patch.object(SharePointClient, '_resumable_upload')
    @patch('os.path.getsize')
    def test_upload_large_file(self, mock_getsize, mock_resumable_upload, mock_get_drive, client):
        """Test uploading a large file."""
        mock_get_drive.return_value = 'drive123'
        mock_getsize.return_value = 5 * 1024 * 1024  # 5MB
        
        mock_file = Mock(spec=SharePointFile)
        mock_resumable_upload.return_value = mock_file
        
        result = client.upload_file('/local/bigfile.txt', 'Documents/bigfile.txt')
        
        assert result == mock_file
        mock_resumable_upload.assert_called_once_with(
            '/local/bigfile.txt',
            'Documents/bigfile.txt',
            'drive123',
            'rename'
        )
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'Small file content')
    def test_simple_upload(self, mock_file, client):
        """Test simple upload method."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'uploaded-file',
            'name': 'file.txt',
            'size': 18,
            'createdDateTime': '2024-01-01T10:00:00Z',
            'lastModifiedDateTime': '2024-01-01T10:00:00Z',
            'webUrl': 'https://sharepoint.com/file.txt'
        }
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client._simple_upload('/local/file.txt', 'Documents/file.txt', 'drive123', 'rename')
        
        assert result.id == 'uploaded-file'
        assert result.name == 'file.txt'
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='PUT',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root:/Documents%2Ffile.txt:/content',
            data=b'Small file content',
            params={'@microsoft.graph.conflictBehavior': 'rename'},
            headers={'Content-Type': 'application/octet-stream'}
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_create_folder(self, mock_get_drive, client):
        """Test creating a folder."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'new-folder',
            'name': 'NewFolder',
            'createdDateTime': '2024-01-01T10:00:00Z',
            'lastModifiedDateTime': '2024-01-01T10:00:00Z',
            'webUrl': 'https://sharepoint.com/NewFolder',
            'folder': {'childCount': 0}
        }
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client.create_folder('NewFolder', parent_path='Documents')
        
        assert result.id == 'new-folder'
        assert result.name == 'NewFolder'
        assert result.child_count == 0
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='POST',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root:/Documents:/children',
            json={
                'name': 'NewFolder',
                'folder': {},
                '@microsoft.graph.conflictBehavior': 'rename'
            }
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_delete_item_success(self, mock_get_drive, client):
        """Test successful deletion of an item."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 204
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client.delete_item('Documents/oldfile.txt')
        
        assert result is True
        client.auth_client.make_graph_request.assert_called_once_with(
            method='DELETE',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root:/Documents%2Foldfile.txt'
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_delete_item_failure(self, mock_get_drive, client):
        """Test failed deletion of an item."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        result = client.delete_item('Documents/nonexistent.txt')
        
        assert result is False
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_search_files(self, mock_get_drive, client):
        """Test searching for files."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {
                    'id': 'file1',
                    'name': 'report.pdf',
                    'size': 5000,
                    'createdDateTime': '2024-01-01T10:00:00Z',
                    'lastModifiedDateTime': '2024-01-01T10:00:00Z',
                    'webUrl': 'https://sharepoint.com/report.pdf',
                    'file': {'mimeType': 'application/pdf'}
                },
                {
                    'id': 'folder1',
                    'name': 'Reports',
                    'createdDateTime': '2024-01-01T10:00:00Z',
                    'lastModifiedDateTime': '2024-01-01T10:00:00Z',
                    'webUrl': 'https://sharepoint.com/Reports',
                    'folder': {'childCount': 5}
                }
            ]
        }
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        results = client.search_files('report')
        
        assert len(results) == 1
        assert results[0].name == 'report.pdf'
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url="https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root/search(q='report')",
            params={'$top': 50}
        )
    
    @patch.object(SharePointClient, 'get_default_drive_id')
    def test_get_file_metadata(self, mock_get_drive, client):
        """Test getting file metadata."""
        mock_get_drive.return_value = 'drive123'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'file-meta',
            'name': 'document.docx',
            'size': 10240,
            'createdDateTime': '2024-01-01T10:00:00Z',
            'lastModifiedDateTime': '2024-01-02T15:00:00Z',
            'webUrl': 'https://sharepoint.com/document.docx',
            'file': {'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        }
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        metadata = client.get_file_metadata('Documents/document.docx')
        
        assert metadata.id == 'file-meta'
        assert metadata.name == 'document.docx'
        assert metadata.size == 10240
        
        client.auth_client.make_graph_request.assert_called_once_with(
            method='GET',
            url='https://graph.microsoft.com/v1.0/sites/test-site-id/drives/drive123/root:/Documents%2Fdocument.docx'
        )


class TestErrorHandling:
    """Test error handling in SharePoint client."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        mock_auth = Mock()
        return SharePointClient(
            site_id="test-site",
            auth_client=mock_auth
        )
    
    def test_list_items_error(self, client):
        """Test error handling in list_drive_items."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = 'Access denied'
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        with pytest.raises(RequestException) as exc_info:
            client.list_drive_items(drive_id='drive123')
        
        assert 'Failed to list items: 403' in str(exc_info.value)
    
    def test_download_file_error(self, client):
        """Test error handling in download_file."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'File not found'
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        with pytest.raises(RequestException) as exc_info:
            client.download_file('nonexistent.txt', drive_id='drive123')
        
        assert 'Failed to get file info: 404' in str(exc_info.value)
    
    def test_upload_file_error(self, client):
        """Test error handling in upload_file."""
        mock_response = Mock()
        mock_response.status_code = 507
        mock_response.text = 'Insufficient storage'
        
        client.auth_client.make_graph_request.return_value = mock_response
        
        with patch('builtins.open', mock_open(read_data=b'content')):
            with patch('os.path.getsize', return_value=100):
                with pytest.raises(RequestException) as exc_info:
                    client._simple_upload('/local/file.txt', 'remote/file.txt', 'drive123', 'rename')
        
        assert 'Failed to upload file: 507' in str(exc_info.value)