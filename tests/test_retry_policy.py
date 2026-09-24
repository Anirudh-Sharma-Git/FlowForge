from app.services.retry_policy import RetryPolicy


def test_retry_delay_increases_with_attempt_number():
    policy = RetryPolicy(
        base_delay_seconds=1.0,
        jitter_ratio=0.0,
    )

    delay_1 = policy.get_delay(1)
    delay_2 = policy.get_delay(2)
    delay_3 = policy.get_delay(3)

    assert delay_1 == 1.0
    assert delay_2 == 2.0
    assert delay_3 == 4.0


def test_retry_delay_is_capped():
    policy = RetryPolicy(
        base_delay_seconds=10.0,
        max_delay_seconds=30.0,
        jitter_ratio=0.0,
    )

    assert policy.get_delay(10) == 30.0


def test_jitter_changes_delay():
    policy = RetryPolicy(
        base_delay_seconds=10.0,
        jitter_ratio=0.2,
    )

    delays = {
        policy.get_delay(1)
        for _ in range(20)
    }

    assert len(delays) > 1