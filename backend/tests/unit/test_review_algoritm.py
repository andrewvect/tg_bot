from datetime import datetime, timedelta

import pytest

from app.states.user import review_algorithm


@pytest.mark.parametrize(
    "checks,passed,expected_minutes",
    [
        (1, True, 40),  # Normal case: passed=True, move to next level
        (5, True, 3840),  # Mid-level case
        (10, True, 983040),  # Max level case
        (11, True, 983040),  # Beyond max level case
        (1, False, 20),  # Failed at beginning
        (5, False, 40),  # Failed at higher level, go back 3 levels
        (2, False, 20),  # Failed with checks < 3
    ],
)
def test_review_algorithm(checks, passed, expected_minutes):
    # Setup
    current_time = datetime(2023, 1, 1, 12, 0)

    # Execute
    result = review_algorithm(current_time, checks, passed)

    # Assert
    expected_time = current_time + timedelta(minutes=expected_minutes)
    assert result == expected_time


def test_review_algorithm_default_passed():
    # Test default value of passed=True
    current_time = datetime(2023, 1, 1, 12, 0)
    result = review_algorithm(current_time, 1)
    expected_time = current_time + timedelta(minutes=40)
    assert result == expected_time
