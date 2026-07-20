"""Selection, grouping, iCalendar generation, and CLI."""

from __future__ import annotations

import argparse
import hashlib
import sysconfig
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from icalendar import Calendar, Event

from .easter import MAX_YEAR, MIN_YEAR, orthodox_easter
from .models import Catalog, Nameday
from .parser import DataValidationError, load_catalog
from .rules import CustomRule, UnsupportedFeastRuleError, resolve_feast_date


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _default_data_path(filename: str) -> Path:
    """Locate YAML data in a source checkout or an installed distribution."""

    source_path = PROJECT_ROOT / "data" / filename
    if source_path.is_file():
        return source_path
    installed_path = (
        Path(sysconfig.get_path("data")) / "share" / "grecal" / filename
    )
    if installed_path.is_file():
        return installed_path
    return source_path


DEFAULT_FEASTS_PATH = _default_data_path("feasts.yaml")
DEFAULT_NAMES_PATH = _default_data_path("names.yaml")
DEFAULT_OBSERVANCES_PATH = _default_data_path("observances.yaml")


@dataclass(frozen=True)
class _YearStatistics:
    year: int
    identity_groups: int
    display_names: int
    church_feasts: int
    calendar_events: int


def select_namedays(
    namedays: Iterable[Nameday],
    *,
    top: int | None = None,
    min_popularity: int | None = None,
) -> tuple[Nameday, ...]:
    """Select entries by rank or minimum popularity; no filters means all."""

    if top is not None and min_popularity is not None:
        raise ValueError("top and min_popularity are mutually exclusive")
    if top is not None and top < 1:
        raise ValueError("top must be at least 1")
    if min_popularity is not None and not 0 <= min_popularity <= 100:
        raise ValueError("min_popularity must be between 0 and 100")

    ordered = sorted(namedays, key=lambda item: (-item.popularity, item.id))
    if top is not None:
        return tuple(ordered[:top])
    if min_popularity is not None:
        return tuple(
            item for item in ordered if item.popularity >= min_popularity
        )
    return tuple(ordered)


def generate_namedays(
    catalog: Catalog,
    from_year: int,
    to_year: int,
    *,
    top: int | None = None,
    min_popularity: int | None = None,
    custom_rules: Mapping[str, CustomRule] | None = None,
) -> dict[date, tuple[str, ...]]:
    """Resolve and group selected names, returning at most one group per day."""

    if not MIN_YEAR <= from_year <= to_year <= MAX_YEAR:
        raise ValueError(
            f"year range must satisfy {MIN_YEAR} <= from_year <= to_year <= {MAX_YEAR}"
        )
    selected = select_namedays(
        catalog.namedays, top=top, min_popularity=min_popularity
    )
    feasts = catalog.feast_map()
    grouped: dict[date, list[str]] = defaultdict(list)
    for year in range(from_year, to_year + 1):
        easter = orthodox_easter(year)
        for nameday in selected:
            celebration = resolve_feast_date(
                feasts[nameday.feast],
                year,
                easter,
                custom_rules=custom_rules,
            )
            for name in nameday.names:
                if name not in grouped[celebration]:
                    grouped[celebration].append(name)
    return {day: tuple(names) for day, names in sorted(grouped.items())}


def generate_observances(
    catalog: Catalog,
    from_year: int,
    to_year: int,
    *,
    custom_rules: Mapping[str, CustomRule] | None = None,
) -> dict[date, tuple[str, ...]]:
    """Resolve and group church observance titles by date."""

    if not MIN_YEAR <= from_year <= to_year <= MAX_YEAR:
        raise ValueError(
            f"year range must satisfy {MIN_YEAR} <= from_year <= to_year <= {MAX_YEAR}"
        )
    feasts = catalog.feast_map()
    grouped: dict[date, list[str]] = defaultdict(list)
    for year in range(from_year, to_year + 1):
        easter = orthodox_easter(year)
        for observance in catalog.observances:
            celebration = resolve_feast_date(
                feasts[observance.feast],
                year,
                easter,
                custom_rules=custom_rules,
            )
            if observance.title not in grouped[celebration]:
                grouped[celebration].append(observance.title)
    return {day: tuple(titles) for day, titles in sorted(grouped.items())}


def _event_uid(day: date, names: Sequence[str]) -> str:
    identity = f"{day.isoformat()}|{'|'.join(names)}".encode("utf-8")
    digest = hashlib.sha256(identity).hexdigest()[:24]
    return f"{digest}@grecal"


def build_calendar(
    grouped_names: Mapping[date, Sequence[str]],
    *,
    grouped_observances: Mapping[date, Sequence[str]] | None = None,
    generated_at: datetime | None = None,
) -> Calendar:
    """Build a UTF-8 calendar with at most one all-day event per date."""

    stamp = generated_at or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    calendar = Calendar()
    calendar.add("prodid", "-//Grecal//Greek Orthodox Calendar//EL")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")

    observances = grouped_observances or {}
    days = sorted(set(grouped_names) | set(observances))
    for day in days:
        names = grouped_names.get(day, ())
        titles = observances.get(day, ())
        title_text = " · ".join(titles)
        names_text = ", ".join(names)
        summary = (
            f"{title_text} — {names_text}"
            if title_text and names_text
            else title_text or names_text
        )
        event = Event()
        event.add("uid", _event_uid(day, (*titles, *names)))
        event.add("dtstamp", stamp.astimezone(timezone.utc))
        event.add("summary", summary)
        event.add("dtstart", day)
        event.add("dtend", day + timedelta(days=1))
        calendar.add_component(event)
    return calendar


def write_calendar(calendar: Calendar, output_path: Path) -> None:
    """Serialize an iCalendar object as UTF-8 bytes."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(calendar.to_ical())


def _year_statistics(
    selected_namedays: Sequence[Nameday],
    grouped_names: Mapping[date, Sequence[str]],
    grouped_observances: Mapping[date, Sequence[str]],
    from_year: int,
    to_year: int,
    *,
    church_feast_count: int,
) -> tuple[_YearStatistics, ...]:
    identity_groups = len(selected_namedays)
    display_names = sum(len(item.names) for item in selected_namedays)
    event_days = set(grouped_names) | set(grouped_observances)
    return tuple(
        _YearStatistics(
            year=year,
            identity_groups=identity_groups,
            display_names=display_names,
            church_feasts=church_feast_count,
            calendar_events=sum(day.year == year for day in event_days),
        )
        for year in range(from_year, to_year + 1)
    )


def _selection_label(args: argparse.Namespace) -> str:
    if args.feasts_only:
        return "church feasts only"
    if args.top is not None:
        label = f"top {args.top} nameday groups"
    elif args.min_popularity is not None:
        label = f"nameday popularity >= {args.min_popularity}"
    else:
        label = "all nameday groups"
    return f"{label} + church feasts" if args.include_feasts else label


def _print_generation_summary(
    output_path: Path,
    selection_label: str,
    statistics: Sequence[_YearStatistics],
) -> None:
    headers = (
        "Year",
        "Identity groups",
        "Display names",
        "Church feasts",
        "Calendar events",
    )
    rows: list[tuple[str, ...]] = [
        (
            str(item.year),
            str(item.identity_groups),
            str(item.display_names),
            str(item.church_feasts),
            str(item.calendar_events),
        )
        for item in statistics
    ]
    totals = tuple(
        sum(getattr(item, field) for item in statistics)
        for field in (
            "identity_groups",
            "display_names",
            "church_feasts",
            "calendar_events",
        )
    )
    rows.append(("Total occurrences", *(str(value) for value in totals)))
    if len(statistics) > 1:
        rows.append(
            (
                "Average/year",
                *(f"{value / len(statistics):.1f}" for value in totals),
            )
        )

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def format_row(row: Sequence[str]) -> str:
        return "  ".join(
            value.ljust(widths[index])
            if index == 0
            else value.rjust(widths[index])
            for index, value in enumerate(row)
        )

    years = (
        str(statistics[0].year)
        if len(statistics) == 1
        else f"{statistics[0].year}-{statistics[-1].year}"
    )
    print(f"Generated: {output_path} ({output_path.stat().st_size:,} bytes)")
    print(f"Years: {years}")
    print(f"Selection: {selection_label}")
    print()
    print(format_row(headers))
    print(format_row(tuple("-" * width for width in widths)))
    for row in rows:
        print(format_row(row))


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an iCalendar of Greek Orthodox namedays and feasts."
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all",
        action="store_true",
        help="include every nameday identity group",
    )
    selection.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="include the N highest-scoring identity groups (N >= 1)",
    )
    selection.add_argument(
        "--min-popularity",
        type=int,
        metavar="N",
        help="include groups with popularity >= N (0-100)",
    )
    selection.add_argument(
        "--feasts-only",
        action="store_true",
        help="include church feasts without namedays",
    )
    parser.add_argument(
        "--include-feasts",
        action="store_true",
        help="include church feasts alongside the selected namedays",
    )
    current_year = date.today().year
    parser.add_argument("--from-year", type=int, default=current_year)
    parser.add_argument("--to-year", type=int)
    parser.add_argument("--output", type=Path, default=Path("grecal.ics"))
    parser.add_argument(
        "--feasts",
        type=Path,
        default=DEFAULT_FEASTS_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--names",
        type=Path,
        default=DEFAULT_NAMES_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--observances",
        type=Path,
        default=DEFAULT_OBSERVANCES_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _argument_parser()
    args = parser.parse_args(argv)
    if args.feasts_only and args.include_feasts:
        parser.error("--feasts-only cannot be combined with --include-feasts")
    to_year = args.to_year if args.to_year is not None else args.from_year
    try:
        catalog = load_catalog(args.feasts, args.names, args.observances)
        selected_namedays = (
            ()
            if args.feasts_only
            else select_namedays(
                catalog.namedays,
                top=args.top,
                min_popularity=args.min_popularity,
            )
        )
        grouped_names = (
            {}
            if args.feasts_only
            else generate_namedays(
                catalog,
                args.from_year,
                to_year,
                top=args.top,
                min_popularity=args.min_popularity,
            )
        )
        grouped_observances = (
            generate_observances(catalog, args.from_year, to_year)
            if args.include_feasts or args.feasts_only
            else {}
        )
        calendar = build_calendar(
            grouped_names,
            grouped_observances=grouped_observances,
        )
        write_calendar(calendar, args.output)
        statistics = _year_statistics(
            selected_namedays,
            grouped_names,
            grouped_observances,
            args.from_year,
            to_year,
            church_feast_count=(
                len(catalog.observances)
                if args.include_feasts or args.feasts_only
                else 0
            ),
        )
        _print_generation_summary(
            args.output,
            _selection_label(args),
            statistics,
        )
    except (
        DataValidationError,
        OSError,
        UnsupportedFeastRuleError,
        ValueError,
    ) as exc:
        parser.error(str(exc))
    return 0
