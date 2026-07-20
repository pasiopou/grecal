from pathlib import Path

import pytest

from grecal.models import FeastType
from grecal.parser import DataValidationError, load_catalog


def _write(path: Path, value: str) -> Path:
    path.write_text(value, encoding="utf-8")
    return path


def test_load_catalog_validates_and_builds_models(tmp_path: Path) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "saint_andrew:\n  type: fixed\n  month: 11\n  day: 30\n",
    )
    names = _write(
        tmp_path / "names.yaml",
        "- id: andreas\n  feast: saint_andrew\n  popularity: 95\n"
        "  names: [Ανδρέας]\n",
    )

    catalog = load_catalog(feasts, names)

    assert catalog.feasts[0].type is FeastType.FIXED
    assert catalog.namedays[0].names == ("Ανδρέας",)


def test_load_catalog_rejects_unknown_feast(tmp_path: Path) -> None:
    feasts = _write(tmp_path / "feasts.yaml", "{}\n")
    names = _write(
        tmp_path / "names.yaml",
        "- id: andreas\n  feast: missing\n  popularity: 95\n"
        "  names: [Ανδρέας]\n",
    )

    with pytest.raises(DataValidationError, match="unknown feast ids: missing"):
        load_catalog(feasts, names)


def test_load_catalog_rejects_duplicate_yaml_mapping_keys(tmp_path: Path) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "same: {type: fixed, month: 1, day: 1}\n"
        "same: {type: fixed, month: 1, day: 2}\n",
    )
    names = _write(tmp_path / "names.yaml", "[]\n")

    with pytest.raises(DataValidationError, match="duplicate key 'same'"):
        load_catalog(feasts, names)


def test_load_catalog_rejects_feast_ids_duplicated_after_trimming(
    tmp_path: Path,
) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "same: {type: fixed, month: 1, day: 1}\n"
        "' same ': {type: fixed, month: 1, day: 2}\n",
    )
    names = _write(tmp_path / "names.yaml", "[]\n")

    with pytest.raises(DataValidationError, match="duplicate feast id: same"):
        load_catalog(feasts, names)


def test_load_catalog_rejects_display_name_used_by_two_entries(tmp_path: Path) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "one: {type: fixed, month: 1, day: 1}\n"
        "two: {type: fixed, month: 1, day: 2}\n",
    )
    names = _write(
        tmp_path / "names.yaml",
        "- {id: first, feast: one, popularity: 50, names: [Μαρία]}\n"
        "- {id: second, feast: two, popularity: 40, names: [Μαρία]}\n",
    )

    with pytest.raises(DataValidationError, match="duplicate display names"):
        load_catalog(feasts, names)


def test_load_catalog_optionally_loads_observances(tmp_path: Path) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "pascha: {type: offset_from_easter, offset: 0}\n",
    )
    names = _write(tmp_path / "names.yaml", "[]\n")
    observances = _write(
        tmp_path / "observances.yaml",
        "- id: pascha\n"
        "  feast: pascha\n"
        "  title: Πάσχα (Ανάσταση)\n"
        "  details: Κινητή εορτή\n",
    )

    nameday_only = load_catalog(feasts, names)
    with_observances = load_catalog(feasts, names, observances)

    assert nameday_only.observances == ()
    assert with_observances.observances[0].title == "Πάσχα (Ανάσταση)"
    assert with_observances.observances[0].details == "Κινητή εορτή"


def test_load_catalog_rejects_observance_with_unknown_feast(tmp_path: Path) -> None:
    feasts = _write(tmp_path / "feasts.yaml", "{}\n")
    names = _write(tmp_path / "names.yaml", "[]\n")
    observances = _write(
        tmp_path / "observances.yaml",
        "- {id: pascha, feast: missing, title: Πάσχα}\n",
    )

    with pytest.raises(DataValidationError, match="observances.yaml.*missing"):
        load_catalog(feasts, names, observances)


@pytest.mark.parametrize("popularity", [-1, 101, "high"])
def test_load_catalog_rejects_invalid_popularity(
    tmp_path: Path, popularity: object
) -> None:
    feasts = _write(
        tmp_path / "feasts.yaml",
        "saint_andrew: {type: fixed, month: 11, day: 30}\n",
    )
    names = _write(
        tmp_path / "names.yaml",
        f"- id: andreas\n  feast: saint_andrew\n  popularity: {popularity}\n"
        "  names: [Ανδρέας]\n",
    )

    with pytest.raises(DataValidationError, match="popularity"):
        load_catalog(feasts, names)
