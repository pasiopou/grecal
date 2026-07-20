import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from icalendar import Calendar
import pytest

from grecal.generator import build_calendar, generate_namedays, main
from grecal.parser import load_catalog


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return load_catalog(ROOT / "data" / "feasts.yaml", ROOT / "data" / "names.yaml")


def test_movable_and_fixed_groups_use_their_configured_dates() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)

    assert sum(len(names) for names in grouped.values()) == 642
    assert {"Λαμπρινή", "Λάμπρος", "Λίνα"} <= set(
        grouped[date(2026, 4, 12)]
    )
    assert {"Αλεξάνδρα", "Αλέκα"} <= set(grouped[date(2026, 4, 21)])
    assert grouped[date(2026, 5, 30)] == ("Εμμέλεια",)
    assert {"Μαρία", "Μαριέττα", "Μάρω"} <= set(
        grouped[date(2026, 8, 15)]
    )


def test_final_ics_has_rfc_line_endings_folding_and_minimal_events() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)
    payload = build_calendar(
        grouped, generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    ).to_ical()

    assert payload.startswith(b"BEGIN:VCALENDAR\r\n")
    assert payload.endswith(b"END:VCALENDAR\r\n")
    assert b"\xef\xbb\xbf" not in payload
    assert b"\n" not in payload.replace(b"\r\n", b"")
    assert max(len(line) for line in payload.split(b"\r\n")) <= 75
    payload.decode("utf-8")

    parsed = Calendar.from_ical(payload)
    events = [component for component in parsed.walk() if component.name == "VEVENT"]
    assert len(events) == len(grouped)
    assert len({event.decoded("dtstart") for event in events}) == len(events)

    required = {"UID", "DTSTAMP", "SUMMARY", "DTSTART", "DTEND"}
    for event in events:
        assert set(event.keys()) == required
        assert event.decoded("dtend") == event.decoded("dtstart") + timedelta(days=1)
        assert event["DTSTART"].params["VALUE"] == "DATE"
        assert event["DTEND"].params["VALUE"] == "DATE"


def test_cli_generates_requested_year_and_reports_statistics(
    tmp_path: Path, capsys
) -> None:
    output = tmp_path / "namedays-2026.ics"

    assert main(["--all", "--from-year", "2026", "--output", str(output)]) == 0

    parsed = Calendar.from_ical(output.read_bytes())
    events = [component for component in parsed.walk() if component.name == "VEVENT"]
    assert len(events) == 226
    assert all(event.decoded("dtstart").year == 2026 for event in events)

    report = capsys.readouterr().out
    assert f"Generated: {output}" in report
    assert "Years: 2026" in report
    assert "Selection: all nameday groups" in report
    assert all(
        heading in report
        for heading in (
            "Identity groups",
            "Display names",
            "Church feasts",
            "Calendar events",
        )
    )
    assert re.search(r"^2026\s+457\s+642\s+0\s+226$", report, re.MULTILINE)
    assert re.search(
        r"^Total occurrences\s+457\s+642\s+0\s+226$",
        report,
        re.MULTILINE,
    )
    assert "Average/year" not in report


def test_cli_reports_yearly_totals_and_averages_for_multiple_years(
    tmp_path: Path, capsys
) -> None:
    output = tmp_path / "namedays-2025-2026.ics"

    assert main(
        [
            "--top",
            "100",
            "--from-year",
            "2025",
            "--to-year",
            "2026",
            "--output",
            str(output),
        ]
    ) == 0

    report = capsys.readouterr().out
    assert "Years: 2025-2026" in report
    assert "Selection: top 100 nameday groups" in report
    assert re.search(r"^2025\s+100\s+208\s+0\s+77$", report, re.MULTILINE)
    assert re.search(r"^2026\s+100\s+208\s+0\s+76$", report, re.MULTILINE)
    assert re.search(
        r"^Total occurrences\s+200\s+416\s+0\s+153$",
        report,
        re.MULTILINE,
    )
    assert re.search(
        r"^Average/year\s+100\.0\s+208\.0\s+0\.0\s+76\.5$",
        report,
        re.MULTILINE,
    )


def test_cli_reports_output_write_errors_without_a_traceback(
    tmp_path: Path, capsys
) -> None:
    with pytest.raises(SystemExit) as error:
        main(
            [
                "--top",
                "1",
                "--from-year",
                "2026",
                "--output",
                str(tmp_path),
            ]
        )

    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "error:" in stderr
    assert str(tmp_path) in stderr
    assert "Traceback" not in stderr
