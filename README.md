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
- primary and additional celebration dates for names with multiple feasts
- one all-day event per date, with all celebrating names in `SUMMARY`
- `--all`, `--top N`, and `--min-popularity N` selection modes
- case- and tonos-insensitive exact lookup with `grecal find NAME`
- ranked partial and typo-tolerant lookup with `grecal search QUERY`
- reverse lookup by calendar date with `grecal date DATE`
- personal calendars with `grecal generate --names NAME,...`
- opt-in combined feast output and a feast-only mode
- single-year or multi-year output
- full data and feast-rule validation with `grecal validate`
- generation previews with `--dry-run`
- calendar name, description, modification time, and optional display color metadata
- persistent calendar and event UIDs suitable for refreshable subscriptions
- UTF-8 RFC 5545 output with CRLF line endings and folded content lines
- minimal `VEVENT` components with no event description or location
- importable by Apple Calendar, Google Calendar, and Outlook

## Project structure

```text
grecal/
├── .github/workflows/ci.yml     # test and distribution build workflow
├── generate_ics.py              # source-tree CLI entry point
├── grecal/
│   ├── __init__.py              # public library API
│   ├── _version.py              # package version source of truth
│   ├── easter.py                # Orthodox computus
│   ├── generator.py             # filtering, grouping, ICS, and CLI
│   ├── models.py                # immutable dataclasses
│   ├── parser.py                # YAML loading and validation
│   └── rules.py                 # all feast-date rule dispatch
├── data/
│   ├── names.yaml               # bundled names
│   ├── feasts.yaml              # bundled dates and rules
│   └── observances.yaml         # optional church feast titles
├── scripts/
│   └── build_site.py            # website data and subscription builder
├── tests/
├── web/                         # hand-written website source
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

## Command-line reference

Grecal uses subcommands exclusively; generation options are not accepted at
the top level.

```text
grecal [-h] [--version] COMMAND
```

| Option | Meaning |
| --- | --- |
| `-h`, `--help` | Show the command list and exit |
| `--version` | Print the installed Grecal version and exit |

The available commands are:

| Command | Purpose | Writes a file? |
| --- | --- | --- |
| `generate` | Generate an ICS calendar | Yes, unless `--dry-run` is used |
| `find` | Resolve one exact name and calculate its dates | No |
| `search` | Discover names with partial and fuzzy matching | No |
| `date` | Show namedays and church observances for one date | No |
| `validate` | Validate catalog files and every feast rule | No |

Running `grecal` without a command prints the same overview. Each command has
focused help, for example `grecal search --help`.

### `grecal generate`

```text
grecal generate
    (--all | --top N | --min-popularity N | --names LIST | --feasts-only)
    [--include-feasts]
    [--from-year YEAR]
    [--to-year YEAR]
    [--output PATH]
    [--calendar-name TEXT]
    [--calendar-description TEXT]
    [--calendar-color COLOR]
    [--calendar-id ID]
    [--dry-run]
    [catalog options]
```

Exactly one selection option is required:

| Selection option | Result |
| --- | --- |
| `--all` | Every nameday identity group |
| `--top N` | The `N` highest-scoring identity groups; `N` must be at least 1 |
| `--min-popularity N` | Groups whose score is at least `N`; accepted range is 0–100 |
| `--names LIST` | Only the comma-separated personal names in `LIST` |
| `--feasts-only` | Church feast titles without namedays |

Other generation options:

| Option | Default | Meaning |
| --- | --- | --- |
| `--include-feasts` | Off | Add church feast titles to the selected namedays |
| `--from-year YEAR` | Current year | First generated year |
| `--to-year YEAR` | Same as `--from-year` | Last generated year |
| `--output PATH` | `grecal.ics` | Destination ICS file |
| `--calendar-name TEXT` | Depends on the selection | Calendar display name |
| `--calendar-description TEXT` | Depends on the selection and years | Calendar description |
| `--calendar-color COLOR` | Omitted | Suggested display color, such as `blue` or `#3f51b5` |
| `--calendar-id ID` | Derived from the selection | Stable logical identity used for calendar and event UIDs |
| `--dry-run` | Off | Calculate and report without writing a file or creating its directory |
| `-h`, `--help` | — | Show generation help |

Selection options are mutually exclusive. `--feasts-only` cannot be combined
with `--include-feasts`. Year ranges are inclusive and must remain within
1900–2100.

Examples:

```bash
# Every nameday in 2026
grecal generate --all --from-year 2026 --output grecal-2026.ics

# The 100 highest-scoring identity groups in 2026
grecal generate --top 100 --from-year 2026 --output grecal-top-100-2026.ics

# Groups scored 80 or higher from 2026 through 2030
grecal generate --min-popularity 80 --from-year 2026 --to-year 2030 --output grecal-2026-2030.ics

# Every nameday plus all church feasts in 2026
grecal generate --all --include-feasts --from-year 2026 --output grecal-complete-2026.ics

# Church feasts only in 2026
grecal generate --feasts-only --from-year 2026 --output grecal-feasts-2026.ics

# A personal calendar containing two names
grecal generate --names Γιώργος,Μαρία --from-year 2026 --output personal.ics

# A personal calendar with custom display metadata
grecal generate \
  --names Γιώργος,Μαρία \
  --from-year 2026 \
  --calendar-name "Οικογενειακές γιορτές" \
  --calendar-description "Ονομαστικές εορτές της οικογένειας" \
  --calendar-color blue \
  --output family.ics

# A long-lived published feed with an explicit stable identity
grecal generate \
  --all \
  --include-feasts \
  --from-year 2025 \
  --to-year 2036 \
  --calendar-id official-complete \
  --output grecal.ics

# Preview the full pipeline without writing the output
grecal generate --all --from-year 2026 --output grecal-2026.ics --dry-run
```

Personal-name matching ignores capitalization and Greek diacritics. Event
summaries contain only the requested canonical spellings: selecting `Γιώργος`
does not also add `Γεώργιος` or `Γεωργία`. Spaces around commas are accepted
when the whole value is quoted. Unknown and empty names are errors.

Grecal chooses a calendar name that reflects the selection mode:

| Selection | Default calendar name |
| --- | --- |
| Namedays | `Grecal — Greek Orthodox Namedays` |
| `--names` | `Grecal — Personal Namedays` |
| `--feasts-only` | `Grecal — Greek Orthodox Feasts` |
| Namedays with `--include-feasts` | `Grecal — Greek Orthodox Calendar` |

The default description similarly identifies the selection and generated year
or inclusive year range. `--calendar-name` and `--calendar-description`
replace those defaults. `--calendar-color` is optional because calendar
applications may ignore or override a suggested color.

Grecal derives a stable calendar identity from the selection mode. For
example, `--all` uses `namedays:all`, `--feasts-only` uses `feasts`, and
`--all --include-feasts` uses `complete:all`. Personal identities use the
resolved names after case- and tonos-insensitive normalization, sorting, and
deduplication, so changing the input order does not change the identity.

The generated year range, output path, display name, description, and color do
not participate in identity. Consequently, overlapping dates keep the same
event UIDs when a calendar is regenerated with a wider year range or revised
summary. Use `--calendar-id` for a long-lived published feed or a custom YAML
catalog whose identity must remain independent of its current selection. Once
published, changing this value makes calendar clients see a different feed.

Output paths may be absolute or relative. Quote paths containing spaces:

```bash
grecal generate --all --from-year 2026 --output "$HOME/My Calendars/grecal-2026.ics"
```

After writing a file, Grecal prints its path and size, the year range, and
generation statistics. A dry-run report begins with `Dry run: no file written`
and reports the path and byte size that would have been generated.

## Website artifact builder

The website uses pre-generated static files and can be hosted on any static
web host without a Python server. Build the complete data bundle from the
repository root:

```bash
.venv/bin/python scripts/build_site.py
```

The default output is `_site/`. It is generated content and is ignored by Git.
Use `--output PATH` to choose another directory. `--today YYYY-MM-DD` fixes the
effective date for a reproducible local build or test; normal deployments omit
it and use the current date in the `Europe/Athens` time zone.

```bash
.venv/bin/python scripts/build_site.py \
  --today 2026-07-22 \
  --output _site
```

Each build validates the bundled calendar data and replaces the generated
bundle:

```text
_site/
├── index.html
├── styles.css
├── app.js
├── branding.json
├── data/
│   ├── config.json
│   ├── calendar-2025.json
│   ├── calendar-2026.json
│   ├── calendar-2027.json
│   ├── calendar-2028.json
│   └── search-2026.json
└── calendars/
    ├── complete.ics
    └── top-100.ics
```

The years above illustrate a build made during 2026. Calendar JSON always
covers the previous year, current year, and next two years. Each occupied date
contains separate `namedays` and `observances` arrays. The search index covers
the current year and contains every name variant and feast title, along with a
case- and tonos-insensitive `normalized` value for client-side fuzzy search.
`data/config.json` records the generated timestamp, available lookup range,
schema version, and subscription metadata.

The complete subscription contains all namedays and church feasts. The popular
subscription contains the top 100 nameday identity groups and no feasts. Their
explicit calendar IDs are respectively `official-complete` and
`official-top-100`, preserving event UIDs across annual rebuilds and overlapping
year ranges. Both feeds include the previous year through two years ahead, so
subscribers keep recent history while receiving future events automatically
when their calendar application refreshes the same URL.

The builder writes into a staging directory before publishing the result. It
will replace only a directory carrying its own marker file, preventing an
accidental overwrite of an unrelated directory. Re-running the same command is
safe and removes stale generated files. It also copies the dependency-free
frontend from `web/` into the output directory.

Website branding is defined entirely in `web/branding.json`, keeping the
frontend reusable without coupling the Grecal library to a particular public
site. The website presents a 31-day agenda spanning 15 days before and after
today; today opens as the first visible row, while the earlier dates remain
available by scrolling upward. It also provides date lookup across the
configured range, typo-tolerant search for the current year, and links for both
calendar subscriptions. Greek is the default language, with a clearly visible
English switch whose selection is stored only in the visitor's browser. To
browse a build locally, start a static server:

```bash
.venv/bin/python -m http.server 8000 --directory _site
```

Then open <http://localhost:8000/>. Opening `index.html` directly as a local
file will not work because browsers restrict its JSON requests. Stop the server
with `Ctrl-C`.

### `grecal find`

```text
grecal find NAME
    [--from-year YEAR]
    [--to-year YEAR]
    [catalog options]
```

| Argument or option | Default | Meaning |
| --- | --- | --- |
| `NAME` | Required | One complete name to resolve |
| `--from-year YEAR` | Current year | First year to calculate |
| `--to-year YEAR` | Same as `--from-year` | Last year to calculate |
| `-h`, `--help` | — | Show exact-lookup help |

`find` performs one case- and tonos-insensitive exact lookup. It prints the
canonical name, identity group, all variants, and one resolved date per year;
it never creates an ICS file.

```bash
grecal find γιωργος --from-year 2026
```

```text
Name: Γιώργος
Identity group: georgios
Variants: Γεώργιος, Γιώργος, Γεωργία
Dates:
  2026-04-23
```

An unknown complete name is an error and suggests trying `grecal search`.

### `grecal search`

```text
grecal search QUERY [--limit N] [catalog options]
```

| Argument or option | Default | Meaning |
| --- | --- | --- |
| `QUERY` | Required | Complete name, name fragment, or potentially misspelled name |
| `--limit N` | `10` | Maximum results; `N` must be at least 1 |
| `-h`, `--help` | — | Show search help |

Search normalization ignores capitalization and Greek diacritics. Results are
ranked deterministically in this order: exact matches, prefixes, substrings,
and fuzzy matches. Fuzzy ranking combines adjacent-transposition-aware edit
distance with sequence similarity, then uses popularity and canonical spelling
as stable tie-breakers.

```bash
grecal search Ανδρ
grecal search αασΑνδρεας --limit 3
```

```text
Ανδρέας  group: andreas
Ανδρούλα  group: andreas
Ανδρονίκη  group: andronikos
```

Search returns status 0 when it finds results and status 1 when there are no
matches. It does not calculate feast dates or create files; pass a selected
result to `grecal find` to calculate dates.

### `grecal date`

```text
grecal date DATE [catalog options]
```

| Argument or option | Default | Meaning |
| --- | --- | --- |
| `DATE` | Required | ISO date in `YYYY-MM-DD` format, or `today` |
| `-h`, `--help` | — | Show date-lookup help |

`date` is the inverse of `find`: it resolves every nameday and church
observance on one date. The two categories are always displayed separately,
and the command never creates an ICS file.

```bash
grecal date 2026-08-15
grecal date today
```

```text
Date: 2026-08-15
Namedays: Μαρία, Μαριέττα, Μαρίκα, ...
Church observances: Κοίμηση της Θεοτόκου
```

Ambiguous formats such as `15/08/2026` are rejected. Dates must be within
1900–2100. The command returns status 0 when it finds a nameday or observance,
status 1 for a valid empty date, and status 2 for invalid input or catalog
errors.

### `grecal validate`

```text
grecal validate [catalog options]
```

Validation checks YAML structure, duplicate identifiers and display names,
popularity ranges, feast cross-references, fixed dates, and every feast rule
throughout 1900–2100. Success prints catalog counts and returns status 0;
invalid data prints an error and returns a nonzero status.

```bash
grecal validate
```

### Catalog options

All five commands accept the same advanced catalog overrides:

| Option | Default | Meaning |
| --- | --- | --- |
| `--feasts-file PATH` | Bundled `feasts.yaml` | Alternative feast definitions |
| `--names-file PATH` | Bundled `names.yaml` | Alternative nameday definitions |
| `--observances-file PATH` | Bundled `observances.yaml` | Alternative church observances |

The `-file` suffix distinguishes a catalog path from personal names:

```text
--names Γιώργος,Μαρία    Personal names selected by `generate`
--names-file names.yaml  YAML catalog containing all names
```

Contributors can validate alternative files explicitly:

```bash
grecal validate --feasts-file data/feasts.yaml --names-file data/names.yaml --observances-file data/observances.yaml
```

### Subsequent use

The `.venv` directory persists between shell sessions. Return to the checkout,
activate it, and run the desired command:

```bash
source .venv/bin/activate
grecal generate --all --from-year 2026 --output grecal-2026.ics
```

Alternatively, invoke the installed script without activating the environment:

```bash
.venv/bin/grecal generate --all --from-year 2026 --output grecal-2026.ics
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
- An error that a command is required means the invocation needs one of
  `generate`, `find`, `search`, `date`, or `validate`.
- Within `generate`, exactly one of `--all`, `--top N`,
  `--min-popularity N`, `--feasts-only`, or `--names LIST` is required.
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
from datetime import date
from pathlib import Path

from grecal import (
    build_calendar,
    generate_namedays,
    generate_observances,
    generate_personal_namedays,
    load_catalog,
    lookup_date,
    normalize_search_text,
    search_names,
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
personal_names = generate_personal_namedays(
    catalog, ("Γιώργος", "Μαρία"), 2026, 2026
)
matches = search_names(catalog, "αασΑνδρεας", limit=3)
search_key = normalize_search_text("Γιώργος")
day = lookup_date(catalog, date(2026, 8, 15))
calendar = build_calendar(
    names,
    grouped_observances=observances,
    calendar_name="Grecal — My Calendar",
    calendar_description="Greek Orthodox namedays and feasts for 2026.",
    calendar_color="blue",
    calendar_id="my-calendar",
)
write_calendar(calendar, Path("grecal-2026.ics"))
```

`generate_namedays` returns a date-keyed mapping, so each date can occur only
once. `generate_observances` does the same for titles. `build_calendar` combines
the mappings while retaining at most one event per date. Omitting the third
path from `load_catalog` and omitting `grouped_observances` produces a
nameday-only calendar. `calendar_name`, `calendar_description`, and
`calendar_color` control the same top-level metadata as the corresponding CLI
options. `calendar_id` provides the stable logical identity used to derive the
calendar and event UIDs. Passing `None` for the name or description omits that
property.

`generate_personal_namedays` uses the same date-keyed shape but includes only
the requested display names. Like the CLI, its matching is case- and
tonos-insensitive and its output uses canonical catalog spellings.

`search_names` returns immutable `NameSearchResult` values in the same ranked
order as `grecal search`. Each result contains the canonical display name,
identity-group ID, popularity, numeric similarity score, and match type.
`normalize_search_text` exposes the same Unicode case- and diacritic-insensitive
normalization used by the CLI and the website search index.

`lookup_date` returns an immutable `DateLookupResult` containing the requested
date plus separate tuples of namedays and church observance titles.

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

`data/names.yaml` points an identity group to a primary feast. Dates must not be
copied into this file.

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

When an identity group is customarily celebrated on more than one date, keep
the principal date in `feast` and list the other feast IDs explicitly in
`additional_feasts`:

```yaml
- id: christina
  feast: feast_nativity_christ
  additional_feasts:
    - feast_christina
  popularity: 98
  names:
    - Χριστίνα
    - Χριστιάνα
```

Generation, personal calendars, date lookup, and website data include every
configured feast. The order is meaningful for data review: `feast` is the
primary association and `additional_feasts` contains secondary associations.
The parser rejects duplicate, repeated-primary, and unknown feast IDs.

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
existing feast. The bundled file contains 22 observances using the Church of
Greece/revised-calendar convention.

## Adding names and feasts

For a name that uses an existing observance, add only a group to `names.yaml`
and reference the existing feast ID. If it has multiple accepted celebration
dates, choose the primary feast and add the others to `additional_feasts`. For
a new fixed observance:

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

`DTEND` is exclusive, as required for an all-day event. At `VCALENDAR` level,
the serializer emits `PRODID`, `VERSION:2.0`, and `CALSCALE:GREGORIAN`, plus:

| Property | Emitted | Purpose |
| --- | --- | --- |
| `UID` | Always | Persistent UUIDv5 identity for the logical calendar |
| `NAME` and `X-WR-CALNAME` | Always by the CLI | Standard display name plus compatibility form |
| `DESCRIPTION` and `X-WR-CALDESC` | Always by the CLI | Standard calendar description plus compatibility form |
| `LAST-MODIFIED` | Always | UTC generation timestamp |
| `COLOR` | With `--calendar-color` | Suggested display color |

Calendar-level `UID`, `NAME`, `DESCRIPTION`, `LAST-MODIFIED`, and `COLOR` follow
[RFC 7986](https://www.rfc-editor.org/rfc/rfc7986.html). The `X-WR-*`
properties are emitted alongside their standard equivalents for calendar-app
compatibility. Individual `VEVENT` components remain intentionally minimal:
they omit event-level `DESCRIPTION`, `LOCATION`, time zones, alarms, and timed
event fields.

Each event UID is a UUIDv5 derived from the calendar identity and ISO date,
not from its summary. The same date in the same logical feed therefore keeps
its UID across regenerated year ranges and catalog corrections, while the same
date in a different feed receives a different UID.

## Validation

The automated suite covers known Orthodox Easter dates and range limits, every
feast-rule type, all eight movable church observances, Saint George transfer
boundaries, custom-rule injection, filtering, same-day grouping, YAML schema
failures, final dataset counts, validation, dry runs, exact lookup, fuzzy
search, reverse date lookup, and every CLI generation mode. The final ICS
checks include:

- valid UTF-8 without a byte-order mark
- CRLF record endings and 75-octet content-line folding
- one `VEVENT` per date
- date-valued `DTSTART` and exclusive next-day `DTEND`
- required `UID`, `DTSTAMP`, and `SUMMARY`
- stable UIDs across content revisions and distinct UIDs between feeds
- standard and compatibility calendar metadata
- no event-level `DESCRIPTION` or `LOCATION`

The packaged console command and bundled YAML are additionally tested from a
built wheel outside the repository before release.

GitHub Actions runs the suite on Python 3.9 through 3.14 for every pull request
and push to `main`. After the test matrix passes, it builds the wheel and source
distribution, verifies the installed wheel, and uploads both as workflow
artifacts.

## License

Grecal is released under the MIT License. See [LICENSE](LICENSE).
