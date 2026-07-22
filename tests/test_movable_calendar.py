from datetime import date
from pathlib import Path

import pytest

from grecal.generator import generate_namedays
from grecal.parser import load_catalog


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(ROOT / "data" / "feasts.yaml", ROOT / "data" / "names.yaml")


def test_movable_rules_match_expected_2026_dates(catalog) -> None:
    grouped = generate_namedays(catalog, 2026, 2026)

    assert "Θεόδωρος" in grouped[date(2026, 2, 28)]
    assert "Ρωξάνη" in grouped[date(2026, 3, 1)]
    assert "Λάζαρος" in grouped[date(2026, 4, 4)]
    assert {"Βαΐα", "Βάιος", "Βάγια", "Δάφνη"} <= set(
        grouped[date(2026, 4, 5)]
    )
    assert {
        "Αναστασία",
        "Αναστάσιος",
        "Ανέστης",
        "Πασχάλης",
    } <= set(grouped[date(2026, 4, 12)])
    assert {"Ραφαέλα", "Ραφαήλ"} <= set(grouped[date(2026, 4, 14)])
    assert {"Θεοχάρης", "Θεοχαρούλα"} <= set(
        grouped[date(2026, 4, 15)]
    )
    expected_life_giving_spring_names = {
        "Ζήσης",
        "Ζήσιμος",
        "Ζωή",
        "Πηγή",
        "Πολυζώης",
    }
    assert expected_life_giving_spring_names <= set(
        grouped[date(2026, 4, 17)]
    )
    assert {"Γεώργιος", "Γιώργος", "Γεωργία"} <= set(
        grouped[date(2026, 4, 23)]
    )
    assert "Μάρκος" in grouped[date(2026, 4, 25)]
    assert "Μυροφόρα" in grouped[date(2026, 4, 26)]
    assert "Νεφέλη" in grouped[date(2026, 5, 21)]
    assert {"Κορίνα", "Τριάδα"} <= set(grouped[date(2026, 6, 1)])
    assert {
        "Αδάμ",
        "Δανάη",
        "Εύα",
        "Ισαάκ",
        "Ραχήλ",
        "Ρεβέκκα",
    } <= set(grouped[date(2026, 12, 13)])


def test_movable_rules_follow_easter_in_2024(catalog) -> None:
    grouped = generate_namedays(catalog, 2024, 2024)

    assert "Λάζαρος" in grouped[date(2024, 4, 27)]
    assert "Αναστασία" in grouped[date(2024, 5, 5)]
    assert "Γιώργος" in grouped[date(2024, 5, 6)]
    assert "Μάρκος" in grouped[date(2024, 5, 7)]
    assert "Θεοχάρης" in grouped[date(2024, 5, 8)]
    assert "Θεοχάρης" in grouped[date(2024, 8, 20)]
    assert "Θεοχάρης" not in grouped.get(date(2024, 4, 15), ())
    assert "Νεφέλη" in grouped[date(2024, 6, 13)]
    assert "Τριάδα" in grouped[date(2024, 6, 24)]
    assert "Αδάμ" in grouped[date(2024, 12, 15)]


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, date(2024, 6, 2)),
        (2025, date(2025, 5, 18)),
        (2026, date(2026, 5, 10)),
    ],
)
def test_samaritan_woman_sunday_is_four_weeks_after_easter(
    catalog, year: int, expected: date
) -> None:
    grouped = generate_namedays(catalog, year, year)

    assert "Φωτεινή" in grouped[expected]


def test_saint_george_moves_when_april_23_is_easter(catalog) -> None:
    grouped = generate_namedays(catalog, 2006, 2006)
    assert "Γιώργος" not in grouped.get(date(2006, 4, 23), ())
    assert "Γιώργος" in grouped[date(2006, 4, 24)]
