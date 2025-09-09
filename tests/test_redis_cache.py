"""
Tests for the Redis caching layer.
"""

import pytest
import pickle
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from cache.redis_cache import (
    CacheManager,
    cache_result,
    get_default_cache
)


class TestCacheManager:
    """Test the CacheManager class."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        mock = Mock(spec=redis.Redis)
        mock.ping.return_value = True
        mock.setex.return_value = True
        mock.get.return_value = None
        mock.delete.return_value = 1
        mock.exists.return_value = 1
        mock.keys.return_value = []
        mock.dbsize.return_value = 0
        mock.info.return_value = {
            'redis_version': '6.2.5',
            'connected_clients': 1,
            'used_memory_human': '1.5M',
            'used_memory_peak_human': '2M',
            'keyspace_hits': 100,
            'keyspace_misses': 20,
            'evicted_keys': 0
        }
        mock.memory_stats.return_value = {}
        return mock
    
    @patch('cache.redis_cache.redis.Redis')
    @patch('cache.redis_cache.redis.ConnectionPool')
    def test_initialization_with_params(self, mock_pool_class, mock_redis_class, mock_redis_client):
        """Test CacheManager initialization with parameters."""
        mock_redis_class.return_value = mock_redis_client
        
        manager = CacheManager(
            host='redis.example.com',
            port=6380,
            db=1,
            password='secret'
        )
        
        assert manager.host == 'redis.example.com'
        assert manager.port == 6380
        assert manager.db == 1
        assert manager.password == 'secret'
        
        # Verify connection pool was created with correct params
        mock_pool_class.assert_called_once()
        call_kwargs = mock_pool_class.call_args[1]
        assert call_kwargs['host'] == 'redis.example.com'
        assert call_kwargs['port'] == 6380
        assert call_kwargs['db'] == 1
        assert call_kwargs['password'] == 'secret'
    
    @patch('cache.redis_cache.redis.from_url')
    def test_initialization_with_connection_string(self, mock_from_url, mock_redis_client):
        """Test CacheManager initialization with connection string."""
        mock_from_url.return_value = mock_redis_client
        
        manager = CacheManager(
            connection_string='redis://user:pass@redis.example.com:6379/0'
        )
        
        mock_from_url.assert_called_once_with(
            'redis://user:pass@redis.example.com:6379/0',
            decode_responses=False,
            socket_timeout=5,
            max_connections=50
        )
    
    @patch('cache.redis_cache.redis.Redis')
    @patch('cache.redis_cache.redis.ConnectionPool')
    def test_connection_failure(self, mock_pool_class, mock_redis_class):
        """Test handling of connection failure."""
        mock_client = Mock()
        mock_client.ping.side_effect = RedisConnectionError("Connection refused")
        mock_redis_class.return_value = mock_client
        
        with pytest.raises(RedisConnectionError):
            CacheManager()
    
    def test_generate_key(self, mock_redis_client):
        """Test cache key generation."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            # Normal key
            key = manager._generate_key('document', 'file.pdf')
            assert key == 'dcri:document:file.pdf'
            
            # Long key (should be hashed)
            long_id = 'a' * 250
            key = manager._generate_key('document', long_id)
            assert key.startswith('dcri:document:')
            assert len(key) < 100  # Hashed to shorter length
    
    def test_set_and_get_string(self, mock_redis_client):
        """Test setting and getting string values."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            # Set string value
            mock_redis_client.setex.return_value = True
            result = manager.set('test_key', 'test_value', ttl=60)
            assert result is True
            
            mock_redis_client.setex.assert_called_with(
                'dcri:general:test_key',
                60,
                'test_value'
            )
            
            # Get string value
            mock_redis_client.get.return_value = b'test_value'
            value = manager.get('test_key')
            assert value == 'test_value'
    
    def test_set_and_get_object(self, mock_redis_client):
        """Test setting and getting object values."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            # Set object value
            test_obj = {'name': 'test', 'value': 123}
            mock_redis_client.setex.return_value = True
            result = manager.set('test_obj', test_obj, ttl=120)
            assert result is True
            
            # Verify object was pickled
            call_args = mock_redis_client.setex.call_args[0]
            assert call_args[0] == 'dcri:general:test_obj'
            assert call_args[1] == 120
            assert pickle.loads(call_args[2]) == test_obj
            
            # Get object value
            mock_redis_client.get.return_value = pickle.dumps(test_obj)
            value = manager.get('test_obj')
            assert value == test_obj
    
    def test_get_with_default(self, mock_redis_client):
        """Test getting with default value."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            mock_redis_client.get.return_value = None
            value = manager.get('nonexistent', default='default_value')
            assert value == 'default_value'
    
    def test_delete(self, mock_redis_client):
        """Test deleting a key."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            mock_redis_client.delete.return_value = 1
            result = manager.delete('test_key')
            assert result is True
            
            mock_redis_client.delete.assert_called_with('dcri:general:test_key')
            
            # Key doesn't exist
            mock_redis_client.delete.return_value = 0
            result = manager.delete('nonexistent')
            assert result is False
    
    def test_exists(self, mock_redis_client):
        """Test checking key existence."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            mock_redis_client.exists.return_value = 1
            result = manager.exists('test_key')
            assert result is True
            
            mock_redis_client.exists.return_value = 0
            result = manager.exists('nonexistent')
            assert result is False
    
    def test_cache_document(self, mock_redis_client):
        """Test caching a document."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            content = b'Document content'
            metadata = {'size': 16, 'type': 'text/plain'}
            
            mock_redis_client.setex.return_value = True
            result = manager.cache_document(
                'documents/test.txt',
                content,
                metadata=metadata
            )
            
            assert result is True
            assert mock_redis_client.setex.call_count == 2
            
            # Verify content was cached
            content_call = mock_redis_client.setex.call_args_list[0]
            assert content_call[0][0] == 'dcri:document:documents/test.txt'
            assert content_call[0][1] == 86400  # DOCUMENT_TTL
            assert content_call[0][2] == content
            
            # Verify metadata was cached
            metadata_call = mock_redis_client.setex.call_args_list[1]
            assert metadata_call[0][0] == 'dcri:metadata:documents/test.txt:metadata'
            assert metadata_call[0][1] == 300  # METADATA_TTL
    
    def test_get_document(self, mock_redis_client):
        """Test getting a cached document."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            content = b'Document content'
            metadata = {'size': 16, 'type': 'text/plain'}
            
            # Mock getting content and metadata
            mock_redis_client.get.side_effect = [
                content,
                pickle.dumps(metadata)
            ]
            
            retrieved_content, retrieved_metadata = manager.get_document('documents/test.txt')
            
            assert retrieved_content == content
            assert retrieved_metadata == metadata
            
            # Verify correct keys were used
            calls = mock_redis_client.get.call_args_list
            assert calls[0][0][0] == 'dcri:document:documents/test.txt'
            assert calls[1][0][0] == 'dcri:metadata:documents/test.txt:metadata'
    
    def test_cache_api_response(self, mock_redis_client):
        """Test caching API response."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            response = {'data': [1, 2, 3], 'status': 'ok'}
            params = {'page': 1, 'limit': 10}
            
            mock_redis_client.setex.return_value = True
            result = manager.cache_api_response(
                '/api/items',
                params,
                response,
                ttl=300
            )
            
            assert result is True
            
            # Verify cache key includes params
            call_args = mock_redis_client.setex.call_args[0]
            assert 'dcri:api:/api/items:{"limit": 10, "page": 1}' in call_args[0]
    
    def test_get_api_response(self, mock_redis_client):
        """Test getting cached API response."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            response = {'data': [1, 2, 3], 'status': 'ok'}
            params = {'page': 1, 'limit': 10}
            
            mock_redis_client.get.return_value = pickle.dumps(response)
            
            cached = manager.get_api_response('/api/items', params)
            assert cached == response
    
    def test_clear_namespace(self, mock_redis_client):
        """Test clearing a namespace."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            # Mock keys in namespace
            mock_redis_client.keys.return_value = [
                b'dcri:document:file1',
                b'dcri:document:file2',
                b'dcri:document:file3'
            ]
            mock_redis_client.delete.return_value = 3
            
            deleted = manager.clear_namespace('document')
            
            assert deleted == 3
            mock_redis_client.keys.assert_called_with('dcri:document:*')
            mock_redis_client.delete.assert_called_with(
                b'dcri:document:file1',
                b'dcri:document:file2',
                b'dcri:document:file3'
            )
    
    def test_get_stats(self, mock_redis_client):
        """Test getting cache statistics."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            mock_redis_client.dbsize.return_value = 42
            mock_redis_client.keys.side_effect = [
                ['key1', 'key2'],  # general
                ['doc1', 'doc2', 'doc3'],  # document
                ['meta1'],  # metadata
                []  # api
            ]
            
            stats = manager.get_stats()
            
            assert stats['connected'] is True
            assert stats['server_version'] == '6.2.5'
            assert stats['total_keys'] == 42
            assert stats['keys_by_namespace']['general'] == 2
            assert stats['keys_by_namespace']['document'] == 3
            assert stats['keys_by_namespace']['metadata'] == 1
            assert stats['keys_by_namespace']['api'] == 0
            assert stats['hit_rate'] == pytest.approx(83.33, rel=0.01)
    
    def test_context_manager(self, mock_redis_client):
        """Test using CacheManager as context manager."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            with CacheManager() as manager:
                assert manager.client == mock_redis_client
            
            mock_redis_client.close.assert_called_once()
    
    def test_error_handling(self, mock_redis_client):
        """Test error handling in cache operations."""
        with patch('cache.redis_cache.redis.Redis', return_value=mock_redis_client):
            manager = CacheManager()
            
            # Simulate Redis error
            mock_redis_client.setex.side_effect = RedisError("Redis error")
            result = manager.set('key', 'value')
            assert result is False
            
            mock_redis_client.get.side_effect = RedisError("Redis error")
            result = manager.get('key', default='default')
            assert result == 'default'
            
            mock_redis_client.delete.side_effect = RedisError("Redis error")
            result = manager.delete('key')
            assert result is False


class TestCacheDecorator:
    """Test the cache_result decorator."""
    
    @patch('cache.redis_cache.get_default_cache')
    def test_cache_result_decorator(self, mock_get_cache):
        """Test caching function results with decorator."""
        mock_cache = Mock(spec=CacheManager)
        mock_get_cache.return_value = mock_cache
        
        # First call - cache miss
        mock_cache.get.return_value = None
        
        @cache_result(ttl=60, namespace='test')
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        assert result == 5
        
        # Verify cache was checked and result was cached
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        set_call = mock_cache.set.call_args
        assert set_call[0][1] == 5  # Result
        assert set_call[1]['ttl'] == 60
        assert set_call[1]['namespace'] == 'test'
        
        # Second call - cache hit
        mock_cache.get.return_value = 5
        mock_cache.set.reset_mock()
        
        result = test_function(2, 3)
        assert result == 5
        
        # Verify result came from cache
        mock_cache.set.assert_not_called()
    
    @patch('cache.redis_cache.get_default_cache')
    def test_cache_decorator_no_redis(self, mock_get_cache):
        """Test decorator when Redis is not available."""
        mock_get_cache.return_value = None
        
        @cache_result()
        def test_function(x):
            return x * 2
        
        result = test_function(5)
        assert result == 10  # Function still works without cache


class TestModuleFunctions:
    """Test module-level functions."""
    
    @patch('cache.redis_cache.CacheManager')
    def test_get_default_cache(self, mock_manager_class):
        """Test getting default cache instance."""
        import cache.redis_cache
        cache.redis_cache._default_cache = None
        
        mock_instance = Mock(spec=CacheManager)
        mock_manager_class.return_value = mock_instance
        
        # First call creates instance
        cache1 = get_default_cache()
        assert cache1 == mock_instance
        mock_manager_class.assert_called_once()
        
        # Second call returns same instance
        cache2 = get_default_cache()
        assert cache2 == cache1
        assert mock_manager_class.call_count == 1
        
        # Clean up
        cache.redis_cache._default_cache = None
    
    @patch('cache.redis_cache.CacheManager')
    def test_get_default_cache_connection_error(self, mock_manager_class):
        """Test handling connection error in default cache."""
        import cache.redis_cache
        cache.redis_cache._default_cache = None
        
        mock_manager_class.side_effect = RedisConnectionError("Connection failed")
        
        result = get_default_cache()
        assert result is None
        
        # Clean up
        cache.redis_cache._default_cache = None