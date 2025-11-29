"""
Conftest for unit tests that don't require database connection.
"""
import pytest


def pytest_configure(config):
    """Configure pytest to skip database setup for unit tests."""
    # Mark unit tests to skip database fixtures
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no database required)"
    )
