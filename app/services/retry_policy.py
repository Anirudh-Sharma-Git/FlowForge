import random


class RetryPolicy:

    def __init__(
        self,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 300.0,
        jitter_ratio: float = 0.2,
    ):
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.jitter_ratio = jitter_ratio

    def get_delay(self, attempt_number: int) -> float:
        exponential_delay = (
            self.base_delay_seconds
            * (2 ** (attempt_number - 1))
        )

        capped_delay = min(
            exponential_delay,
            self.max_delay_seconds,
        )

        jitter = capped_delay * self.jitter_ratio

        return capped_delay + random.uniform(
            -jitter,
            jitter,
        )
