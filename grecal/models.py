"""Validated domain models for Grecal's YAML data files."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeastType(str, Enum):
    FIXED = "fixed"
    OFFSET_FROM_EASTER = "offset_from_easter"
    SAINT_GEORGE = "saint_george"
    CUSTOM = "custom"


@dataclass(frozen=True)
class Feast:
    id: str
    type: FeastType
    month: int | None = None
    day: int | None = None
    offset: int | None = None
    rule: str | None = None


@dataclass(frozen=True)
class Nameday:
    id: str
    feast: str
    popularity: int
    names: tuple[str, ...]
    additional_feasts: tuple[str, ...] = ()

    @property
    def feasts(self) -> tuple[str, ...]:
        """Return the primary feast followed by any additional feasts."""

        return (self.feast, *self.additional_feasts)


@dataclass(frozen=True)
class Observance:
    id: str
    feast: str
    title: str
    details: str | None = None


@dataclass(frozen=True)
class Catalog:
    feasts: tuple[Feast, ...]
    namedays: tuple[Nameday, ...]
    observances: tuple[Observance, ...] = ()

    def feast_map(self) -> dict[str, Feast]:
        return {feast.id: feast for feast in self.feasts}
