"""Retry handler dengan exponential backoff untuk network operations"""
import time
import logging
import random

logger = logging.getLogger(__name__)


class RetryHandler:
    """Retry logic dengan exponential backoff dan jitter."""
    
    def __init__(self, max_retries=3, initial_delay=0.5, max_delay=10, exponential_base=2):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def execute(self, func, *args, **kwargs):
        """Execute function dengan retry logic."""
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
                    delay = self.initial_delay * (self.exponential_base ** attempt)
                    delay = min(delay, self.max_delay)
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    delay = max(0, delay + jitter)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} gagal: {str(e)}. Retry dalam {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Semua {self.max_retries + 1} attempts gagal. Last error: {str(e)}"
                    )
        
        raise last_exception if last_exception else Exception("Unknown error")
