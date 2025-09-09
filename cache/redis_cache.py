"""
Redis caching layer for DCRI MCP Tools.

Provides caching functionality for frequently accessed documents from SharePoint
and other data sources to improve performance and reduce API calls.
"""

import os
import json
import pickle
import hashlib
import logging
from typing import Optional, Any, Union, Dict
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis cache manager for document and data caching.
    
    Provides methods for caching SharePoint documents, API responses,
    and other frequently accessed data with TTL support.
    """
    
    DEFAULT_TTL = 3600  # 1 hour default TTL
    DOCUMENT_TTL = 86400  # 24 hours for documents
    METADATA_TTL = 300  # 5 minutes for metadata
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
        decode_responses: bool = False,
        socket_timeout: int = 5,
        max_connections: int = 50
    ):
        """
        Initialize the Redis cache manager.
        
        Args:
            host: Redis host (defaults to env var REDIS_HOST or localhost)
            port: Redis port (defaults to env var REDIS_PORT or 6379)
            db: Redis database number (defaults to env var REDIS_DB or 0)
            password: Redis password (defaults to env var REDIS_PASSWORD)
            connection_string: Full Redis connection string (overrides other params)
            decode_responses: Whether to decode responses to strings
            socket_timeout: Socket timeout in seconds
            max_connections: Maximum number of connections in pool
        """
        # Use connection string if provided
        if connection_string or os.getenv('REDIS_CONNECTION_STRING'):
            conn_str = connection_string or os.getenv('REDIS_CONNECTION_STRING')
            self.client = redis.from_url(
                conn_str,
                decode_responses=decode_responses,
                socket_timeout=socket_timeout,
                max_connections=max_connections
            )
        else:
            # Use individual parameters
            self.host = host or os.getenv('REDIS_HOST', 'localhost')
            self.port = int(port or os.getenv('REDIS_PORT', 6379))
            self.db = int(db or os.getenv('REDIS_DB', 0))
            self.password = password or os.getenv('REDIS_PASSWORD')
            
            # Create connection pool
            pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_timeout=socket_timeout,
                max_connections=max_connections
            )
            
            self.client = redis.Redis(connection_pool=pool)
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection."""
        try:
            self.client.ping()
            logger.info("Successfully connected to Redis")
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate a cache key.
        
        Args:
            namespace: Cache namespace (e.g., 'document', 'metadata')
            identifier: Unique identifier for the cached item
            
        Returns:
            Cache key string
        """
        # Create a hash for very long identifiers
        if len(identifier) > 200:
            identifier = hashlib.sha256(identifier.encode()).hexdigest()
        
        return f"dcri:{namespace}:{identifier}"
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "general"
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be serialized)
            ttl: Time to live in seconds (defaults to DEFAULT_TTL)
            namespace: Cache namespace
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_key(namespace, key)
        ttl = ttl or self.DEFAULT_TTL
        
        try:
            # Serialize the value
            if isinstance(value, (str, bytes)):
                serialized = value
            else:
                serialized = pickle.dumps(value)
            
            # Set with TTL
            result = self.client.setex(cache_key, ttl, serialized)
            
            logger.debug(f"Cached {cache_key} with TTL {ttl}s")
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Failed to cache {cache_key}: {e}")
            return False
    
    def get(
        self,
        key: str,
        namespace: str = "general",
        default: Any = None
    ) -> Any:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            namespace: Cache namespace
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        cache_key = self._generate_key(namespace, key)
        
        try:
            value = self.client.get(cache_key)
            
            if value is None:
                logger.debug(f"Cache miss for {cache_key}")
                return default
            
            # Deserialize if needed
            try:
                deserialized = pickle.loads(value)
                logger.debug(f"Cache hit for {cache_key}")
                return deserialized
            except (pickle.PickleError, TypeError):
                # Return raw bytes for document namespace, decode for others
                logger.debug(f"Cache hit for {cache_key}")
                if namespace == "document":
                    return value  # Keep as bytes for document content
                return value.decode('utf-8') if isinstance(value, bytes) else value
                
        except RedisError as e:
            logger.error(f"Failed to get {cache_key}: {e}")
            return default
    
    def delete(self, key: str, namespace: str = "general") -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            namespace: Cache namespace
            
        Returns:
            True if key was deleted, False otherwise
        """
        cache_key = self._generate_key(namespace, key)
        
        try:
            result = self.client.delete(cache_key)
            logger.debug(f"Deleted {cache_key} from cache")
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Failed to delete {cache_key}: {e}")
            return False
    
    def exists(self, key: str, namespace: str = "general") -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            namespace: Cache namespace
            
        Returns:
            True if key exists, False otherwise
        """
        cache_key = self._generate_key(namespace, key)
        
        try:
            return bool(self.client.exists(cache_key))
        except RedisError as e:
            logger.error(f"Failed to check existence of {cache_key}: {e}")
            return False
    
    def cache_document(
        self,
        document_path: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache a document with its metadata.
        
        Args:
            document_path: Document path/identifier
            content: Document content as bytes
            metadata: Optional document metadata
            ttl: Time to live (defaults to DOCUMENT_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        ttl = ttl or self.DOCUMENT_TTL
        
        # Cache content
        content_cached = self.set(
            key=document_path,
            value=content,
            ttl=ttl,
            namespace="document"
        )
        
        # Cache metadata if provided
        metadata_cached = True
        if metadata:
            metadata_cached = self.set(
                key=f"{document_path}:metadata",
                value=metadata,
                ttl=self.METADATA_TTL,
                namespace="metadata"
            )
        
        return content_cached and metadata_cached
    
    def get_document(
        self,
        document_path: str
    ) -> tuple[Optional[bytes], Optional[Dict[str, Any]]]:
        """
        Get a cached document with its metadata.
        
        Args:
            document_path: Document path/identifier
            
        Returns:
            Tuple of (content, metadata) or (None, None) if not found
        """
        content = self.get(document_path, namespace="document")
        metadata = self.get(f"{document_path}:metadata", namespace="metadata")
        
        return content, metadata
    
    def cache_api_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        response: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache an API response.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            response: Response data
            ttl: Time to live (defaults to DEFAULT_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        # Create cache key from endpoint and params
        params_str = json.dumps(params, sort_keys=True) if params else ""
        cache_key = f"{endpoint}:{params_str}"
        
        return self.set(
            key=cache_key,
            value=response,
            ttl=ttl or self.DEFAULT_TTL,
            namespace="api"
        )
    
    def get_api_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Get a cached API response.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Cached response or None
        """
        params_str = json.dumps(params, sort_keys=True) if params else ""
        cache_key = f"{endpoint}:{params_str}"
        
        return self.get(cache_key, namespace="api")
    
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Cache namespace to clear
            
        Returns:
            Number of keys deleted
        """
        pattern = f"dcri:{namespace}:*"
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys from namespace '{namespace}'")
                return deleted
            return 0
            
        except RedisError as e:
            logger.error(f"Failed to clear namespace '{namespace}': {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            info = self.client.info()
            memory_info = self.client.memory_stats()
            
            # Count keys by namespace
            namespaces = ['general', 'document', 'metadata', 'api']
            key_counts = {}
            
            for ns in namespaces:
                pattern = f"dcri:{ns}:*"
                key_counts[ns] = len(self.client.keys(pattern))
            
            return {
                'connected': True,
                'server_version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'used_memory_peak_human': info.get('used_memory_peak_human'),
                'total_keys': self.client.dbsize(),
                'keys_by_namespace': key_counts,
                'hit_rate': self._calculate_hit_rate(info),
                'evicted_keys': info.get('evicted_keys', 0)
            }
            
        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'connected': False, 'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> Optional[float]:
        """
        Calculate cache hit rate.
        
        Args:
            info: Redis info dictionary
            
        Returns:
            Hit rate as percentage or None
        """
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        total = hits + misses
        if total == 0:
            return None
            
        return (hits / total) * 100
    
    def close(self):
        """Close Redis connection."""
        try:
            self.client.close()
            logger.info("Closed Redis connection")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Decorator for caching function results
def cache_result(ttl: int = 3600, namespace: str = "function"):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        namespace: Cache namespace
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cache_manager = get_default_cache()
            if cache_manager:
                cached = cache_manager.get(cache_key, namespace=namespace)
                if cached is not None:
                    return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            if cache_manager and result is not None:
                cache_manager.set(cache_key, result, ttl=ttl, namespace=namespace)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_default_cache: Optional[CacheManager] = None


def get_default_cache() -> Optional[CacheManager]:
    """
    Get or create the default cache manager.
    
    Returns:
        CacheManager instance or None if Redis is not available
    """
    global _default_cache
    
    if _default_cache is None:
        try:
            _default_cache = CacheManager()
        except (RedisConnectionError, RedisError) as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
            return None
    
    return _default_cache