from datetime import date
from typing import Optional

import pytest

from grecal.easter import orthodox_easter
from grecal.models import Feast, FeastType
from grecal.rules import UnsupportedFeastRuleError, resolve_feast_date


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2026, date(2026, 4, 23)),
        (2024, date(2024, 5, 6)),
        (2006, date(2006, 4, 24)),
    ],
)
def test_saint_george_rule(year: int, expected: date) -> None:
    feast = Feast("saint_george", FeastType.SAINT_GEORGE)
    assert resolve_feast_date(feast, year, orthodox_easter(year)) == expected


@pytest.mark.parametrize(
    ("offset", "expected"),
    [(-43, date(2026, 2, 28)), (-8, date(2026, 4, 4)), (50, date(2026, 6, 1))],
)
def test_offset_from_easter_rule(offset: int, expected: date) -> None:
    feast = Feast("movable", FeastType.OFFSET_FROM_EASTER, offset=offset)
    assert resolve_feast_date(feast, 2026, orthodox_easter(2026)) == expected


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2026, date(2026, 4, 25)),
        (2024, date(2024, 5, 7)),
        (2022, date(2022, 4, 26)),
    ],
)
def test_saint_mark_custom_rule(year: int, expected: date) -> None:
    feast = Feast(
        "saint_mark",
        FeastType.CUSTOM,
        month=4,
        day=25,
        rule="saint_mark",
    )
    assert resolve_feast_date(feast, year, orthodox_easter(year)) == expected


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2022, date(2022, 12, 11)),
        (2026, date(2026, 12, 13)),
        (2027, date(2027, 12, 12)),
    ],
)
def test_sunday_on_or_after_custom_rule(year: int, expected: date) -> None:
    feast = Feast(
        "forefathers",
        FeastType.CUSTOM,
        month=12,
        day=11,
        rule="sunday_on_or_after",
    )
    assert resolve_feast_date(feast, year, orthodox_easter(year)) == expected


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, date(2024, 2, 29)),
        (2025, None),
        (2100, None),
    ],
)
def test_leap_day_only_custom_rule(
    year: int, expected: Optional[date]
) -> None:
    feast = Feast(
        "kassianos",
        FeastType.CUSTOM,
        month=2,
        day=29,
        rule="leap_day_only",
    )
    assert resolve_feast_date(feast, year, orthodox_easter(year)) == expected


def test_injected_custom_rule_has_no_global_registration() -> None:
    feast = Feast("example", FeastType.CUSTOM, rule="example")
    expected = date(2026, 9, 9)

    actual = resolve_feast_date(
        feast,
        2026,
        orthodox_easter(2026),
        custom_rules={"example": lambda _feast, _year, _easter: expected},
    )

    assert actual == expected
    with pytest.raises(UnsupportedFeastRuleError, match="unknown custom rule"):
        resolve_feast_date(feast, 2026, orthodox_easter(2026))
