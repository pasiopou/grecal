from datetime import date
from pathlib import Path

from grecal.generator import generate_namedays, select_namedays
from grecal.models import FeastType
from grecal.parser import load_catalog


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return load_catalog(ROOT / "data" / "feasts.yaml", ROOT / "data" / "names.yaml")


def test_production_dataset_has_expected_size() -> None:
    catalog = _catalog()
    assert len(catalog.feasts) == 453
    assert len(catalog.namedays) == 457
    assert sum(len(item.names) for item in catalog.namedays) == 642
    assert {feast.type for feast in catalog.feasts} == set(FeastType)


def test_common_variants_are_present() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}

    assert "Γιάννης" in by_id["ioannis"].names
    assert "Κώστας" in by_id["konstantinos"].names
    assert {"Θανάσης", "Θάνος"} <= set(by_id["athanasios"].names)
    assert "Σπύρος" in by_id["spyridon"].names
    assert {"Γεώργιος", "Γιώργος", "Γεωργία"} <= set(
        by_id["georgios"].names
    )


def test_known_fixed_namedays_are_generated_and_grouped() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)

    assert {"Ιωάννης", "Ιωάννα", "Γιάννης"} <= set(
        grouped[date(2026, 1, 7)]
    )
    expected_athanasios_names = {
        "Αθανάσιος",
        "Αθανασία",
        "Θανάσης",
        "Θάνος",
    }
    assert expected_athanasios_names <= set(grouped[date(2026, 1, 18)])
    assert {"Κωνσταντίνος", "Κώστας"} <= set(
        grouped[date(2026, 5, 21)]
    )
    assert {"Σπυρίδων", "Σπύρος"} <= set(grouped[date(2026, 12, 12)])


def test_panagiotis_group_celebrates_on_dormition() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)
    panagiotis_names = {
        "Παναγιώτα",
        "Παναγιώτης",
        "Παναγούλα",
        "Παναγιούλα",
        "Τούλα",
    }

    assert panagiotis_names <= set(grouped[date(2026, 8, 15)])
    assert panagiotis_names.isdisjoint(grouped.get(date(2026, 4, 5), ()))


def test_documented_selection_examples_match_the_production_data() -> None:
    catalog = _catalog()

    top_100 = select_namedays(catalog.namedays, top=100)
    minimum_80 = select_namedays(catalog.namedays, min_popularity=80)

    assert (len(top_100), sum(len(item.names) for item in top_100)) == (100, 208)
    assert (len(minimum_80), sum(len(item.names) for item in minimum_80)) == (
        161,
        287,
    )
    assert len(generate_namedays(catalog, 2026, 2026, top=100)) == 76
    assert len(
        generate_namedays(catalog, 2026, 2026, min_popularity=80)
    ) == 108
