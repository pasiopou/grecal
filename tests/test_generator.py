from datetime import date, datetime, timezone

from icalendar import Calendar
import pytest

from grecal.generator import build_calendar, generate_namedays, select_namedays
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
