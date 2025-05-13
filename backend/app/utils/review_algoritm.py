from datetime import datetime, timedelta


def review_algorithm(
    checks: int,
    passed: bool = True,
    review_date: datetime | None = None,
) -> int:
    """
    Determines the next review date based on the number of checks and whether the last review was passed.

    Args:
        checks (int): The number of times the review has been checked.
        passed (bool): Indicates if the last review was passed. Defaults to True.
        review_date (datetime): The current review date. Defaults to the current datetime.

    Returns:
        int: The timestamp (as an integer, in seconds since epoch) of the next review date.
    """
    if review_date is None:
        review_date = datetime.now()

    # Constants for review intervals in minutes
    REVIEW_INTERVALS = {
        1: 20,  # 20 minutes
        2: 60,  # 1 hour
        3: 120,  # 2 hours
        4: 240,  # 4 hours
        5: 480,  # 8 hours
        6: 960,  # 16 hours
        7: 1920,  # 32 hours (1.33 days)
        8: 3840,  # 64 hours (2.67 days)
        9: 7680,  # 128 hours (5.33 days)
        10: 15360,  # 256 hours (10.67 days)
    }

    values = REVIEW_INTERVALS

    if passed:
        if checks > 10:
            next_review = review_date + timedelta(minutes=values[10])
        else:
            next_review = review_date + timedelta(minutes=values[min(checks + 1, 10)])
    else:
        if checks < 3:
            next_review = review_date + timedelta(minutes=values[1])
        else:
            next_review = review_date + timedelta(minutes=values[max(checks - 3, 1)])

    return int(next_review.timestamp())
