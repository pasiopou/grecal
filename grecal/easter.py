"""Orthodox Easter date calculation for Grecal."""

from __future__ import annotations

from datetime import date, timedelta


MIN_YEAR = 1900
MAX_YEAR = 2100


def orthodox_easter(year: int) -> date:
    """Return Greek Orthodox Easter Sunday in the Gregorian calendar.

    The calculation first determines Easter in the Julian calendar using the
    Orthodox computus, then converts that date to the civil Gregorian calendar.
    Only the project's documented range is accepted.
    """

    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError(f"year must be between {MIN_YEAR} and {MAX_YEAR}")

    golden_year = year % 19
    julian_leap_cycle = year % 4
    weekday_cycle = year % 7
    epact = (19 * golden_year + 15) % 30
    days_to_sunday = (
        2 * julian_leap_cycle + 4 * weekday_cycle - epact + 34
    ) % 7

    paschal_day = epact + days_to_sunday + 114
    julian_month = paschal_day // 31
    julian_day = paschal_day % 31 + 1

    # For March/April dates, this is the Julian-to-Gregorian difference.
    calendar_difference = year // 100 - year // 400 - 2
    return date(year, julian_month, julian_day) + timedelta(
        days=calendar_difference
    )
