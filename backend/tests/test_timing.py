"""Tests for the @timed decorator."""

import logging

import pytest

from app.core.timing import timed


def test_timed_returns_result_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    @timed
    def add(a: int, b: int) -> int:
        return a + b

    with caplog.at_level(logging.INFO):
        assert add(2, 3) == 5

    assert add.__name__ == "add"
    assert "add took" in caplog.text
