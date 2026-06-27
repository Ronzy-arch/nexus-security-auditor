"""
HTTP Connection Pool Manager untuk optimisasi performa
Menyediakan koneksi reusable dengan keep-alive dan pooling
"""
import http.client
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class HTTPConnectionPool:
    """
    Connection pool untuk HTTP requests dengan reuse connections
    dan automatic cleanup.
    """
    
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.connections = {}
    
    def _get_host_key(self, host, port=80):
        """Generate unique key untuk host:port"""
        return f"{host}:{port}"
    
    def get_connection(self, host, port=80, timeout=5.0):
        """
        Get atau create HTTP connection ke host:port.
        Reuse existing connection jika available.
        """
        key = self._get_host_key(host, port)
        
        try:
            # Coba reuse existing connection
            if key in self.connections:
                conn = self.connections[key]
                # Test jika connection masih valid
                try:
                    conn.request("HEAD", "/", timeout=timeout)
                    response = conn.getresponse()
                    response.read()
                    return conn
                except:
                    # Connection dead, buat baru
                    del self.connections[key]
            
            # Create new connection
            conn = http.client.HTTPConnection(host, port=port, timeout=timeout)
            self.connections[key] = conn
            return conn
        except Exception as e:
            logger.error(f"Failed to get connection for {key}: {str(e)}")
            # Fallback: create new connection yang tidak di-pool
            return http.client.HTTPConnection(host, port=port, timeout=timeout)
    
    def close_all(self):
        """Close semua koneksi dalam pool"""
        for key, conn in self.connections.items():
            try:
                conn.close()
            except:
                pass
        self.connections.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()


# Global pool instance
_global_pool = None


def get_http_pool():
    """Get atau create global HTTP connection pool"""
    global _global_pool
    if _global_pool is None:
        _global_pool = HTTPConnectionPool(pool_size=10)
    return _global_pool


def close_http_pool():
    """Close global pool"""
    global _global_pool
    if _global_pool is not None:
        _global_pool.close_all()
        _global_pool = None
