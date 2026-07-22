"""Load and validate Grecal's YAML source-of-truth files."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from .models import Catalog, Feast, FeastType, Nameday, Observance


class DataValidationError(ValueError):
    """Raised when the nameday YAML data does not match the schema."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> Any:
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None,
                None,
                f"expected a mapping node, but found {node.id}",
                node.start_mark,
            )
        self.flatten_mapping(node)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def _load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return yaml.load(stream, Loader=_UniqueKeySafeLoader)
    except OSError as exc:
        raise DataValidationError(f"cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise DataValidationError(f"invalid YAML in {path}: {exc}") from exc


def _required_string(data: Mapping[str, Any], field: str, context: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DataValidationError(f"{context}.{field} must be a non-empty string")
    return value.strip()


def _optional_int(data: Mapping[str, Any], field: str, context: str) -> int | None:
    value = data.get(field)
    if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
        raise DataValidationError(f"{context}.{field} must be an integer")
    return value


def _parse_feasts(raw: Any) -> tuple[Feast, ...]:
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise DataValidationError("feasts.yaml must contain a mapping")

    feasts: list[Feast] = []
    seen_ids: set[str] = set()
    for feast_id, value in raw.items():
        context = f"feast {feast_id!r}"
        if not isinstance(feast_id, str) or not feast_id.strip():
            raise DataValidationError("every feast id must be a non-empty string")
        cleaned_feast_id = feast_id.strip()
        if cleaned_feast_id in seen_ids:
            raise DataValidationError(f"duplicate feast id: {cleaned_feast_id}")
        seen_ids.add(cleaned_feast_id)
        if not isinstance(value, Mapping):
            raise DataValidationError(f"{context} must be a mapping")
        try:
            feast_type = FeastType(_required_string(value, "type", context))
        except ValueError as exc:
            supported = ", ".join(item.value for item in FeastType)
            raise DataValidationError(
                f"{context}.type must be one of: {supported}"
            ) from exc

        month = _optional_int(value, "month", context)
        day = _optional_int(value, "day", context)
        offset = _optional_int(value, "offset", context)
        rule_value = value.get("rule")
        if rule_value is not None and (
            not isinstance(rule_value, str) or not rule_value.strip()
        ):
            raise DataValidationError(f"{context}.rule must be a non-empty string")
        rule = rule_value.strip() if isinstance(rule_value, str) else None

        if (month is None) != (day is None):
            raise DataValidationError(
                f"{context} must provide month and day together"
            )
        if month is not None and day is not None:
            try:
                date(2000, month, day)
            except ValueError as exc:
                raise DataValidationError(f"{context} has an invalid date") from exc

        if feast_type is FeastType.FIXED:
            if month is None:
                raise DataValidationError(
                    f"{context} requires integer month and day fields"
                )
        elif feast_type is FeastType.OFFSET_FROM_EASTER and offset is None:
            raise DataValidationError(f"{context} requires an integer offset field")
        elif feast_type is FeastType.CUSTOM and rule is None:
            raise DataValidationError(f"{context} requires a rule field")

        feasts.append(
            Feast(
                id=cleaned_feast_id,
                type=feast_type,
                month=month,
                day=day,
                offset=offset,
                rule=rule,
            )
        )
    return tuple(feasts)


def _parse_namedays(raw: Any) -> tuple[Nameday, ...]:
    if raw is None:
        raw = []
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise DataValidationError("names.yaml must contain a list")

    namedays: list[Nameday] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for index, value in enumerate(raw):
        context = f"names.yaml entry {index}"
        if not isinstance(value, Mapping):
            raise DataValidationError(f"{context} must be a mapping")
        nameday_id = _required_string(value, "id", context)
        if nameday_id in seen_ids:
            raise DataValidationError(f"duplicate nameday id: {nameday_id}")
        seen_ids.add(nameday_id)
        feast_id = _required_string(value, "feast", context)
        additional_feasts_value = value.get("additional_feasts", ())
        if not isinstance(additional_feasts_value, Sequence) or isinstance(
            additional_feasts_value, (str, bytes)
        ):
            raise DataValidationError(
                f"{context}.additional_feasts must be a list"
            )
        if any(
            not isinstance(feast, str) or not feast.strip()
            for feast in additional_feasts_value
        ):
            raise DataValidationError(
                f"{context}.additional_feasts must contain only non-empty strings"
            )
        additional_feasts = tuple(
            feast.strip() for feast in additional_feasts_value
        )
        if len(set(additional_feasts)) != len(additional_feasts):
            raise DataValidationError(
                f"{context}.additional_feasts contains duplicates"
            )
        if feast_id in additional_feasts:
            raise DataValidationError(
                f"{context}.additional_feasts repeats the primary feast"
            )
        popularity = value.get("popularity")
        if (
            not isinstance(popularity, int)
            or isinstance(popularity, bool)
            or not 0 <= popularity <= 100
        ):
            raise DataValidationError(
                f"{context}.popularity must be an integer from 0 to 100"
            )
        names = value.get("names")
        if (
            not isinstance(names, Sequence)
            or isinstance(names, (str, bytes))
            or not names
        ):
            raise DataValidationError(f"{context}.names must be a non-empty list")
        if any(not isinstance(name, str) or not name.strip() for name in names):
            raise DataValidationError(
                f"{context}.names must contain only non-empty strings"
            )
        cleaned_names = tuple(name.strip() for name in names)
        if len(set(cleaned_names)) != len(cleaned_names):
            raise DataValidationError(f"{context}.names contains duplicates")
        repeated_names = sorted(set(cleaned_names) & seen_names)
        if repeated_names:
            raise DataValidationError(
                "duplicate display names across entries: " + ", ".join(repeated_names)
            )
        seen_names.update(cleaned_names)
        namedays.append(
            Nameday(
                id=nameday_id,
                feast=feast_id,
                popularity=popularity,
                names=cleaned_names,
                additional_feasts=additional_feasts,
            )
        )
    return tuple(namedays)


def _parse_observances(raw: Any) -> tuple[Observance, ...]:
    if raw is None:
        raw = []
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise DataValidationError("observances.yaml must contain a list")

    observances: list[Observance] = []
    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    for index, value in enumerate(raw):
        context = f"observances.yaml entry {index}"
        if not isinstance(value, Mapping):
            raise DataValidationError(f"{context} must be a mapping")
        observance_id = _required_string(value, "id", context)
        if observance_id in seen_ids:
            raise DataValidationError(f"duplicate observance id: {observance_id}")
        seen_ids.add(observance_id)
        feast_id = _required_string(value, "feast", context)
        title = _required_string(value, "title", context)
        if title in seen_titles:
            raise DataValidationError(f"duplicate observance title: {title}")
        seen_titles.add(title)
        details_value = value.get("details")
        if details_value is not None and (
            not isinstance(details_value, str) or not details_value.strip()
        ):
            raise DataValidationError(f"{context}.details must be a non-empty string")
        details = details_value.strip() if isinstance(details_value, str) else None
        observances.append(
            Observance(
                id=observance_id,
                feast=feast_id,
                title=title,
                details=details,
            )
        )
    return tuple(observances)


def load_catalog(
    feasts_path: Path,
    names_path: Path,
    observances_path: Path | None = None,
) -> Catalog:
    """Load YAML data and validate all feast cross-references.

    Omitting ``observances_path`` loads a nameday-only catalog.
    """

    feasts = _parse_feasts(_load_yaml(feasts_path))
    namedays = _parse_namedays(_load_yaml(names_path))
    observances = (
        _parse_observances(_load_yaml(observances_path))
        if observances_path is not None
        else ()
    )
    feast_ids = {feast.id for feast in feasts}
    nameday_feast_ids = {
        feast_id for item in namedays for feast_id in item.feasts
    }
    missing_namedays = sorted(nameday_feast_ids - feast_ids)
    if missing_namedays:
        raise DataValidationError(
            "names.yaml references unknown feast ids: "
            + ", ".join(missing_namedays)
        )
    missing_observances = sorted(
        {item.feast for item in observances} - feast_ids
    )
    if missing_observances:
        raise DataValidationError(
            "observances.yaml references unknown feast ids: "
            + ", ".join(missing_observances)
        )
    return Catalog(
        feasts=feasts,
        namedays=namedays,
        observances=observances,
    )
