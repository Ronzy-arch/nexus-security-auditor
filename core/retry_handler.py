"""
Retry handler dengan exponential backoff untuk network operations
"""
import time
import logging
import random

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Retry logic dengan exponential backoff dan jitter.
    
    Attributes:
        max_retries: Maximum jumlah retry attempts
        initial_delay: Initial delay dalam seconds (default: 0.5)
        max_delay: Maximum delay dalam seconds (default: 10)
        exponential_base: Base untuk exponential backoff (default: 2)
    """
    
    def __init__(self, max_retries=3, initial_delay=0.5, max_delay=10, exponential_base=2):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def execute(self, func, *args, **kwargs):
        """
        Execute function dengan retry logic.
        
        Args:
            func: Function untuk dijalankan
            *args: Positional arguments untuk func
            **kwargs: Keyword arguments untuk func
        
        Returns:
            Result dari func jika sukses
        
        Raises:
            Exception: Jika semua retry gagal
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Sukses pada attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate delay dengan exponential backoff + jitter
                    delay = self.initial_delay * (self.exponential_base ** attempt)
                    delay = min(delay, self.max_delay)
                    # Add jitter: ±25% dari delay
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    delay = max(0, delay + jitter)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} gagal: {str(e)}. "
                        f"Retry dalam {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Semua {self.max_retries + 1} attempts gagal. "
                        f"Last error: {str(e)}"
                    )
        
        raise last_exception if last_exception else Exception("Unknown error")
    
    def execute_async_safe(self, func, *args, **kwargs):
        """
        Execute function dengan retry, handle sync/async safely.
        """
        return self.execute(func, *args, **kwargs)


# Convenience decorator
def with_retry(max_retries=3, initial_delay=0.5):
    """Decorator untuk retry logic"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = RetryHandler(max_retries=max_retries, initial_delay=initial_delay)
            return handler.execute(func, *args, **kwargs)
        return wrapper
    return decorator
