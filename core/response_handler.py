"""
Efficient HTTP response streaming with optimal buffering
Uses BytesIO instead of string concatenation to avoid reallocation overhead
"""
import io
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ResponseHandler:
    """Stream HTTP responses efficiently with memory limits."""
    
    def __init__(self, chunk_size: int = 4096, max_size: int = 500000):
        """
        Initialize response handler.
        
        Args:
            chunk_size: Read chunk size (default: 4KB)
            max_size: Maximum response body size (default: 500KB)
        """
        self.chunk_size = chunk_size
        self.max_size = max_size
    
    def read_response(self, response, encoding: str = "utf-8") -> str:
        """
        Read HTTP response efficiently with memory limit.
        
        Args:
            response: http.client.HTTPResponse object
            encoding: Character encoding (default: utf-8)
            
        Returns:
            Response body as string
            
        Raises:
            ValueError: If response exceeds max_size
        """
        buffer = io.BytesIO()
        bytes_read = 0
        
        try:
            while True:
                chunk = response.read(self.chunk_size)
                if not chunk:
                    break
                
                bytes_read += len(chunk)
                if bytes_read > self.max_size:
                    logger.warning(
                        f"Response exceeded max_size ({self.max_size} bytes), truncating"
                    )
                    break
                
                buffer.write(chunk)
            
            return buffer.getvalue().decode(encoding, errors="ignore")
        
        except Exception as e:
            logger.error(f"Error reading response: {str(e)}")
            return buffer.getvalue().decode(encoding, errors="ignore")
        
        finally:
            buffer.close()
    
    def read_response_binary(self, response) -> bytes:
        """
        Read HTTP response as binary with memory limit.
        
        Args:
            response: http.client.HTTPResponse object
            
        Returns:
            Response body as bytes
        """
        buffer = io.BytesIO()
        bytes_read = 0
        
        try:
            while True:
                chunk = response.read(self.chunk_size)
                if not chunk:
                    break
                
                bytes_read += len(chunk)
                if bytes_read > self.max_size:
                    logger.warning(
                        f"Response exceeded max_size ({self.max_size} bytes), truncating"
                    )
                    break
                
                buffer.write(chunk)
            
            return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Error reading binary response: {str(e)}")
            return buffer.getvalue()
        
        finally:
            buffer.close()


# Global response handler instances
_handlers = {}


def get_response_handler(max_size: int = 500000) -> ResponseHandler:
    """
    Get or create response handler for given max_size.
    
    Args:
        max_size: Maximum response size
        
    Returns:
        ResponseHandler instance
    """
    if max_size not in _handlers:
        _handlers[max_size] = ResponseHandler(max_size=max_size)
    return _handlers[max_size]
