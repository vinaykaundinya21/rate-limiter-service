import pytest
from unittest.mock import patch, MagicMock
from app.algorithms.token_bucket import is_allowed_token_bucket
from app.algorithms.sliding_window import is_allowed_sliding_window
from app.algorithms.fixed_window import is_allowed_fixed_window


# ─── Token Bucket Tests ───────────────────────────────────────────

def test_token_bucket_first_request_allowed():
    with patch("app.algorithms.token_bucket.get_redis") as mock_redis:
        r = MagicMock()
        r.hgetall.return_value = {}
        mock_redis.return_value = r
        result = is_allowed_token_bucket("user1", capacity=10, refill_rate=1.0)
        assert result == True

def test_token_bucket_blocks_when_no_tokens():
    with patch("app.algorithms.token_bucket.get_redis") as mock_redis:
        r = MagicMock()
        r.hgetall.return_value = {"tokens": "0", "last_refill": "1700000000.0"}
        mock_redis.return_value = r
        result = is_allowed_token_bucket("user2", capacity=10, refill_rate=0.0)
        assert result == False

def test_token_bucket_allows_after_refill():
    with patch("app.algorithms.token_bucket.get_redis") as mock_redis:
        r = MagicMock()
        r.hgetall.return_value = {"tokens": "0", "last_refill": "1700000000.0"}
        mock_redis.return_value = r
        result = is_allowed_token_bucket("user3", capacity=10, refill_rate=100.0)
        assert result == True


# ─── Sliding Window Tests ─────────────────────────────────────────

def test_sliding_window_first_request_allowed():
    with patch("app.algorithms.sliding_window.get_redis") as mock_redis:
        r = MagicMock()
        r.zcard.return_value = 0
        mock_redis.return_value = r
        result = is_allowed_sliding_window("user1", limit=10, window_seconds=60)
        assert result == True

def test_sliding_window_blocks_when_limit_reached():
    with patch("app.algorithms.sliding_window.get_redis") as mock_redis:
        r = MagicMock()
        r.zcard.return_value = 10
        mock_redis.return_value = r
        result = is_allowed_sliding_window("user2", limit=10, window_seconds=60)
        assert result == False

def test_sliding_window_allows_within_limit():
    with patch("app.algorithms.sliding_window.get_redis") as mock_redis:
        r = MagicMock()
        r.zcard.return_value = 5
        mock_redis.return_value = r
        result = is_allowed_sliding_window("user3", limit=10, window_seconds=60)
        assert result == True


# ─── Fixed Window Tests ───────────────────────────────────────────

def test_fixed_window_first_request_allowed():
    with patch("app.algorithms.fixed_window.get_redis") as mock_redis:
        r = MagicMock()
        r.incr.return_value = 1
        mock_redis.return_value = r
        result = is_allowed_fixed_window("user1", limit=10, window_seconds=60)
        assert result == True

def test_fixed_window_blocks_when_limit_exceeded():
    with patch("app.algorithms.fixed_window.get_redis") as mock_redis:
        r = MagicMock()
        r.incr.return_value = 11
        mock_redis.return_value = r
        result = is_allowed_fixed_window("user2", limit=10, window_seconds=60)
        assert result == False

def test_fixed_window_allows_at_exact_limit():
    with patch("app.algorithms.fixed_window.get_redis") as mock_redis:
        r = MagicMock()
        r.incr.return_value = 10
        mock_redis.return_value = r
        result = is_allowed_fixed_window("user3", limit=10, window_seconds=60)
        assert result == True
