#!/usr/bin/env python3
"""Generate Grecal's static website data and subscription calendars."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grecal import (  # noqa: E402
    Catalog,
    build_calendar,
    generate_namedays,
    generate_observances,
    load_catalog,
    normalize_search_text,
    validate_catalog,
)
from grecal.easter import MAX_YEAR, MIN_YEAR  # noqa: E402


SCHEMA_VERSION = 1
OUTPUT_MARKER = ".grecal-site-output"
ATHENS = ZoneInfo("Europe/Athens")
DEFAULT_FEASTS_PATH = PROJECT_ROOT / "data" / "feasts.yaml"
DEFAULT_NAMES_PATH = PROJECT_ROOT / "data" / "names.yaml"
DEFAULT_OBSERVANCES_PATH = PROJECT_ROOT / "data" / "observances.yaml"
DEFAULT_WEB_PATH = PROJECT_ROOT / "web"
FRONTEND_FILES = ("styles.css", "app.js", "branding.json")


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"expected an ISO date in YYYY-MM-DD format: {value}"
        ) from exc


def _utc_timestamp(value: datetime | None = None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    return stamp.astimezone(timezone.utc).replace(microsecond=0)


def _iso_timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_branding() -> dict[str, Any]:
    source = DEFAULT_WEB_PATH / "branding.json"
    if not source.is_file():
        raise ValueError(f"missing website branding file: {source}")
    try:
        branding = json.loads(source.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"invalid website branding file: {source}") from exc

    if not isinstance(branding, dict) or branding.get("schema_version") != 1:
        raise ValueError("website branding uses an unsupported schema")
    for key in ("default_language", "language_storage_key", "site_name"):
        if not isinstance(branding.get(key), str) or not branding[key].strip():
            raise ValueError(f"website branding requires a non-empty {key}")

    wordmark = branding.get("wordmark")
    if not isinstance(wordmark, dict):
        raise ValueError("website branding requires wordmark settings")
    if not isinstance(wordmark.get("primary"), str) or not wordmark["primary"].strip():
        raise ValueError("website branding requires a non-empty wordmark primary")
    if not isinstance(wordmark.get("suffix"), str):
        raise ValueError("website branding requires a wordmark suffix string")

    repository = branding.get("repository")
    if not isinstance(repository, dict):
        raise ValueError("website branding requires repository settings")
    for key in ("label", "url"):
        if not isinstance(repository.get(key), str) or not repository[key].strip():
            raise ValueError(f"website branding requires a non-empty repository {key}")

    subscriptions = branding.get("subscriptions")
    if not isinstance(subscriptions, dict):
        raise ValueError("website branding requires subscription settings")
    for selection in ("complete", "top_100"):
        details = subscriptions.get(selection)
        if not isinstance(details, dict):
            raise ValueError(
                f"website branding requires {selection!r} subscription settings"
            )
        for key in ("calendar_id", "name", "description"):
            if not isinstance(details.get(key), str) or not details[key].strip():
                raise ValueError(
                    f"website branding subscription {selection!r} "
                    f"requires a non-empty {key}"
                )
        try:
            details["description"].format(years="YYYY–YYYY")
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"website branding subscription {selection!r} "
                "has an invalid description template"
            ) from exc

    locales = branding.get("locales")
    default_language = branding["default_language"]
    if not isinstance(locales, dict) or default_language not in locales:
        raise ValueError("website branding requires its default locale")
    for language in ("el", "en"):
        if language not in locales:
            raise ValueError(f"website branding requires the {language!r} locale")
    for language, localized in locales.items():
        if not isinstance(language, str) or not isinstance(localized, dict):
            raise ValueError("website branding locales must be objects")
        for key in ("title", "description", "home_label", "noscript_message"):
            if not isinstance(localized.get(key), str) or not localized[key].strip():
                raise ValueError(
                    f"website branding locale {language!r} requires a non-empty {key}"
                )
    return branding


def _render_index(destination: Path, branding: Mapping[str, Any]) -> None:
    source = DEFAULT_WEB_PATH / "index.html"
    if not source.is_file():
        raise ValueError(f"missing website source file: {source}")
    default_language = branding["default_language"]
    localized = branding["locales"][default_language]
    replacements = {
        "DEFAULT_LANGUAGE": default_language,
        "DEFAULT_TITLE": localized["title"],
        "DEFAULT_DESCRIPTION": localized["description"],
        "DEFAULT_HOME_LABEL": localized["home_label"],
        "DEFAULT_NOSCRIPT_MESSAGE": localized["noscript_message"],
        "WORDMARK_PRIMARY": branding["wordmark"]["primary"],
        "WORDMARK_SUFFIX": branding["wordmark"]["suffix"],
        "REPOSITORY_LABEL": branding["repository"]["label"],
        "REPOSITORY_URL": branding["repository"]["url"],
    }
    rendered = source.read_text(encoding="utf-8")
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", escape(value, quote=True))
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("website index contains an unknown branding placeholder")
    (destination / "index.html").write_text(rendered, encoding="utf-8")


def _copy_frontend(destination: Path, branding: Mapping[str, Any]) -> None:
    for filename in FRONTEND_FILES:
        source = DEFAULT_WEB_PATH / filename
        if not source.is_file():
            raise ValueError(f"missing website source file: {source}")
        shutil.copy2(source, destination / filename)
    _render_index(destination, branding)


def _calendar_year_payload(
    year: int,
    grouped_names: Mapping[date, Sequence[str]],
    grouped_observances: Mapping[date, Sequence[str]],
) -> dict[str, Any]:
    days = []
    occupied_days = sorted(
        day
        for day in set(grouped_names) | set(grouped_observances)
        if day.year == year
    )
    for day in occupied_days:
        days.append(
            {
                "date": day.isoformat(),
                "namedays": list(grouped_names.get(day, ())),
                "observances": list(grouped_observances.get(day, ())),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "year": year,
        "event_count": len(days),
        "days": days,
    }


def _search_index_payload(
    catalog: Catalog,
    year: int,
    grouped_names: Mapping[date, Sequence[str]],
    grouped_observances: Mapping[date, Sequence[str]],
) -> dict[str, Any]:
    dates_by_name: dict[str, list[str]] = defaultdict(list)
    for day, names in grouped_names.items():
        if day.year != year:
            continue
        for name in names:
            dates_by_name[name].append(day.isoformat())

    dates_by_observance: dict[str, list[str]] = defaultdict(list)
    for day, titles in grouped_observances.items():
        if day.year != year:
            continue
        for title in titles:
            dates_by_observance[title].append(day.isoformat())

    entries: list[dict[str, Any]] = []
    for nameday in catalog.namedays:
        for name in nameday.names:
            entries.append(
                {
                    "id": nameday.id,
                    "kind": "name",
                    "label": name,
                    "normalized": normalize_search_text(name),
                    "dates": sorted(dates_by_name[name]),
                    "popularity": nameday.popularity,
                }
            )
    for observance in catalog.observances:
        entries.append(
            {
                "id": observance.id,
                "kind": "feast",
                "label": observance.title,
                "normalized": normalize_search_text(observance.title),
                "dates": sorted(dates_by_observance[observance.title]),
                "popularity": None,
            }
        )
    entries.sort(
        key=lambda item: (
            item["normalized"],
            item["kind"],
            item["id"],
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "year": year,
        "entry_count": len(entries),
        "entries": entries,
    }


def _write_subscription(
    path: Path,
    grouped_names: Mapping[date, Sequence[str]],
    grouped_observances: Mapping[date, Sequence[str]],
    *,
    generated_at: datetime,
    calendar_id: str,
    calendar_name: str,
    calendar_description: str,
) -> tuple[int, int]:
    calendar = build_calendar(
        grouped_names,
        grouped_observances=grouped_observances,
        generated_at=generated_at,
        calendar_id=calendar_id,
        calendar_name=calendar_name,
        calendar_description=calendar_description,
    )
    payload = calendar.to_ical()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    event_count = len(set(grouped_names) | set(grouped_observances))
    return event_count, len(payload)


def _replace_output(staging: Path, output: Path) -> None:
    if output.exists():
        marker = output / OUTPUT_MARKER
        if not output.is_dir() or not marker.is_file():
            raise ValueError(
                f"refusing to replace unrecognized output directory: {output}"
            )
        shutil.rmtree(output)
    staging.replace(output)


def build_site(
    output: Path,
    *,
    today: date,
    generated_at: datetime | None = None,
    catalog: Catalog | None = None,
) -> dict[str, Any]:
    """Build static JSON and ICS artifacts into ``output``."""

    from_year = today.year - 1
    to_year = today.year + 2
    if not MIN_YEAR <= from_year <= today.year <= to_year <= MAX_YEAR:
        raise ValueError(
            "website range must remain within "
            f"Grecal's supported years {MIN_YEAR}-{MAX_YEAR}"
        )

    source = catalog or load_catalog(
        DEFAULT_FEASTS_PATH,
        DEFAULT_NAMES_PATH,
        DEFAULT_OBSERVANCES_PATH,
    )
    validate_catalog(source)
    branding = _load_branding()
    stamp = _utc_timestamp(generated_at)
    grouped_names = generate_namedays(source, from_year, to_year)
    grouped_observances = generate_observances(source, from_year, to_year)
    top_names = generate_namedays(source, from_year, to_year, top=100)

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{output.name}-",
            dir=output.parent,
        )
    )
    try:
        _copy_frontend(staging, branding)
        (staging / OUTPUT_MARKER).write_text(
            "Generated by scripts/build_site.py.\n",
            encoding="utf-8",
        )
        data_directory = staging / "data"
        for year in range(from_year, to_year + 1):
            _write_json(
                data_directory / f"calendar-{year}.json",
                _calendar_year_payload(
                    year,
                    grouped_names,
                    grouped_observances,
                ),
            )
        _write_json(
            data_directory / f"search-{today.year}.json",
            _search_index_payload(
                source,
                today.year,
                grouped_names,
                grouped_observances,
            ),
        )

        years = f"{from_year}–{to_year}"
        complete_branding = branding["subscriptions"]["complete"]
        popular_branding = branding["subscriptions"]["top_100"]
        complete_events, complete_bytes = _write_subscription(
            staging / "calendars" / "complete.ics",
            grouped_names,
            grouped_observances,
            generated_at=stamp,
            calendar_id=complete_branding["calendar_id"],
            calendar_name=complete_branding["name"],
            calendar_description=complete_branding["description"].format(
                years=years
            ),
        )
        popular_events, popular_bytes = _write_subscription(
            staging / "calendars" / "top-100.ics",
            top_names,
            {},
            generated_at=stamp,
            calendar_id=popular_branding["calendar_id"],
            calendar_name=popular_branding["name"],
            calendar_description=popular_branding["description"].format(
                years=years
            ),
        )

        config: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": _iso_timestamp(stamp),
            "today": today.isoformat(),
            "current_year": today.year,
            "calendar_years": list(range(from_year, to_year + 1)),
            "lookup": {
                "min_date": date(today.year, 1, 1).isoformat(),
                "max_date": date(to_year, 12, 31).isoformat(),
            },
            "search_year": today.year,
            "subscriptions": {
                "complete": {
                    "path": "calendars/complete.ics",
                    "calendar_id": complete_branding["calendar_id"],
                    "from_year": from_year,
                    "to_year": to_year,
                    "event_count": complete_events,
                    "bytes": complete_bytes,
                },
                "top_100": {
                    "path": "calendars/top-100.ics",
                    "calendar_id": popular_branding["calendar_id"],
                    "from_year": from_year,
                    "to_year": to_year,
                    "event_count": popular_events,
                    "bytes": popular_bytes,
                },
            },
        }
        _write_json(data_directory / "config.json", config)
        _replace_output(staging, output)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return config


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build static Grecal website data and subscriptions.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("_site"),
        help="generated site directory (default: _site)",
    )
    parser.add_argument(
        "--today",
        type=_parse_date,
        default=datetime.now(ATHENS).date(),
        help="build date in YYYY-MM-DD form (default: today in Athens)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _argument_parser()
    args = parser.parse_args(argv)
    try:
        config = build_site(args.output, today=args.today)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{parser.prog}: error: {exc}\n")

    years = config["calendar_years"]
    print(f"Generated site artifacts: {args.output.resolve()}")
    print(f"Calendar data: {years[0]}-{years[-1]}")
    print(f"Search index: {config['search_year']}")
    for subscription in config["subscriptions"].values():
        print(
            f"Subscription: {subscription['path']} "
            f"({subscription['event_count']} events, "
            f"{subscription['bytes']} bytes)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
