from datetime import date

import pytest

from grecal.easter import orthodox_easter


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (1900, date(1900, 4, 22)),
        (2000, date(2000, 4, 30)),
        (2024, date(2024, 5, 5)),
        (2025, date(2025, 4, 20)),
        (2026, date(2026, 4, 12)),
        (2100, date(2100, 5, 2)),
    ],
)
def test_orthodox_easter_known_dates(year: int, expected: date) -> None:
    assert orthodox_easter(year) == expected


@pytest.mark.parametrize("year", [1899, 2101])
def test_orthodox_easter_rejects_out_of_range_years(year: int) -> None:
    with pytest.raises(ValueError, match="between 1900 and 2100"):
        orthodox_easter(year)
