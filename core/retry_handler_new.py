"""
Retry handler with exponential backoff, jitter, and timeout enforcement
Adds connection limits and function-level timeout support
"""
import time
import logging
import random
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Retry logic with exponential backoff, jitter, and configurable timeouts.
    
    Features:
    - Exponential backoff with configurable base
    - Random jitter to prevent thundering herd
    - Function-level timeout support
    - Connection attempt limits
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.5,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        function_timeout: Optional[float] = None
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retries (default: 3)
            initial_delay: Initial delay in seconds (default: 0.5)
            max_delay: Maximum delay cap in seconds (default: 10.0)
            exponential_base: Base for exponential backoff (default: 2.0)
            function_timeout: Timeout for individual function calls in seconds
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.function_timeout = function_timeout
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic and exponential backoff.
        
        Args:
            func: Callable to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            Exception: Last exception if all retries exhausted
        """
        last_exception = None
        total_wait_time = 0.0
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries + 1} for {func.__name__}")
                
                # Execute with timeout if configured
                if self.function_timeout is not None:
                    result = self._execute_with_timeout(func, self.function_timeout, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(
                        f"Success on attempt {attempt + 1} (total wait: {total_wait_time:.2f}s)"
                    )
                
                return result
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff with jitter
                    delay = self.initial_delay * (self.exponential_base ** attempt)
                    delay = min(delay, self.max_delay)
                    
                    # Add jitter (±25% randomness)
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    delay_with_jitter = max(0, delay + jitter)
                    total_wait_time += delay_with_jitter
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay_with_jitter:.2f}s... "
                        f"(cumulative wait: {total_wait_time:.2f}s)"
                    )
                    time.sleep(delay_with_jitter)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts exhausted. "
                        f"Total wait time: {total_wait_time:.2f}s. "
                        f"Last error: {str(e)}"
                    )
        
        raise last_exception if last_exception else Exception("Unknown error in retry handler")
    
    @staticmethod
    def _execute_with_timeout(func: Callable, timeout: float, *args, **kwargs) -> Any:
        """
        Execute function with timeout (requires threading).
        
        Note: This is a simple implementation using threading.
        For more robust timeout handling, consider using signal or asyncio.
        
        Args:
            func: Function to execute
            timeout: Timeout in seconds
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            TimeoutError: If function exceeds timeout
        """
        import threading
        
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Function {func.__name__} exceeded {timeout}s timeout")
        
        if exception[0] is not None:
            raise exception[0]
        
        return result[0]


# Pre-configured retry handlers for common use cases
HTTP_RETRY_HANDLER = RetryHandler(
    max_retries=2,
    initial_delay=0.3,
    max_delay=10.0,
    exponential_base=2.0,
    function_timeout=5.0
)

NETWORK_RETRY_HANDLER = RetryHandler(
    max_retries=3,
    initial_delay=0.5,
    max_delay=15.0,
    exponential_base=2.0,
    function_timeout=10.0
)


def create_retry_handler(
    max_retries: int = 3,
    initial_delay: float = 0.5,
    max_delay: float = 10.0,
    exponential_base: float = 2.0
) -> RetryHandler:
    """
    Create a custom retry handler.
    
    Args:
        max_retries: Maximum retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Exponential backoff base
        
    Returns:
        RetryHandler instance
    """
    return RetryHandler(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base
    )
