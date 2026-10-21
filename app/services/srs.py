from datetime import date, timedelta
from typing import Optional


def calculate_sm2(
    grade: int,
    repetitions: int,
    interval_days: int,
    ease_factor: float,
    today: Optional[date] = None,
) -> tuple[int, int, float, date]:
    """
    Pure implementation of the SuperMemo 2 (SM-2) spaced repetition algorithm.

    Args:
        grade: User recall score from 0 (complete blackout) to 5 (perfect recall).
        repetitions: Number of consecutive successful recalls (grade >= 3).
        interval_days: Current review interval in days.
        ease_factor: Ease factor (difficulty multiplier, default 2.5, min 1.3).
        today: Reference date for due date calculation (defaults to date.today()).

    Returns:
        tuple of (new_repetitions, new_interval_days, new_ease_factor, new_due_date)
    """
    if not isinstance(grade, int) or grade < 0 or grade > 5:
        raise ValueError("Grade must be an integer between 0 and 5.")

    if today is None:
        today = date.today()

    # Calculate new Ease Factor
    # EF' = EF + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    new_ef = ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    # If score is below 3, reset repetitions and restart with 1-day interval
    if grade < 3:
        new_repetitions = 0
        new_interval = 1
    else:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = int(round(interval_days * new_ef))
            if new_interval < 1:
                new_interval = 1
        new_repetitions = repetitions + 1

    new_due_date = today + timedelta(days=new_interval)
    return new_repetitions, new_interval, round(new_ef, 3), new_due_date
