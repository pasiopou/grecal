# Website source

This directory contains the hand-written, dependency-free website frontend
powered by Grecal:

- `branding.json` is the single source of public branding, localized page
  metadata, repository attribution, and the browser preference namespace.
- `index.html` defines the accessible page structure and uses branding
  placeholders rendered by the site builder.
- `styles.css` provides the responsive visual design.
- `app.js` loads the generated calendar data and implements Greek/English
  localization, the agenda, date lookup, fuzzy search, and subscription links.

Greek is the default language. A visitor can switch to English, and that choice
is kept in browser-local storage without accounts, analytics, or tracking.

Run `python scripts/build_site.py` from the repository root to copy these files
and generate the JSON and ICS assets under `_site/`. Generated artifacts are
ignored by Git and should not be edited by hand.
