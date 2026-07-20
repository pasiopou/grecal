"""Grecal: generate Greek Orthodox calendar files."""

__version__ = "1.0.0"

from .generator import (
    build_calendar,
    generate_namedays,
    generate_observances,
    write_calendar,
)
from .models import Catalog, Feast, FeastType, Nameday, Observance
from .parser import load_catalog

__all__ = [
    "Catalog",
    "Feast",
    "FeastType",
    "Nameday",
    "Observance",
    "build_calendar",
    "generate_namedays",
    "generate_observances",
    "load_catalog",
    "write_calendar",
    "__version__",
]
