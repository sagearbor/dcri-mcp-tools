"""
SharePoint client module for DCRI MCP Tools.

This module provides functionality to interact with SharePoint Online
using the Microsoft Graph API for document management operations.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, BinaryIO, Union
from urllib.parse import quote, urljoin, quote as url_quote
from dataclasses import dataclass
from datetime import datetime
import requests
from requests.exceptions import RequestException

from auth.graph_auth import GraphAuthClient

logger = logging.getLogger(__name__)


@dataclass
class SharePointFile:
    """Container for SharePoint file information."""
    id: str
    name: str
    size: int
    created_datetime: datetime
    last_modified_datetime: datetime
    web_url: str
    download_url: Optional[str] = None
    mime_type: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    parent_path: Optional[str] = None


@dataclass
class SharePointFolder:
    """Container for SharePoint folder information."""
    id: str
    name: str
    created_datetime: datetime
    last_modified_datetime: datetime
    web_url: str
    child_count: int = 0
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    parent_path: Optional[str] = None


class SharePointClient:
    """
    SharePoint Online client using Microsoft Graph API.
    
    Provides methods for listing, downloading, uploading, and managing
    files and folders in SharePoint document libraries.
    """
    
    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
    MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB for simple upload
    
    def __init__(
        self,
        site_id: Optional[str] = None,
        auth_client: Optional[GraphAuthClient] = None,
        site_url: Optional[str] = None
    ):
        """
        Initialize the SharePoint client.
        
        Args:
            site_id: SharePoint site ID (defaults to env var SHAREPOINT_SITE_ID)
            auth_client: GraphAuthClient instance (creates new if not provided)
            site_url: SharePoint site URL (alternative to site_id)
        """
        self.auth_client = auth_client or GraphAuthClient()
        self.site_id = site_id or os.getenv('SHAREPOINT_SITE_ID')
        self.site_url = site_url or os.getenv('SHAREPOINT_SITE_URL')
        
        if not self.site_id and not self.site_url:
            raise ValueError(
                "Either site_id or site_url must be provided as parameter "
                "or environment variable (SHAREPOINT_SITE_ID or SHAREPOINT_SITE_URL)"
            )
        
        # If we have site_url but not site_id, we'll fetch it
        if not self.site_id and self.site_url:
            self.site_id = self._get_site_id_from_url(self.site_url)
    
    def _get_site_id_from_url(self, site_url: str) -> str:
        """
        Get site ID from SharePoint site URL.
        
        Args:
            site_url: Full SharePoint site URL
            
        Returns:
            Site ID string
        """
        # Parse the URL to get hostname and site path
        from urllib.parse import urlparse
        parsed = urlparse(site_url)
        hostname = parsed.hostname
        site_path = parsed.path
        
        # Construct the Graph API URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{hostname}:{site_path}"
        
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to get site ID: {response.status_code} - {response.text}")
        
        data = response.json()
        return data['id']
    
    def _parse_file_item(self, item: Dict[str, Any]) -> SharePointFile:
        """Parse a file item from Graph API response."""
        return SharePointFile(
            id=item['id'],
            name=item['name'],
            size=item.get('size', 0),
            created_datetime=datetime.fromisoformat(item['createdDateTime'].replace('Z', '+00:00')),
            last_modified_datetime=datetime.fromisoformat(item['lastModifiedDateTime'].replace('Z', '+00:00')),
            web_url=item.get('webUrl', ''),
            download_url=item.get('@microsoft.graph.downloadUrl'),
            mime_type=item.get('file', {}).get('mimeType'),
            created_by=item.get('createdBy', {}).get('user', {}).get('displayName'),
            modified_by=item.get('lastModifiedBy', {}).get('user', {}).get('displayName'),
            parent_path=item.get('parentReference', {}).get('path')
        )
    
    def _parse_folder_item(self, item: Dict[str, Any]) -> SharePointFolder:
        """Parse a folder item from Graph API response."""
        return SharePointFolder(
            id=item['id'],
            name=item['name'],
            created_datetime=datetime.fromisoformat(item['createdDateTime'].replace('Z', '+00:00')),
            last_modified_datetime=datetime.fromisoformat(item['lastModifiedDateTime'].replace('Z', '+00:00')),
            web_url=item.get('webUrl', ''),
            child_count=item.get('folder', {}).get('childCount', 0),
            created_by=item.get('createdBy', {}).get('user', {}).get('displayName'),
            modified_by=item.get('lastModifiedBy', {}).get('user', {}).get('displayName'),
            parent_path=item.get('parentReference', {}).get('path')
        )
    
    def list_drive_items(
        self, 
        folder_path: Optional[str] = None,
        drive_id: Optional[str] = None
    ) -> Dict[str, List[Union[SharePointFile, SharePointFolder]]]:
        """
        List files and folders in a SharePoint document library.
        
        Args:
            folder_path: Path to folder (None for root)
            drive_id: Drive ID (defaults to site's default drive)
            
        Returns:
            Dictionary with 'files' and 'folders' lists
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Construct API URL
        if folder_path:
            # Encode the folder path
            encoded_path = quote(folder_path, safe='')
            api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root/children"
        
        # Make request
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url,
            params={'$expand': 'thumbnails', '$top': 1000}
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to list items: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Parse items
        files = []
        folders = []
        
        for item in data.get('value', []):
            if 'file' in item:
                files.append(self._parse_file_item(item))
            elif 'folder' in item:
                folders.append(self._parse_folder_item(item))
        
        return {
            'files': files,
            'folders': folders
        }
    
    def get_default_drive_id(self) -> str:
        """
        Get the default document library drive ID for the site.
        
        Returns:
            Drive ID string
        """
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drive"
        
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to get default drive: {response.status_code} - {response.text}")
        
        data = response.json()
        return data['id']
    
    def download_file(
        self,
        file_path: str,
        drive_id: Optional[str] = None,
        local_path: Optional[str] = None
    ) -> Union[bytes, str]:
        """
        Download a file from SharePoint.
        
        Args:
            file_path: Path to file in SharePoint
            drive_id: Drive ID (defaults to site's default drive)
            local_path: Local path to save file (if None, returns content)
            
        Returns:
            File content as bytes if local_path is None, 
            otherwise the local file path
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Encode the file path
        encoded_path = quote(file_path, safe='')
        
        # Get file metadata with download URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}"
        
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to get file info: {response.status_code} - {response.text}")
        
        data = response.json()
        download_url = data.get('@microsoft.graph.downloadUrl')
        
        if not download_url:
            # Try alternate method
            content_url = f"{api_url}/content"
            response = self.auth_client.make_graph_request(
                method='GET',
                url=content_url
            )
        else:
            # Download from the download URL (doesn't need auth)
            response = requests.get(download_url)
        
        if response.status_code != 200:
            raise RequestException(f"Failed to download file: {response.status_code}")
        
        content = response.content
        
        if local_path:
            # Save to local file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(content)
            logger.info(f"File downloaded to {local_path}")
            return local_path
        else:
            return content
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        drive_id: Optional[str] = None,
        conflict_behavior: str = 'rename'
    ) -> SharePointFile:
        """
        Upload a file to SharePoint.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in SharePoint
            drive_id: Drive ID (defaults to site's default drive)
            conflict_behavior: 'rename', 'replace', or 'fail'
            
        Returns:
            SharePointFile object for uploaded file
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Get file size
        file_size = os.path.getsize(local_path)
        
        if file_size <= self.MAX_FILE_SIZE:
            return self._simple_upload(local_path, remote_path, drive_id, conflict_behavior)
        else:
            return self._resumable_upload(local_path, remote_path, drive_id, conflict_behavior)
    
    def _simple_upload(
        self,
        local_path: str,
        remote_path: str,
        drive_id: str,
        conflict_behavior: str
    ) -> SharePointFile:
        """Simple upload for small files (<4MB)."""
        # Read file content
        with open(local_path, 'rb') as f:
            content = f.read()
        
        # Encode the remote path
        encoded_path = quote(remote_path, safe='')
        
        # Construct API URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}:/content"
        
        # Add conflict behavior parameter
        params = {}
        if conflict_behavior == 'rename':
            params['@microsoft.graph.conflictBehavior'] = 'rename'
        elif conflict_behavior == 'replace':
            params['@microsoft.graph.conflictBehavior'] = 'replace'
        elif conflict_behavior == 'fail':
            params['@microsoft.graph.conflictBehavior'] = 'fail'
        
        # Upload file
        response = self.auth_client.make_graph_request(
            method='PUT',
            url=api_url,
            data=content,
            params=params,
            headers={'Content-Type': 'application/octet-stream'}
        )
        
        if response.status_code not in [200, 201]:
            raise RequestException(f"Failed to upload file: {response.status_code} - {response.text}")
        
        data = response.json()
        return self._parse_file_item(data)
    
    def _resumable_upload(
        self,
        local_path: str,
        remote_path: str,
        drive_id: str,
        conflict_behavior: str
    ) -> SharePointFile:
        """Resumable upload for large files (>4MB)."""
        # Create upload session
        encoded_path = quote(remote_path, safe='')
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}:/createUploadSession"
        
        session_data = {
            'item': {
                '@microsoft.graph.conflictBehavior': conflict_behavior
            }
        }
        
        response = self.auth_client.make_graph_request(
            method='POST',
            url=api_url,
            json=session_data
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to create upload session: {response.status_code} - {response.text}")
        
        session = response.json()
        upload_url = session['uploadUrl']
        
        # Upload file in chunks
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        file_size = os.path.getsize(local_path)
        
        with open(local_path, 'rb') as f:
            start = 0
            while start < file_size:
                # Read chunk
                chunk = f.read(chunk_size)
                end = min(start + len(chunk), file_size)
                
                # Upload chunk
                headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {start}-{end-1}/{file_size}'
                }
                
                response = requests.put(
                    upload_url,
                    data=chunk,
                    headers=headers
                )
                
                if response.status_code not in [200, 201, 202]:
                    raise RequestException(f"Failed to upload chunk: {response.status_code} - {response.text}")
                
                start = end
                
                # Log progress
                progress = (start / file_size) * 100
                logger.info(f"Upload progress: {progress:.1f}%")
        
        # Parse final response
        data = response.json()
        return self._parse_file_item(data)
    
    def create_folder(
        self,
        folder_name: str,
        parent_path: Optional[str] = None,
        drive_id: Optional[str] = None
    ) -> SharePointFolder:
        """
        Create a folder in SharePoint.
        
        Args:
            folder_name: Name of the folder to create
            parent_path: Parent folder path (None for root)
            drive_id: Drive ID (defaults to site's default drive)
            
        Returns:
            SharePointFolder object for created folder
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Construct API URL
        if parent_path:
            encoded_path = quote(parent_path, safe='')
            api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root/children"
        
        # Create folder request
        folder_data = {
            'name': folder_name,
            'folder': {},
            '@microsoft.graph.conflictBehavior': 'rename'
        }
        
        response = self.auth_client.make_graph_request(
            method='POST',
            url=api_url,
            json=folder_data
        )
        
        if response.status_code not in [200, 201]:
            raise RequestException(f"Failed to create folder: {response.status_code} - {response.text}")
        
        data = response.json()
        return self._parse_folder_item(data)
    
    def delete_item(
        self,
        item_path: str,
        drive_id: Optional[str] = None
    ) -> bool:
        """
        Delete a file or folder from SharePoint.
        
        Args:
            item_path: Path to item to delete
            drive_id: Drive ID (defaults to site's default drive)
            
        Returns:
            True if deletion was successful
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Encode the item path
        encoded_path = quote(item_path, safe='')
        
        # Construct API URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}"
        
        response = self.auth_client.make_graph_request(
            method='DELETE',
            url=api_url
        )
        
        if response.status_code == 204:
            logger.info(f"Successfully deleted: {item_path}")
            return True
        else:
            logger.error(f"Failed to delete item: {response.status_code} - {response.text}")
            return False
    
    def search_files(
        self,
        query: str,
        drive_id: Optional[str] = None,
        limit: int = 50
    ) -> List[SharePointFile]:
        """
        Search for files in SharePoint.
        
        Args:
            query: Search query string
            drive_id: Drive ID (defaults to site's default drive)
            limit: Maximum number of results
            
        Returns:
            List of SharePointFile objects
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Construct API URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root/search(q='{quote(query, safe='')}')"
        
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url,
            params={'$top': limit}
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to search files: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Parse results
        files = []
        for item in data.get('value', []):
            if 'file' in item:
                files.append(self._parse_file_item(item))
        
        return files
    
    def get_file_metadata(
        self,
        file_path: str,
        drive_id: Optional[str] = None
    ) -> SharePointFile:
        """
        Get metadata for a specific file.
        
        Args:
            file_path: Path to file in SharePoint
            drive_id: Drive ID (defaults to site's default drive)
            
        Returns:
            SharePointFile object
        """
        # Get drive ID if not provided
        if not drive_id:
            drive_id = self.get_default_drive_id()
        
        # Encode the file path
        encoded_path = quote(file_path, safe='')
        
        # Construct API URL
        api_url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives/{drive_id}/root:/{encoded_path}"
        
        response = self.auth_client.make_graph_request(
            method='GET',
            url=api_url
        )
        
        if response.status_code != 200:
            raise RequestException(f"Failed to get file metadata: {response.status_code} - {response.text}")
        
        data = response.json()
        return self._parse_file_item(data)