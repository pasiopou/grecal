from datetime import date, datetime, timezone

from icalendar import Calendar
import pytest

from grecal.generator import (
    build_calendar,
    generate_namedays,
    generate_personal_namedays,
    lookup_date,
    search_names,
    select_namedays,
    select_namedays_by_name,
    validate_catalog,
)
from grecal.models import Catalog, Feast, FeastType, Nameday, Observance


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


def test_lookup_date_returns_namedays_and_observances() -> None:
    source = _catalog()
    catalog = Catalog(
        feasts=source.feasts,
        namedays=source.namedays,
        observances=(Observance("shared", "shared", "Κοινή εορτή"),),
    )

    result = lookup_date(catalog, date(2026, 11, 30))

    assert result.day == date(2026, 11, 30)
    assert result.namedays == ("Ανδρέας", "Ανδριανή", "Άντρια")
    assert result.observances == ("Κοινή εορτή",)


def test_lookup_date_returns_empty_groups_and_validates_the_year() -> None:
    assert lookup_date(_catalog(), date(2026, 1, 1)).namedays == ()

    with pytest.raises(ValueError, match="between 1900 and 2100"):
        lookup_date(_catalog(), date(1899, 11, 30))


def test_search_names_ranks_prefixes_before_substrings() -> None:
    results = search_names(_catalog(), "ανδ", limit=2)

    assert [result.name for result in results] == ["Ανδρέας", "Ανδριανή"]
    assert [result.match_type for result in results] == ["prefix", "prefix"]


def test_search_names_handles_adjacent_transpositions() -> None:
    results = search_names(_catalog(), "ανδρεσα")

    assert results[0].name == "Ανδρέας"
    assert results[0].match_type == "fuzzy"


@pytest.mark.parametrize(
    ("query", "limit", "message"),
    [
        ("", 10, "query must not be empty"),
        ("Ανδρέας", 0, "limit must be at least 1"),
    ],
)
def test_search_names_rejects_invalid_arguments(
    query: str, limit: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        search_names(_catalog(), query, limit=limit)


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


def test_calendar_contains_standard_and_compatibility_metadata() -> None:
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    calendar = build_calendar(
        {date(2026, 8, 15): ("Μαρία",)},
        generated_at=stamp,
        calendar_name="Οικογενειακές γιορτές",
        calendar_description="Ονομαστικές εορτές της οικογένειας",
        calendar_color="blue",
        calendar_id="official-complete",
    )

    assert str(calendar["UID"]) == (
        "urn:uuid:b484af8b-559e-5081-a6be-8b69bc217873"
    )
    assert str(calendar["NAME"]) == "Οικογενειακές γιορτές"
    assert str(calendar["X-WR-CALNAME"]) == "Οικογενειακές γιορτές"
    assert str(calendar["DESCRIPTION"]) == "Ονομαστικές εορτές της οικογένειας"
    assert str(calendar["X-WR-CALDESC"]) == "Ονομαστικές εορτές της οικογένειας"
    assert calendar.decoded("LAST-MODIFIED") == stamp
    assert str(calendar["COLOR"]) == "blue"
    event = next(item for item in calendar.walk() if item.name == "VEVENT")
    assert str(event["UID"]) == (
        "urn:uuid:fd5eabe4-6772-5832-ba47-1290876b29ff"
    )


def test_event_uids_are_stable_across_content_changes_and_isolated_by_feed() -> None:
    day = date(2026, 8, 15)
    original = build_calendar(
        {day: ("Μαρία",)},
        calendar_id="official-complete",
    )
    revised = build_calendar(
        {day: ("Μαρία", "Παναγιώτης")},
        grouped_observances={day: ("Κοίμηση της Θεοτόκου",)},
        calendar_id="official-complete",
    )
    other_feed = build_calendar(
        {day: ("Μαρία",)},
        calendar_id="personal:maria",
    )

    original_event = next(
        item for item in original.walk() if item.name == "VEVENT"
    )
    revised_event = next(
        item for item in revised.walk() if item.name == "VEVENT"
    )
    other_event = next(
        item for item in other_feed.walk() if item.name == "VEVENT"
    )
    assert str(original_event["UID"]) == str(revised_event["UID"])
    assert str(original_event["UID"]) != str(other_event["UID"])
    assert str(original["UID"]) == str(revised["UID"])
    assert str(original["UID"]) != str(other_feed["UID"])


def test_calendar_metadata_can_be_omitted_and_rejects_empty_values() -> None:
    calendar = build_calendar(
        {},
        calendar_name=None,
        calendar_description=None,
    )

    assert "NAME" not in calendar
    assert "X-WR-CALNAME" not in calendar
    assert "DESCRIPTION" not in calendar
    assert "X-WR-CALDESC" not in calendar
    assert "COLOR" not in calendar
    assert "LAST-MODIFIED" in calendar

    with pytest.raises(ValueError, match="calendar_name must be a non-empty"):
        build_calendar({}, calendar_name="  ")
    with pytest.raises(ValueError, match="calendar_id must be a non-empty"):
        build_calendar({}, calendar_id="  ")
