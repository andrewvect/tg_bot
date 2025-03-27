from datetime import datetime, timedelta


def review_algorithm(
    checks: int,
    passed: bool = True,
    review_date: datetime = None,
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

    # values which define how many minutes should pass before next review
    values = {
        1: 20,
        2: 60,
        3: 120,
        4: 240,
        5: 480,
        6: 960,
        7: 1920,
        8: 3840,
        9: 7680,
        10: 15360,
    }

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
