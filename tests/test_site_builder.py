import json
from datetime import date, datetime, timezone
from pathlib import Path

from icalendar import Calendar
import pytest

from scripts.build_site import OUTPUT_MARKER, build_site, main


BUILD_DAY = date(2026, 7, 22)
BUILD_STAMP = datetime(2026, 7, 22, 12, 30, tzinfo=timezone.utc)


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _events(calendar: Calendar):
    return [item for item in calendar.walk() if item.name == "VEVENT"]


@pytest.fixture(scope="module")
def built_site(tmp_path_factory):
    output = tmp_path_factory.mktemp("site-builder") / "_site"
    config = build_site(
        output,
        today=BUILD_DAY,
        generated_at=BUILD_STAMP,
    )
    return output, config


def test_site_builder_generates_the_expected_artifact_set(built_site) -> None:
    output, config = built_site

    assert config["schema_version"] == 1
    assert config["generated_at"] == "2026-07-22T12:30:00Z"
    assert config["today"] == "2026-07-22"
    assert config["calendar_years"] == [2025, 2026, 2027, 2028]
    assert config["lookup"] == {
        "min_date": "2026-01-01",
        "max_date": "2028-12-31",
    }
    assert config["search_year"] == 2026

    expected_files = {
        OUTPUT_MARKER,
        "calendars/complete.ics",
        "calendars/top-100.ics",
        "data/config.json",
        "data/search-2026.json",
        "data/calendar-2025.json",
        "data/calendar-2026.json",
        "data/calendar-2027.json",
        "data/calendar-2028.json",
    }
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert actual_files == expected_files
    assert _read_json(output / "data" / "config.json") == config


def test_calendar_json_contains_complete_ordered_daily_data(built_site) -> None:
    output, _ = built_site
    payload = _read_json(output / "data" / "calendar-2026.json")

    assert payload["schema_version"] == 1
    assert payload["year"] == 2026
    assert payload["event_count"] == 228
    assert [item["date"] for item in payload["days"]] == sorted(
        item["date"] for item in payload["days"]
    )
    assert all(item["date"].startswith("2026-") for item in payload["days"])

    dormition = next(
        item for item in payload["days"] if item["date"] == "2026-08-15"
    )
    assert "Κοίμηση της Θεοτόκου" in dormition["observances"]
    assert "Μαρία" in dormition["namedays"]
    assert "Παναγιώτης" in dormition["namedays"]

    raw_payload = (output / "data" / "calendar-2026.json").read_bytes()
    assert not raw_payload.startswith(b"\xef\xbb\xbf")
    assert "Κοίμηση της Θεοτόκου".encode("utf-8") in raw_payload


def test_search_index_contains_names_and_feasts_for_the_current_year(
    built_site,
) -> None:
    output, _ = built_site
    payload = _read_json(output / "data" / "search-2026.json")

    assert payload["schema_version"] == 1
    assert payload["year"] == 2026
    assert payload["entry_count"] == 664
    assert len(payload["entries"]) == 664
    assert payload["entries"] == sorted(
        payload["entries"],
        key=lambda item: (item["normalized"], item["kind"], item["id"]),
    )
    assert all(item["dates"] for item in payload["entries"])

    george = next(item for item in payload["entries"] if item["label"] == "Γιώργος")
    assert george == {
        "id": "georgios",
        "kind": "name",
        "label": "Γιώργος",
        "normalized": "γιωργοσ",
        "dates": ["2026-04-23"],
        "popularity": 100,
    }
    dormition = next(
        item
        for item in payload["entries"]
        if item["label"] == "Κοίμηση της Θεοτόκου"
    )
    assert dormition == {
        "id": "dormition",
        "kind": "feast",
        "label": "Κοίμηση της Θεοτόκου",
        "normalized": "κοιμηση τησ θεοτοκου",
        "dates": ["2026-08-15"],
        "popularity": None,
    }


def test_subscription_calendars_have_the_expected_ranges_and_identities(
    built_site,
) -> None:
    output, config = built_site
    complete_path = output / "calendars" / "complete.ics"
    popular_path = output / "calendars" / "top-100.ics"
    complete = Calendar.from_ical(complete_path.read_bytes())
    popular = Calendar.from_ical(popular_path.read_bytes())
    complete_events = _events(complete)
    popular_events = _events(popular)

    assert str(complete["UID"]) == (
        "urn:uuid:b484af8b-559e-5081-a6be-8b69bc217873"
    )
    assert str(popular["UID"]) == (
        "urn:uuid:1780acd7-b007-5b37-992b-5dd23ffe7a35"
    )
    assert str(complete["NAME"]) == "Grecal — Greek Orthodox Calendar"
    assert str(popular["NAME"]) == "Grecal — Popular Namedays"
    assert len(complete_events) == 917
    assert len(popular_events) == 304
    assert {event.decoded("DTSTART").year for event in complete_events} == {
        2025,
        2026,
        2027,
        2028,
    }
    assert {event.decoded("DTSTART").year for event in popular_events} == {
        2025,
        2026,
        2027,
        2028,
    }

    dormition = next(
        event
        for event in complete_events
        if event.decoded("DTSTART") == date(2026, 8, 15)
    )
    assert str(dormition["UID"]) == (
        "urn:uuid:fd5eabe4-6772-5832-ba47-1290876b29ff"
    )
    assert "Κοίμηση της Θεοτόκου" in str(dormition["SUMMARY"])
    assert all(
        "Κοίμηση της Θεοτόκου" not in str(event["SUMMARY"])
        for event in popular_events
    )

    complete_config = config["subscriptions"]["complete"]
    popular_config = config["subscriptions"]["top_100"]
    assert complete_config["event_count"] == len(complete_events)
    assert popular_config["event_count"] == len(popular_events)
    assert complete_config["bytes"] == complete_path.stat().st_size
    assert popular_config["bytes"] == popular_path.stat().st_size


def test_builder_replaces_only_recognized_generated_output(tmp_path: Path) -> None:
    output = tmp_path / "_site"
    build_site(output, today=BUILD_DAY, generated_at=BUILD_STAMP)
    stale = output / "data" / "stale.json"
    stale.write_text("{}", encoding="utf-8")

    build_site(output, today=BUILD_DAY, generated_at=BUILD_STAMP)

    assert not stale.exists()

    unrecognized = tmp_path / "important"
    unrecognized.mkdir()
    (unrecognized / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="refusing to replace unrecognized"):
        build_site(
            unrecognized,
            today=BUILD_DAY,
            generated_at=BUILD_STAMP,
        )
    assert (unrecognized / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_builder_rejects_ranges_outside_grecal_support(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="supported years 1900-2100"):
        build_site(tmp_path / "_site", today=date(2099, 1, 1))


def test_site_builder_cli_reports_generated_artifacts(
    tmp_path: Path,
    capsys,
) -> None:
    output = tmp_path / "_site"

    assert main(["--today", "2026-07-22", "--output", str(output)]) == 0

    report = capsys.readouterr().out
    assert f"Generated site artifacts: {output}" in report
    assert "Calendar data: 2025-2028" in report
    assert "Search index: 2026" in report
    assert "Subscription: calendars/complete.ics" in report
    assert "Subscription: calendars/top-100.ics" in report
