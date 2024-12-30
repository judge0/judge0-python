import time
from abc import ABC, abstractmethod


class RetryStrategy(ABC):
    """Abstract base class that defines the interface for any retry strategy.

    See :obj:`MaxRetries`, :obj:`MaxWaitTime`, and :obj:`RegularPeriodRetry` for
    example implementations.
    """

    @abstractmethod
    def is_done(self) -> bool:
        """Check if the retry strategy has exhausted its retries."""
        pass

    @abstractmethod
    def wait(self) -> None:
        """Delay implementation before the next retry attempt."""
        pass

    @abstractmethod
    def step(self) -> None:
        """Update internal attributes of the retry strategy."""
        pass


class MaxRetries(RetryStrategy):
    """Check for submissions status every 100 ms and retry a maximum of
    `max_retries` times.

    Parameters
    ----------
    max_retries : int
        Max number of retries.
    """

    def __init__(self, max_retries: int = 20):
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1.")
        self.n_retries = 0
        self.max_retries = max_retries

    def step(self):
        """Increment the number of retries by one."""
        self.n_retries += 1

    def wait(self):
        """Wait for 0.1 seconds between retries."""
        time.sleep(0.1)

    def is_done(self) -> bool:
        """Check if the number of retries is bigger or equal to specified
        maximum number of retries."""
        return self.n_retries >= self.max_retries


class MaxWaitTime(RetryStrategy):
    """Check for submissions status every 100 ms and wait for all submissions
    a maximum of `max_wait_time` (seconds).

    Parameters
    ----------
    max_wait_time_sec : float
        Maximum waiting time (in seconds).
    """

    def __init__(self, max_wait_time_sec: float = 5 * 60):
        self.max_wait_time_sec = max_wait_time_sec
        self.total_wait_time = 0

    def step(self):
        """Add 0.1 seconds to total waiting time."""
        self.total_wait_time += 0.1

    def wait(self):
        """Wait (sleep) for 0.1 seconds."""
        time.sleep(0.1)

    def is_done(self):
        """Check if the total waiting time is bigger or equal to the specified
        maximum waiting time."""
        return self.total_wait_time >= self.max_wait_time_sec


class RegularPeriodRetry(RetryStrategy):
    """Check for submissions status periodically for indefinite amount of time.

    Parameters
    ----------
    wait_time_sec : float
        Wait time between retries (in seconds).
    """

    def __init__(self, wait_time_sec: float = 0.1):
        self.wait_time_sec = wait_time_sec

    def wait(self):
        """Wait for `wait_time_sec` seconds."""
        time.sleep(self.wait_time_sec)

    def is_done(self) -> bool:
        """Return False, as this retry strategy is indefinite."""
        return False

    def step(self) -> None:
        """Satisfy the interface with a dummy implementation."""
        pass
