# Grecal

[![CI](https://github.com/pasiopou/grecal/actions/workflows/ci.yml/badge.svg)](https://github.com/pasiopou/grecal/actions/workflows/ci.yml)

`grecal` is a reusable Python library and command-line application for
generating UTF-8 iCalendar files containing Greek Orthodox namedays and,
optionally, major church observances. Dates, names, and observance titles live
in YAML; Python is responsible only for validation, feast rules, selection,
grouping, and serialization.

The catalog contains 457 identity groups, 642 unique display names, 22 church
observances, and 453 feast definitions.

For installation and CLI examples, see
[running from a checkout](#running-from-a-checkout).

## Features

- Orthodox Easter calculation for 1900–2100, without external services
- fixed, Easter-offset, Saint George, and named custom feast rules
- one all-day event per date, with all celebrating names in `SUMMARY`
- `--all`, `--top N`, and `--min-popularity N` selection modes
- opt-in combined feast output and a feast-only mode
- single-year or multi-year output
- full data and feast-rule validation with `grecal validate`
- generation previews with `--dry-run`
- UTF-8 RFC 5545 output with CRLF line endings and folded content lines
- minimal events with no description or location
- importable by Apple Calendar, Google Calendar, and Outlook

## Project structure

```text
grecal/
├── .github/workflows/ci.yml     # test and distribution build workflow
├── generate_ics.py              # source-tree CLI entry point
├── grecal/
│   ├── __init__.py              # public library API
│   ├── easter.py                # Orthodox computus
│   ├── generator.py             # filtering, grouping, ICS, and CLI
│   ├── models.py                # immutable dataclasses
│   ├── parser.py                # YAML loading and validation
│   └── rules.py                 # all feast-date rule dispatch
├── data/
│   ├── names.yaml               # production names
│   ├── feasts.yaml              # production dates and rules
│   └── observances.yaml         # optional church feast titles
├── tests/
├── pyproject.toml
└── README.md
```

## Running from a checkout

Grecal requires Python 3.9 or newer. The commands below target macOS and Linux
and assume the repository is already checked out and the shell is in its root
directory.

### Set up the Python environment

Check the installed Python version:

```bash
python3 --version
```

If Python is missing or older than 3.9, install a current Python 3 release with
the system package manager or from [python.org](https://www.python.org/downloads/).

Create and activate a virtual environment, then install Grecal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

A virtual environment is an isolated Python installation for this checkout.
Once activated, `python`, `pip`, and installed commands resolve inside
`.venv`, without modifying the system Python. The first installation downloads
PyYAML and icalendar; calendar generation itself does not require network
access.

Confirm that the CLI is available:

```bash
grecal --help
```

### Generate a calendar

For every nameday in 2026:

```bash
grecal --all --from-year 2026 --output grecal-2026.ics
```

This creates `grecal-2026.ics` in the current directory. After writing the
file, Grecal prints its path and size, the selected year range, and generation
statistics. The file can be imported into Apple Calendar, Google Calendar,
Outlook, or another iCalendar-compatible application.

Every invocation requires exactly one selection mode:

| Selection mode | Result |
| --- | --- |
| `--all` | Every nameday identity group |
| `--top N` | The `N` highest-scoring nameday identity groups |
| `--min-popularity N` | Nameday groups whose score is at least `N` |
| `--feasts-only` | Church feast titles without namedays |

`--include-feasts` is not a selection mode. Add it to `--all`, `--top N`, or
`--min-popularity N` to include church feast titles alongside namedays. Do not
combine two selection modes.

Common examples:

```bash
# Every nameday in 2026
grecal --all --from-year 2026 --output grecal-2026.ics

# The 100 highest-scoring identity groups in 2026
grecal --top 100 --from-year 2026 --output grecal-top-100-2026.ics

# Groups scored 80 or higher from 2026 through 2030
grecal --min-popularity 80 --from-year 2026 --to-year 2030 --output grecal-2026-2030.ics

# Every nameday plus all church feasts in 2026
grecal --all --include-feasts --from-year 2026 --output grecal-complete-2026.ics

# Church feasts only in 2026
grecal --feasts-only --from-year 2026 --output grecal-feasts-2026.ics
```

Year ranges are inclusive and must remain within 1900–2100. If
`--from-year` is omitted, Grecal uses the current year. If `--to-year` is
omitted, it uses the same year as `--from-year`. If `--output` is omitted, the
output path is `grecal.ics` in the current directory:

```bash
grecal --all
```

Output paths may be absolute or relative. Quote paths containing spaces:

```bash
grecal --all --from-year 2026 --output "$HOME/My Calendars/grecal-2026.ics"
```

To run the complete generation pipeline and view the report without writing a
file or creating its parent directory, add `--dry-run`:

```bash
grecal --all --from-year 2026 --output grecal-2026.ics --dry-run
```

The report begins with `Dry run: no file written` and shows the path and byte
size that would have been generated.

### Validate the data

Validate the YAML schema, cross-references, duplicate values, and every feast
calculation throughout the supported 1900–2100 range:

```bash
grecal validate
```

A successful validation prints the catalog counts and exits with status 0. An
invalid file or feast rule prints an error and exits with a nonzero status.
Contributors can validate alternative files explicitly:

```bash
grecal validate --feasts data/feasts.yaml --names data/names.yaml --observances data/observances.yaml
```

### Subsequent use

The `.venv` directory persists between shell sessions. Return to the checkout,
activate it, and run the desired command:

```bash
source .venv/bin/activate
grecal --all --from-year 2026 --output grecal-2026.ics
```

Alternatively, invoke the installed script without activating the environment:

```bash
.venv/bin/grecal --all --from-year 2026 --output grecal-2026.ics
```

After updating the checkout, reinstall it so `.venv` receives the latest code,
YAML data, and dependencies:

```bash
source .venv/bin/activate
python -m pip install .
```

Use `deactivate` to leave an active virtual environment.

### Troubleshooting

- If `grecal` is not found, activate `.venv` or invoke
  `.venv/bin/grecal` directly.
- If Python reports a missing module, activate `.venv` and rerun
  `python -m pip install .`.
- Package download errors during initial installation usually indicate that
  access to the Python Package Index is unavailable or requires proxy
  configuration.
- An error that a selection argument is required means the command needs
  exactly one of `--all`, `--top N`, `--min-popularity N`, or
  `--feasts-only`.
- Relative output paths are resolved from the current working directory. For
  permission errors, choose a writable destination.
- From an activated environment, `python generate_ics.py ...` is an equivalent
  source-tree entry point if the console script is unavailable.

### Development installation

Install the test dependencies in editable mode and run the suite:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

The built wheel includes `names.yaml`, `feasts.yaml`, and
`observances.yaml`, so an installed console command also works outside the
source checkout.

## Popularity and selection

Popularity belongs to a nameday identity group in `data/names.yaml`:

```yaml
- id: georgios
  feast: feast_saint_george
  popularity: 100
  names:
    - Γεώργιος
    - Γιώργος
    - Γεωργία
```

The score is an integer from 0 through 100. A larger value sorts ahead of a
smaller one; 100 is the highest possible score and 0 is the lowest. It is a
relative selection score, not a percentage or probability. Grecal does not
calculate the score while generating a calendar—it reads the value stored in
YAML. All variants in one identity group share that group's score.

The two options use `N` differently:

| Option | Meaning of `N` | Accepted values |
| --- | --- | --- |
| `--top N` | Number of highest-scoring identity groups to select | Any integer `N >= 1` |
| `--min-popularity N` | Minimum score a group must have, inclusive | Any integer from `0` through `100` |

For `--top N`, groups are ordered first by descending popularity and then by
their stable `id` in ascending order. The second key makes results deterministic
when several groups have the same score. A tie at the cutoff is therefore split
by `id`; the command returns exactly `N` groups when at least `N` groups exist.
With the current 457 groups, values from 1 through 457 select exactly that many
groups, while a value greater than 457 simply selects all 457. Zero and negative
values are rejected.

For `--min-popularity N`, the comparison is `popularity >= N`, so ties are
always included. `--min-popularity 100` selects only groups scored 100,
`--min-popularity 80` selects groups scored 80 through 100, and
`--min-popularity 0` is equivalent to selecting every group. Values outside
0–100 are rejected.

Current-data examples for 2026 illustrate why `N` is not an event count:

| Selection | Identity groups | Display names | Calendar events |
| --- | ---: | ---: | ---: |
| `--top 100` | 100 | 208 | 76 |
| `--min-popularity 80` | 161 | 287 | 108 |
| `--all` | 457 | 642 | 226 |

One group can contain multiple display names, and groups sharing a date are
merged into one event. Consequently, `--top 100` means 100 YAML identity
groups—not 100 spellings, people, dates, or events.

Church observances are independent of popularity. `--include-feasts` adds all
22 observances after nameday filtering, and `--feasts-only` generates only
those observances without requiring a nameday selection.

## Generation report

After writing the ICS file, the CLI prints its path and size, the requested
year range, the active selection, and a yearly statistics table. For example:

```text
Generated: grecal-2025-2026.ics (30,756 bytes)
Years: 2025-2026
Selection: top 100 nameday groups

Year               Identity groups  Display names  Church feasts  Calendar events
-----------------  ---------------  -------------  -------------  ---------------
2025                           100            208              0               77
2026                           100            208              0               76
Total occurrences              200            416              0              153
Average/year                 100.0          208.0            0.0             76.5
```

The columns have these meanings:

- **Identity groups** is the number of selected entries from `names.yaml`.
  Selection is applied for every generated year, so this value normally stays
  constant across the yearly rows.
- **Display names** is the number of spellings and common variants carried by
  those selected groups. It counts names before same-date grouping.
- **Church feasts** is the number of observance titles included for the year.
  It is 0 for a nameday-only calendar and currently 22 with
  `--include-feasts` or `--feasts-only`.
- **Calendar events** is the actual number of all-day `VEVENT` components for
  the year. Names and feast titles that share a date are merged, so this is a
  count of unique occupied calendar dates rather than a sum of the other
  columns.

`Total occurrences` sums every yearly row. Thus a group selected in two years
counts twice in that row; the total is not a count of unique YAML definitions.
For a multi-year calendar, `Average/year` divides each total by the number of
years and displays one decimal place. A single-year report omits the redundant
average row.

## Library use

```python
from pathlib import Path

from grecal import (
    build_calendar,
    generate_namedays,
    generate_observances,
    load_catalog,
    validate_catalog,
    write_calendar,
)

catalog = load_catalog(
    Path("data/feasts.yaml"),
    Path("data/names.yaml"),
    Path("data/observances.yaml"),
)
validate_catalog(catalog)
names = generate_namedays(catalog, 2026, 2026, min_popularity=80)
observances = generate_observances(catalog, 2026, 2026)
calendar = build_calendar(names, grouped_observances=observances)
write_calendar(calendar, Path("grecal-2026.ics"))
```

`generate_namedays` returns a date-keyed mapping, so each date can occur only
once. `generate_observances` does the same for titles. `build_calendar` combines
the mappings while retaining at most one event per date. Omitting the third
path from `load_catalog` and omitting `grouped_observances` produces a
nameday-only calendar.

## YAML formats

`data/feasts.yaml` maps stable feast IDs to one of four rule types.

### Fixed date

```yaml
saint_andrew:
  type: fixed
  month: 11
  day: 30
```

### Offset from Orthodox Easter

```yaml
pentecost:
  type: offset_from_easter
  offset: 49

holy_spirit:
  type: offset_from_easter
  offset: 50
```

Offsets are signed day counts relative to Easter Sunday.

### Saint George

```yaml
saint_george:
  type: saint_george
```

Saint George is April 23 unless April 23 is on or before Orthodox Easter; in
that case it transfers to Easter Monday.

### Custom rule

```yaml
saint_mark:
  type: custom
  rule: saint_mark
  month: 4
  day: 25

sunday_of_forefathers:
  type: custom
  rule: sunday_on_or_after
  month: 12
  day: 11
```

Built-in custom rules are dispatched centrally in `grecal/rules.py`. Library
callers may provide extra custom resolvers to `generate_namedays` through its
`custom_rules` argument; nothing is registered globally.

`data/names.yaml` points an identity group to a feast. Dates must not be copied
into this file.

```yaml
- id: andreas
  feast: saint_andrew
  popularity: 95
  names:
    - Ανδρέας
    - Αντρέας
```

Popularity is an integer from 0 through 100. Every group must have a unique ID,
reference an existing feast, and contain at least one non-empty display name.
A display name may occur in only one group.

`data/observances.yaml` assigns a display title to a feast definition. The
optional `details` field is a reference note and is never emitted as an ICS
description:

```yaml
- id: pentecost
  feast: feast_pentecost
  title: Πεντηκοστή
  details: 50ή ημέρα από το Πάσχα, με την Κυριακή του Πάσχα ως 1η ημέρα
```

Observance IDs and titles must be unique, and every entry must reference an
existing feast. The production file contains 22 observances using the Church
of Greece/revised-calendar convention.

## Adding names and feasts

For a name that uses an existing observance, add only a group to `names.yaml`
and reference the existing feast ID. For a new fixed observance:

1. Add the date once to `feasts.yaml`.
2. Add one or more identity groups to `names.yaml` that reference it.
3. Assign an integer popularity score from 0 through 100.
4. Add a focused test for the date and any important everyday variants.
5. Run the complete test suite.

For a new movable calculation, prefer `offset_from_easter` when possible. Add a
new rule type or custom rule only when the feast cannot be expressed by existing
data fields, and keep all calculation logic in `grecal/rules.py`.

To add a title that does not correspond to a name, add or reuse its date rule in
`feasts.yaml`, then add an entry to `observances.yaml`. Do not add a placeholder
name to `names.yaml`.

## iCalendar shape

Each generated date produces one minimal all-day event:

```text
BEGIN:VEVENT
SUMMARY:Γιώργος, Γεωργία, Γεώργιος
DTSTART;VALUE=DATE:20260423
DTEND;VALUE=DATE:20260424
UID:...
DTSTAMP:...
END:VEVENT
```

When church observances are enabled, titles precede names. An abbreviated
combined summary looks like this:

```text
SUMMARY:Κοίμηση της Θεοτόκου — Μαρία, Μαριέττα, Μαρίκα, …, Παναγιώτης, …
```

Multiple observances on one date are separated by ` · ` and remain in the same
event. Nameday-only summaries are unchanged.

`DTEND` is exclusive, as required for an all-day event. The serializer also
emits `PRODID`, `VERSION:2.0`, and `CALSCALE:GREGORIAN`. It deliberately omits
`DESCRIPTION`, `LOCATION`, time zones, alarms, and timed-event fields.

## Validation

The automated suite covers known Orthodox Easter dates and range limits, every
feast-rule type, all eight movable church observances, Saint George transfer
boundaries, custom-rule injection, filtering, same-day grouping, YAML schema
failures, final dataset counts, `grecal validate`, dry runs, and every CLI
generation mode. The final ICS checks include:

- valid UTF-8 without a byte-order mark
- CRLF record endings and 75-octet content-line folding
- one `VEVENT` per date
- date-valued `DTSTART` and exclusive next-day `DTEND`
- required `UID`, `DTSTAMP`, and `SUMMARY`
- no `DESCRIPTION` or `LOCATION`

The packaged console command and bundled YAML are additionally tested from a
built wheel outside the repository before release.

GitHub Actions runs the suite on Python 3.9 through 3.14 for every pull request
and push to `main`. After the test matrix passes, it builds the wheel and source
distribution, verifies the installed wheel, and uploads both as workflow
artifacts.

## License

Grecal is released under the MIT License. See [LICENSE](LICENSE).
