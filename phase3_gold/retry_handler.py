#!/usr/bin/env python3
"""
Retry Handler - Gold Tier
=========================
Reusable retry decorator with exponential backoff

Usage:
    @with_retry(max_attempts=3, base_delay=1)
    def my_function():
        pass
"""

import time
import logging
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RetryHandler')


class TransientError(Exception):
    """Temporary error that can be retried"""
    pass


class PermanentError(Exception):
    """Permanent error that should not be retried"""
    pass


def with_retry(max_attempts=3, base_delay=1, max_delay=60, exceptions=(TransientError,)):
    """
    Retry decorator with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 60)
        exceptions: Tuple of exceptions to catch and retry (default: TransientError)

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, base_delay=2)
        def send_email():
            # May raise TransientError
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__}: All {max_attempts} attempts failed. "
                            f"Last error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"{func.__name__}: Attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {delay}s... Error: {e}"
                    )

                    time.sleep(delay)

                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"{func.__name__}: Non-retryable error: {e}")
                    raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_on_error(max_attempts=3, base_delay=1, max_delay=60):
    """
    Simplified retry decorator that catches all Exception types

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Example:
        @retry_on_error(max_attempts=3)
        def api_call():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__}: All {max_attempts} attempts failed. "
                            f"Last error: {e}"
                        )
                        raise

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"{func.__name__}: Attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class RetryHandler:
    """
    Class-based retry handler for more complex scenarios

    Example:
        handler = RetryHandler(max_attempts=3, base_delay=2)
        result = handler.execute(my_function, arg1, arg2)
    """

    def __init__(self, max_attempts=3, base_delay=1, max_delay=60):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempt = 0

    def execute(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        self.attempt = 0
        last_exception = None

        while self.attempt < self.max_attempts:
            self.attempt += 1

            try:
                result = func(*args, **kwargs)
                return result

            except TransientError as e:
                last_exception = e

                if self.attempt == self.max_attempts:
                    logger.error(
                        f"Function failed after {self.max_attempts} attempts. "
                        f"Last error: {e}"
                    )
                    raise

                delay = self._calculate_delay()
                logger.warning(
                    f"Attempt {self.attempt}/{self.max_attempts} failed. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

            except Exception as e:
                # Non-retryable exception
                logger.error(f"Non-retryable error: {e}")
                raise

        if last_exception:
            raise last_exception

    def _calculate_delay(self):
        """Calculate delay with exponential backoff"""
        return min(self.base_delay * (2 ** (self.attempt - 1)), self.max_delay)

    def reset(self):
        """Reset attempt counter"""
        self.attempt = 0


# Graceful degradation helpers

class GracefulDegradation:
    """
    Helper class for graceful degradation when services fail

    Example:
        degrader = GracefulDegradation()
        if degrader.is_available('gmail_api'):
            send_email()
        else:
            degrader.queue_for_later(email_data)
    """

    def __init__(self):
        self.unavailable_services = {}
        self.queues = {}

    def is_available(self, service: str) -> bool:
        """Check if service is available"""
        if service in self.unavailable_services:
            last_failure = self.unavailable_services[service]
            # Service unavailable for more than 1 hour?
            if time.time() - last_failure > 3600:
                del self.unavailable_services[service]
                return True
            return False
        return True

    def mark_unavailable(self, service: str):
        """Mark service as unavailable"""
        self.unavailable_services[service] = time.time()
        logger.warning(f"Service {service} marked as unavailable")

    def queue_for_later(self, service: str, data: dict):
        """Queue data for later processing"""
        if service not in self.queues:
            self.queues[service] = []

        self.queues[service].append({
            'data': data,
            'queued_at': time.time()
        })

        logger.info(f"Queued data for {service} (queue size: {len(self.queues[service])})")

    def get_queue(self, service: str) -> list:
        """Get queued data for service"""
        return self.queues.get(service, [])

    def clear_queue(self, service: str):
        """Clear queue after successful processing"""
        if service in self.queues:
            count = len(self.queues[service])
            del self.queues[service]
            logger.info(f"Cleared queue for {service} ({count} items)")


if __name__ == '__main__':
    # Test retry decorator
    @with_retry(max_attempts=3, base_delay=1)
    def test_function():
        import random
        if random.random() < 0.7:
            raise TransientError("Random failure")
        return "Success!"

    print("Testing retry decorator...")
    for i in range(5):
        try:
            result = test_function()
            print(f"Test {i+1}: {result}")
        except TransientError as e:
            print(f"Test {i+1}: Failed - {e}")

    print("\nAll tests completed!")
