"""Single dispatch point for all Grecal feast-date rules."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable, Mapping, Optional

from .models import Feast, FeastType


class UnsupportedFeastRuleError(NotImplementedError):
    """Raised when a feast refers to an unknown or unsupported rule."""


CustomRule = Callable[[Feast, int, date], Optional[date]]


def _require_nominal_date(feast: Feast, year: int) -> date:
    if feast.month is None or feast.day is None:
        raise ValueError(f"feast {feast.id!r} requires month and day")
    return date(year, feast.month, feast.day)


def _saint_mark(feast: Feast, year: int, easter: date) -> date:
    """Resolve Saint Mark's nominal feast and its Paschal transfer."""

    nominal = _require_nominal_date(feast, year)
    transfer_threshold = nominal - timedelta(days=2)
    return easter + timedelta(days=2) if easter > transfer_threshold else nominal


def _sunday_on_or_after(feast: Feast, year: int, easter: date) -> date:
    """Return the first Sunday on or after a data-provided nominal date."""

    nominal = _require_nominal_date(feast, year)
    return nominal + timedelta(days=(6 - nominal.weekday()) % 7)


def _leap_day_only(feast: Feast, year: int, easter: date) -> date | None:
    """Return 29 February in leap years and no occurrence otherwise."""

    del easter
    if feast.month != 2 or feast.day != 29:
        raise ValueError(
            f"feast {feast.id!r} requires the nominal date 29 February"
        )
    try:
        return date(year, 2, 29)
    except ValueError:
        return None


def _builtin_custom_rule(rule: str) -> CustomRule | None:
    if rule == "saint_mark":
        return _saint_mark
    if rule == "sunday_on_or_after":
        return _sunday_on_or_after
    if rule == "leap_day_only":
        return _leap_day_only
    return None


def resolve_feast_date(
    feast: Feast,
    year: int,
    easter: date,
    *,
    custom_rules: Mapping[str, CustomRule] | None = None,
) -> date | None:
    """Resolve a feast, returning ``None`` when it has no occurrence that year."""

    if feast.type is FeastType.FIXED:
        return _require_nominal_date(feast, year)
    if feast.type is FeastType.OFFSET_FROM_EASTER:
        if feast.offset is None:
            raise ValueError(f"Easter-offset feast {feast.id!r} has no offset")
        return easter + timedelta(days=feast.offset)
    if feast.type is FeastType.SAINT_GEORGE:
        nominal = date(year, 4, 23)
        return easter + timedelta(days=1) if nominal <= easter else nominal
    if feast.type is FeastType.CUSTOM:
        if feast.rule is None:
            raise ValueError(f"custom feast {feast.id!r} has no rule name")
        resolver = (custom_rules or {}).get(feast.rule)
        if resolver is None:
            resolver = _builtin_custom_rule(feast.rule)
        if resolver is None:
            raise UnsupportedFeastRuleError(
                f"unknown custom rule {feast.rule!r} for feast {feast.id!r}"
            )
        return resolver(feast, year, easter)
    raise UnsupportedFeastRuleError(
        f"unsupported rule type {feast.type.value!r}"
    )
