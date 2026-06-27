"""
DNS Resolution Cache untuk optimisasi performa
Mencegah DNS lookup berulang untuk hostname yang sama
"""
import socket
import threading
import time
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class DNSCache:
    """
    Thread-safe DNS resolution cache dengan TTL support.
    Default TTL: 300 seconds (5 menit)
    """
    
    def __init__(self, ttl=300, max_size=1000):
        self.ttl = ttl
        self.max_size = max_size
        self.cache = {}
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def resolve(self, hostname):
        """
        Resolve hostname dengan cache.
        Return: IP address (str) atau None jika gagal
        """
        # Quick check tanpa lock untuk read performance
        if hostname in self.cache:
            ip, timestamp = self.cache[hostname]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                logger.debug(f"DNS cache hit: {hostname} -> {ip}")
                return ip
        
        # Cache miss atau expired, lakukan resolve
        try:
            with self.lock:
                # Double-check setelah acquire lock
                if hostname in self.cache:
                    ip, timestamp = self.cache[hostname]
                    if time.time() - timestamp < self.ttl:
                        self.hits += 1
                        return ip
                
                # Resolve
                ip = socket.gethostbyname(hostname)
                
                # Store dengan timestamp
                if len(self.cache) >= self.max_size:
                    # Simple eviction: remove oldest entry
                    oldest_key = min(self.cache.keys(), 
                                   key=lambda k: self.cache[k][1])
                    del self.cache[oldest_key]
                
                self.cache[hostname] = (ip, time.time())
                self.misses += 1
                logger.debug(f"DNS cache miss (resolved): {hostname} -> {ip}")
                return ip
        except socket.gaierror as e:
            logger.warning(f"DNS resolution failed for {hostname}: {str(e)}")
            self.misses += 1
            return None
        except Exception as e:
            logger.error(f"DNS cache error: {str(e)}")
            self.misses += 1
            return None
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def stats(self):
        """Return cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_queries": total
        }


# Global DNS cache instance
_global_dns_cache = None


def get_dns_cache():
    """Get atau create global DNS cache"""
    global _global_dns_cache
    if _global_dns_cache is None:
        _global_dns_cache = DNSCache(ttl=300, max_size=1000)
    return _global_dns_cache


def resolve_hostname(hostname):
    """Convenience function untuk resolve dengan cache"""
    cache = get_dns_cache()
    return cache.resolve(hostname)
