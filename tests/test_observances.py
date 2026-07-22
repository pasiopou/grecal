import re
from datetime import date, datetime, timezone
from pathlib import Path

from icalendar import Calendar
import pytest

from grecal.generator import (
    build_calendar,
    generate_namedays,
    generate_observances,
    main,
)
from grecal.parser import load_catalog


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return load_catalog(
        ROOT / "data" / "feasts.yaml",
        ROOT / "data" / "names.yaml",
        ROOT / "data" / "observances.yaml",
    )


def _events(calendar: Calendar):
    return [component for component in calendar.walk() if component.name == "VEVENT"]


def test_production_catalog_has_38_unique_observances() -> None:
    catalog = _catalog()

    assert len(catalog.observances) == 38
    assert len({item.id for item in catalog.observances}) == 38
    assert len({item.title for item in catalog.observances}) == 38
    referenced_feasts = {
        feast_id for item in catalog.namedays for feast_id in item.feasts
    } | {
        item.feast for item in catalog.observances
    }
    assert referenced_feasts == {item.id for item in catalog.feasts}


def test_all_movable_observances_resolve_from_easter() -> None:
    grouped = generate_observances(_catalog(), 2026, 2026)

    assert "Κυριακή της Απόκρεω" in grouped[date(2026, 2, 15)]
    assert "Κυριακή της Τυρινής" in grouped[date(2026, 2, 22)]
    assert "Καθαρά Δευτέρα" in grouped[date(2026, 2, 23)]
    assert "Κυριακή της Ορθοδοξίας" in grouped[date(2026, 3, 1)]
    assert "Κυριακή του Αγίου Γρηγορίου του Παλαμά" in grouped[
        date(2026, 3, 8)
    ]
    assert "Κυριακή της Σταυροπροσκυνήσεως" in grouped[
        date(2026, 3, 15)
    ]
    assert "Κυριακή του Αγίου Ιωάννη της Κλίμακος" in grouped[
        date(2026, 3, 22)
    ]
    assert "Παρασκευή Ακάθιστου Ύμνου" in grouped[
        date(2026, 3, 27)
    ]
    assert "Κυριακή της Οσίας Μαρίας της Αιγυπτίας" in grouped[
        date(2026, 3, 29)
    ]
    assert "Κυριακή των Βαΐων" in grouped[date(2026, 4, 5)]
    assert (
        "Μεγάλη Παρασκευή - Τα άγια πάθη του Κυρίου και η Σταύρωση"
        in grouped[date(2026, 4, 10)]
    )
    assert "Πάσχα (Ανάσταση)" in grouped[date(2026, 4, 12)]
    assert "Κυριακή του Θωμά" in grouped[date(2026, 4, 19)]
    assert "Κυριακή των Μυροφόρων" in grouped[date(2026, 4, 26)]
    assert "Κυριακή του Παραλύτου" in grouped[date(2026, 5, 3)]
    assert "Κυριακή της Σαμαρείτιδος" in grouped[date(2026, 5, 10)]
    assert "Κυριακή του Τυφλού" in grouped[date(2026, 5, 17)]
    assert "Ανάληψη του Κυρίου" in grouped[date(2026, 5, 21)]
    assert "Πεντηκοστή" in grouped[date(2026, 5, 31)]
    assert "Του Αγίου Πνεύματος" in grouped[date(2026, 6, 1)]
    assert "Κυριακή των Αγίων Πάντων" in grouped[date(2026, 6, 7)]
    assert "Σάββατο των Αγίων Θεοδώρων" in grouped[date(2026, 2, 28)]
    assert "Σάββατο του Λαζάρου" in grouped[date(2026, 4, 4)]
    assert "Ζωοδόχος Πηγή" in grouped[date(2026, 4, 17)]
    assert "Κυριακή των Προπατόρων" in grouped[date(2026, 12, 13)]


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, date(2024, 4, 19)),
        (2025, date(2025, 4, 4)),
        (2026, date(2026, 3, 27)),
    ],
)
def test_friday_of_akathist_hymn_tracks_orthodox_easter(
    year: int, expected: date
) -> None:
    grouped = generate_observances(_catalog(), year, year)

    assert "Παρασκευή Ακάθιστου Ύμνου" in grouped[expected]


@pytest.mark.parametrize(
    ("day", "title"),
    [
        (date(2026, 1, 1), "Περιτομή του Κυρίου"),
        (date(2026, 1, 6), "Θεοφάνια (Βάπτιση)"),
        (date(2026, 1, 30), "Οι Τρεις Ιεράρχες"),
        (date(2026, 2, 2), "Υπαπαντή του Κυρίου"),
        (date(2026, 3, 25), "Ευαγγελισμός της Θεοτόκου"),
        (date(2026, 8, 6), "Μεταμόρφωση του Σωτήρος"),
        (date(2026, 8, 15), "Κοίμηση της Θεοτόκου"),
        (
            date(2026, 8, 31),
            "Κατάθεσις της Τιμίας Ζώνης της Θεοτόκου",
        ),
        (date(2026, 9, 8), "Γέννηση της Θεοτόκου"),
        (date(2026, 9, 14), "Ύψωση του Τιμίου Σταυρού"),
        (date(2026, 11, 21), "Εισόδια της Θεοτόκου"),
        (
            date(2026, 12, 26),
            "Σύναξις της Υπεραγίας Θεοτόκου",
        ),
        (
            date(2026, 12, 25),
            "Γέννηση του Χριστού (Χριστούγεννα)",
        ),
    ],
)
def test_all_fixed_observances_resolve_to_the_supplied_dates(
    day: date, title: str
) -> None:
    grouped = generate_observances(_catalog(), 2026, 2026)

    assert title in grouped[day]


def test_combined_summary_puts_observances_before_names() -> None:
    day = date(2026, 8, 15)
    calendar = build_calendar(
        {day: ("Μαρία", "Μάρω")},
        grouped_observances={day: ("Κοίμηση της Θεοτόκου",)},
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    event = _events(calendar)[0]

    assert str(event["SUMMARY"]) == (
        "Κοίμηση της Θεοτόκου — Μαρία, Μάρω"
    )
    assert "DESCRIPTION" not in event
    assert "LOCATION" not in event


def test_multiple_observances_still_produce_one_event_for_the_day() -> None:
    day = date(2026, 3, 25)
    calendar = build_calendar(
        {},
        grouped_observances={
            day: ("Πρώτη εορτή", "Δεύτερη εορτή")
        },
    )
    events = _events(calendar)

    assert len(events) == 1
    assert str(events[0]["SUMMARY"]) == (
        "Πρώτη εορτή · Δεύτερη εορτή"
    )


def test_nameday_only_generation_excludes_observance_titles() -> None:
    catalog = _catalog()
    names = generate_namedays(catalog, 2026, 2026)
    calendar = build_calendar(
        names,
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert len(_events(calendar)) == 265
    easter_event = next(
        event
        for event in _events(calendar)
        if event.decoded("DTSTART") == date(2026, 4, 12)
    )
    easter_summary = str(easter_event["SUMMARY"])
    assert easter_summary.startswith("Αναστασία, Τασούλα")
    assert "Αναστάσιος" in easter_summary
    assert "Ανέστης" in easter_summary
    assert "Ορθόδοξο Πάσχα" not in easter_summary


def test_feasts_only_cli_generates_38_events(tmp_path: Path, capsys) -> None:
    output = tmp_path / "feasts-2026.ics"

    assert main(
        [
            "generate",
            "--feasts-only",
            "--from-year",
            "2026",
            "--output",
            str(output),
        ]
    ) == 0

    parsed = Calendar.from_ical(output.read_bytes())
    events = _events(parsed)
    assert len(events) == 38
    assert str(parsed["UID"]) == (
        "urn:uuid:4ea6860e-3df1-5f49-8098-dc834e9a093b"
    )
    assert str(parsed["NAME"]) == "Grecal — Greek Orthodox Feasts"
    assert any(
        str(event["SUMMARY"]) == "Πεντηκοστή"
        for event in events
    )
    report = capsys.readouterr().out
    assert "Selection: church feasts only" in report
    assert re.search(r"^2026\s+0\s+0\s+38\s+38$", report, re.MULTILINE)


def test_include_feasts_cli_merges_titles_with_names(tmp_path: Path) -> None:
    output = tmp_path / "combined-2026.ics"

    assert main(
        [
            "generate",
            "--all",
            "--include-feasts",
            "--from-year",
            "2026",
            "--output",
            str(output),
        ]
    ) == 0

    parsed = Calendar.from_ical(output.read_bytes())
    events = _events(parsed)
    assert len(events) == 269
    assert str(parsed["UID"]) == (
        "urn:uuid:209a65ff-4de0-5814-bd78-e273c944ae52"
    )
    assert str(parsed["NAME"]) == "Grecal — Greek Orthodox Calendar"
    assert len({event.decoded("DTSTART") for event in events}) == len(events)
    dormition = next(
        event
        for event in events
        if event.decoded("DTSTART") == date(2026, 8, 15)
    )
    dormition_summary = str(dormition["SUMMARY"])
    assert dormition_summary.startswith("Κοίμηση της Θεοτόκου — ")
    assert "Παναγιώτης" in dormition_summary
    assert "Μαρία" in dormition_summary
    assert all("DESCRIPTION" not in event for event in events)
    assert all("LOCATION" not in event for event in events)
