import json
from datetime import date, datetime, timezone
from pathlib import Path

from icalendar import Calendar
import pytest

from grecal import (
    Catalog,
    Feast,
    FeastType,
    Nameday,
    generate_namedays,
    load_catalog,
)
from scripts.build_site import (
    OUTPUT_MARKER,
    _calendar_year_payload,
    _generate_commemorations,
    _search_index_payload,
    build_site,
    main,
)


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
        "app.js",
        "branding.json",
        "calendars/complete.ics",
        "calendars/top-100.ics",
        "data/config.json",
        "data/search-2026.json",
        "data/calendar-2025.json",
        "data/calendar-2026.json",
        "data/calendar-2027.json",
        "data/calendar-2028.json",
        "index.html",
        "styles.css",
    }
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert actual_files == expected_files
    assert _read_json(output / "data" / "config.json") == config


def test_site_builder_copies_the_frontend(built_site) -> None:
    output, _ = built_site
    index = (output / "index.html").read_text(encoding="utf-8")
    styles = (output / "styles.css").read_text(encoding="utf-8")
    script = (output / "app.js").read_text(encoding="utf-8")
    branding = _read_json(output / "branding.json")

    assert f'<html lang="{branding["default_language"]}">' in index
    assert branding["site_name"] in index
    assert "{{" not in index
    assert "brand-mark" not in index
    assert 'data-language="el"' in index
    assert 'data-language="en"' in index
    assert branding["repository"]["url"] in index
    assert (
        'target="_blank" rel="noopener noreferrer">'
        f'{branding["repository"]["label"]}</a>'
    ) in index
    assert 'id="agenda"' in index
    assert 'id="date-lookup"' in index
    assert 'id="search"' in index
    assert 'id="subscriptions"' in index
    assert "tool-number" not in index
    assert 'src="app.js"' in index
    assert 'href="styles.css"' in index
    assert "--color-ink" in styles
    assert ".language-switch" in styles
    assert ".event-group.is-feast" in styles
    assert "padding: 1.75rem 0 2.75rem" in styles
    assert 'loadJson("branding.json")' in script
    assert 'loadJson("data/config.json")' in script
    assert 'fetch(path, { cache: "no-store" })' in script
    assert "TRANSLATIONS" in script
    assert "state.branding.language_storage_key" in script
    assert "damerauLevenshtein" in script
    assert "transliterateGreek" in script
    assert "searchFormsForEntry" in script
    assert "Γιώργος ή Giorgos" in index
    assert "data.commemorations" in script
    assert 'appendEvents(container, dayData(isoDate), t("noEventsOnDate"), true)' in script
    assert 'scrollTo({ top: today.offsetTop, behavior: behavior })' in script
    assert "position: relative" in styles
    assert "Europe/Athens" in script


def test_calendar_json_contains_complete_ordered_daily_data(built_site) -> None:
    output, _ = built_site
    payload = _read_json(output / "data" / "calendar-2026.json")

    assert payload["schema_version"] == 1
    assert payload["year"] == 2026
    assert payload["event_count"] == 269
    assert [item["date"] for item in payload["days"]] == sorted(
        item["date"] for item in payload["days"]
    )
    assert all(item["date"].startswith("2026-") for item in payload["days"])

    dormition = next(
        item for item in payload["days"] if item["date"] == "2026-08-15"
    )
    assert "Κοίμηση της Θεοτόκου" in dormition["observances"]
    assert "Κοίμηση της Υπεραγίας Θεοτόκου" not in dormition["commemorations"]
    assert "Μαρία" in dormition["namedays"]
    assert "Παναγιώτης" in dormition["namedays"]

    transfiguration = next(
        item for item in payload["days"] if item["date"] == "2026-08-06"
    )
    assert transfiguration["observances"] == ["Μεταμόρφωση του Σωτήρος"]
    assert transfiguration["commemorations"] == []

    today = next(item for item in payload["days"] if item["date"] == "2026-07-22")
    assert "Αγία Μαρία η Μαγδαληνή" in today["commemorations"]

    archangels = next(
        item for item in payload["days"] if item["date"] == "2026-11-08"
    )
    archangels_title = (
        "Σύναξη Αρχαγγέλων Μιχαήλ και Γαβριήλ "
        "και λοιπών Ασωμάτων Δυνάμεων"
    )
    assert archangels["commemorations"].count(archangels_title) == 1

    cyprian_and_justina = next(
        item for item in payload["days"] if item["date"] == "2026-10-02"
    )
    assert {
        "Κυπριανός",
        "Κυπριανή",
        "Ιουστίνη",
        "Ιούστα",
    } <= set(cyprian_and_justina["namedays"])
    assert cyprian_and_justina["commemorations"] == [
        "Αγίων Κυπριανού επισκόπου Καρθαγένης και Ιουστίνης της παρθένου"
    ]

    porphyrios = next(
        item for item in payload["days"] if item["date"] == "2026-12-02"
    )
    assert {"Πορφύριος", "Πορφυρία", "Πορφυρούλα"} <= set(
        porphyrios["namedays"]
    )
    assert "Όσιος Πορφύριος ο Καυσοκαλυβίτης" in porphyrios[
        "commemorations"
    ]

    judas_thaddeus = next(
        item for item in payload["days"] if item["date"] == "2026-06-19"
    )
    assert "Ιούδας" in judas_thaddeus["namedays"]
    assert "Αγίου Ιούδα του Θαδδαίου" in judas_thaddeus["commemorations"]

    raw_payload = (output / "data" / "calendar-2026.json").read_bytes()
    assert not raw_payload.startswith(b"\xef\xbb\xbf")
    assert "Κοίμηση της Θεοτόκου".encode("utf-8") in raw_payload


def test_saint_george_is_a_commemoration_and_keeps_its_transfer_rule() -> None:
    root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(
        root / "data" / "feasts.yaml",
        root / "data" / "names.yaml",
        root / "data" / "observances.yaml",
    )
    grouped = _generate_commemorations(catalog, 2024, 2024)

    title = "Άγιος Γεώργιος ο Μεγαλομάρτυρας"
    assert title not in grouped.get(date(2024, 4, 23), ())
    assert title in grouped[date(2024, 5, 6)]


def test_future_year_date_lookup_data_contains_every_name_variant(built_site) -> None:
    output, _ = built_site
    payload = _read_json(output / "data" / "calendar-2027.json")
    new_year = next(
        item for item in payload["days"] if item["date"] == "2027-01-01"
    )

    assert {
        "Βάσια",
        "Βιβή",
        "Βίβιαν",
        "Βασιλίνα",
        "Βασίλης",
        "Βάσος",
        "Βασίλας",
        "Τηλεμάχη",
        "Εμμέλεια",
        "Εμμελεία",
    } <= set(new_year["namedays"])
    assert set(new_year["primary_namedays"]) == set(new_year["namedays"]) - {
        "Εμμέλεια",
        "Εμμελεία",
    }


def test_search_index_contains_names_and_feasts_for_the_current_year(
    built_site,
) -> None:
    output, _ = built_site
    payload = _read_json(output / "data" / "search-2026.json")

    assert payload["schema_version"] == 1
    assert payload["year"] == 2026
    assert payload["entry_count"] == 1831
    assert len(payload["entries"]) == 1831
    assert payload["entries"] == sorted(
        payload["entries"],
        key=lambda item: (item["normalized"], item["kind"], item["id"]),
    )
    assert all(
        item["dates"] or item["id"] == "kassianos"
        for item in payload["entries"]
    )

    george = next(item for item in payload["entries"] if item["label"] == "Γιώργος")
    assert george == {
        "id": "georgios",
        "kind": "name",
        "label": "Γιώργος",
        "normalized": "γιωργοσ",
        "dates": ["2026-04-23"],
        "popularity": 100,
    }
    anastasia = next(
        item for item in payload["entries"] if item["label"] == "Αναστασία"
    )
    anastasios = next(
        item for item in payload["entries"] if item["label"] == "Αναστάσιος"
    )
    assert anastasia["dates"] == [
        "2026-04-12",
        "2026-01-22",
        "2026-10-29",
        "2026-12-22",
    ]
    assert anastasios["dates"] == [
        "2026-04-12",
        "2026-01-22",
        "2026-09-17",
    ]
    kassiani = next(
        item for item in payload["entries"] if item["label"] == "Κασσιανή"
    )
    kassianos = next(
        item for item in payload["entries"] if item["label"] == "Κασσιανός"
    )
    assert kassiani["dates"] == ["2026-09-07"]
    assert kassianos["dates"] == []
    maria = next(item for item in payload["entries"] if item["label"] == "Μαρία")
    eystathios = next(
        item for item in payload["entries"] if item["label"] == "Ευστάθιος"
    )
    assert maria["dates"] == [
        "2026-08-15",
        "2026-02-02",
        "2026-11-21",
    ]
    assert eystathios["dates"] == ["2026-09-20", "2026-02-21"]
    primary_first = {
        "Τίτος": ["2026-08-25", "2026-04-02"],
        "Σωκράτης": ["2026-10-21", "2026-04-10"],
        "Θωμάς": ["2026-04-19", "2026-10-06"],
        "Ιάκωβος": ["2026-04-30", "2026-10-23"],
        "Θεοχάρης": ["2026-08-20", "2026-04-15"],
        "Καλή": ["2026-05-15", "2026-04-18", "2026-05-22"],
    }
    for label, dates in primary_first.items():
        entry = next(
            item for item in payload["entries"] if item["label"] == label
        )
        assert entry["dates"] == dates
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
    assert all(
        item["label"] != "Αγία Μαρία η Μαγδαληνή"
        for item in payload["entries"]
    )


def test_commemorations_resolve_from_their_mapped_feast_rules(
    tmp_path: Path,
) -> None:
    catalog = Catalog(
        feasts=(Feast("saint", FeastType.FIXED, month=7, day=22),),
        namedays=(),
    )
    path = tmp_path / "commemorations.yaml"

    path.write_text(
        "commemorations:\n"
        "  - id: saint\n"
        "    title: Saint title\n"
        "feasts:\n"
        "  saint:\n"
        "    - saint\n",
        encoding="utf-8",
    )
    grouped = _generate_commemorations(catalog, 2026, 2026, path=path)

    assert grouped == {date(2026, 7, 22): ("Saint title",)}


def test_multi_date_name_payload_marks_and_orders_primary_feast() -> None:
    catalog = Catalog(
        feasts=(
            Feast("christmas", FeastType.FIXED, month=12, day=25),
            Feast("saint_christina", FeastType.FIXED, month=7, day=24),
        ),
        namedays=(
            Nameday(
                "christina",
                "christmas",
                98,
                ("Χριστίνα",),
                ("saint_christina",),
            ),
        ),
    )
    grouped_names = generate_namedays(catalog, 2026, 2026)

    calendar_payload = _calendar_year_payload(
        catalog,
        2026,
        grouped_names,
        {},
    )
    days = {item["date"]: item for item in calendar_payload["days"]}
    assert days["2026-12-25"]["primary_namedays"] == ["Χριστίνα"]
    assert days["2026-07-24"]["primary_namedays"] == []
    assert days["2026-07-24"]["commemorations"] == []

    search_payload = _search_index_payload(
        catalog,
        2026,
        grouped_names,
        {},
    )
    assert search_payload["entries"][0]["dates"] == [
        "2026-12-25",
        "2026-07-24",
    ]


def test_subscription_calendars_have_the_expected_ranges_and_identities(
    built_site,
) -> None:
    output, config = built_site
    complete_path = output / "calendars" / "complete.ics"
    popular_path = output / "calendars" / "top-100.ics"
    complete = Calendar.from_ical(complete_path.read_bytes())
    popular = Calendar.from_ical(popular_path.read_bytes())
    branding = _read_json(output / "branding.json")
    complete_events = _events(complete)
    popular_events = _events(popular)

    assert str(complete["UID"]) == (
        "urn:uuid:b484af8b-559e-5081-a6be-8b69bc217873"
    )
    assert str(popular["UID"]) == (
        "urn:uuid:1780acd7-b007-5b37-992b-5dd23ffe7a35"
    )
    assert str(complete["NAME"]) == branding["subscriptions"]["complete"]["name"]
    assert str(popular["NAME"]) == branding["subscriptions"]["top_100"]["name"]
    assert len(complete_events) == 1085
    assert len(popular_events) == 436
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
