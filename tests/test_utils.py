"""Tests for utility functions."""

from master_doc_system.utils import add


def test_add_returns_sum() -> None:
    """add should return the arithmetic sum of its inputs."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
