"""Grecal: generate Greek Orthodox calendar files."""

from .generator import (
    DateLookupResult,
    NameSearchResult,
    build_calendar,
    generate_namedays,
    generate_observances,
    generate_personal_namedays,
    lookup_date,
    search_names,
    select_namedays_by_name,
    validate_catalog,
    write_calendar,
)
from .models import Catalog, Feast, FeastType, Nameday, Observance
from .parser import load_catalog
from ._version import __version__

__all__ = [
    "Catalog",
    "DateLookupResult",
    "Feast",
    "FeastType",
    "Nameday",
    "NameSearchResult",
    "Observance",
    "build_calendar",
    "generate_namedays",
    "generate_observances",
    "generate_personal_namedays",
    "load_catalog",
    "lookup_date",
    "search_names",
    "select_namedays_by_name",
    "validate_catalog",
    "write_calendar",
    "__version__",
]
