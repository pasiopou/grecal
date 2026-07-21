from datetime import date, datetime, timezone

from icalendar import Calendar
import pytest

from grecal.generator import (
    build_calendar,
    generate_namedays,
    generate_personal_namedays,
    select_namedays,
    select_namedays_by_name,
    validate_catalog,
)
from grecal.models import Catalog, Feast, FeastType, Nameday


def _catalog() -> Catalog:
    return Catalog(
        feasts=(Feast("shared", FeastType.FIXED, month=11, day=30),),
        namedays=(
            Nameday("andreas", "shared", 95, ("Ανδρέας",)),
            Nameday("andriani", "shared", 60, ("Ανδριανή", "Άντρια")),
        ),
    )


def test_filtering_by_top_and_minimum_popularity() -> None:
    entries = _catalog().namedays
    assert [item.id for item in select_namedays(entries, top=1)] == ["andreas"]
    assert [
        item.id for item in select_namedays(entries, min_popularity=80)
    ] == ["andreas"]
    assert select_namedays(entries, top=99) == tuple(
        sorted(entries, key=lambda item: (-item.popularity, item.id))
    )


def test_top_filter_uses_id_to_break_equal_score_ties() -> None:
    entries = (
        Nameday("zeta", "shared", 80, ("Ζήτα",)),
        Nameday("alpha", "shared", 80, ("Άλφα",)),
    )

    assert [item.id for item in select_namedays(entries, top=1)] == ["alpha"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"top": 0}, "top must be at least 1"),
        ({"min_popularity": -1}, "between 0 and 100"),
        ({"min_popularity": 101}, "between 0 and 100"),
    ],
)
def test_filtering_rejects_values_outside_documented_ranges(
    kwargs: dict[str, int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        select_namedays(_catalog().namedays, **kwargs)


def test_names_on_the_same_day_are_grouped_in_one_result() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)
    assert grouped == {
        date(2026, 11, 30): ("Ανδρέας", "Ανδριανή", "Άντρια")
    }


def test_validate_catalog_checks_each_year_in_the_range() -> None:
    catalog = Catalog(
        feasts=(Feast("leap_day", FeastType.FIXED, month=2, day=29),),
        namedays=(),
    )

    validate_catalog(catalog, 2024, 2024)
    # CPython 3.14 made the date() error more specific; the wording is not part
    # of the public API, so test the validation failure rather than its text.
    with pytest.raises(ValueError):
        validate_catalog(catalog, 2024, 2025)


def test_selection_by_name_ignores_case_and_diacritics() -> None:
    selected = select_namedays_by_name(_catalog(), ("ανδρεας", "ΑΝΤΡΙΑ"))

    assert selected == (
        Nameday("andreas", "shared", 95, ("Ανδρέας",)),
        Nameday("andriani", "shared", 60, ("Άντρια",)),
    )


def test_selection_by_name_reports_all_unknown_names() -> None:
    with pytest.raises(
        ValueError,
        match="names not found in the catalog: Άγνωστος, Κανένας",
    ):
        select_namedays_by_name(_catalog(), ("Άγνωστος", "Κανένας"))


def test_personal_calendar_contains_only_requested_variants() -> None:
    grouped = generate_personal_namedays(
        _catalog(), ("Ανδρέας", "Άντρια"), 2026, 2026
    )

    assert grouped == {date(2026, 11, 30): ("Ανδρέας", "Άντρια")}


def test_ics_contains_one_all_day_event_without_description_or_location() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    payload = build_calendar(grouped, generated_at=stamp).to_ical()
    parsed = Calendar.from_ical(payload)
    events = [item for item in parsed.walk() if item.name == "VEVENT"]

    assert len(events) == 1
    event = events[0]
    assert str(event["SUMMARY"]) == "Ανδρέας, Ανδριανή, Άντρια"
    assert event.decoded("dtstart") == date(2026, 11, 30)
    assert event.decoded("dtend") == date(2026, 12, 1)
    assert "DESCRIPTION" not in event
    assert "LOCATION" not in event
    assert "Ανδρέας".encode("utf-8") in payload
