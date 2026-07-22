from datetime import date
from pathlib import Path

import pytest

from grecal.generator import generate_namedays, select_namedays
from grecal.models import FeastType
from grecal.parser import load_catalog


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return load_catalog(ROOT / "data" / "feasts.yaml", ROOT / "data" / "names.yaml")


def test_production_dataset_has_expected_size() -> None:
    catalog = _catalog()
    assert len(catalog.feasts) == 584
    assert len(catalog.namedays) == 465
    assert sum(len(item.names) for item in catalog.namedays) == 1755
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


def test_panagiotis_group_celebrates_on_dormition_and_palm_sunday() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)
    panagiotis_names = {
        "Παναγιώτα",
        "Παναγιώτης",
        "Παναγούλα",
        "Παναγιούλα",
        "Τούλα",
    }

    assert panagiotis_names <= set(grouped[date(2026, 8, 15)])
    assert panagiotis_names <= set(grouped[date(2026, 4, 5)])


def test_christina_has_primary_and_additional_celebrations() -> None:
    catalog = _catalog()
    christina = next(item for item in catalog.namedays if item.id == "christina")
    grouped = generate_namedays(catalog, 2026, 2026)

    assert christina.feast == "feast_nativity_christ"
    assert christina.additional_feasts == ("feast_christina",)
    assert {"Χριστίνα", "Χριστιάνα"} <= set(grouped[date(2026, 12, 25)])
    assert {"Χριστίνα", "Χριστιάνα"} <= set(grouped[date(2026, 7, 24)])


def test_magdalini_celebrates_on_july_22_not_may_19() -> None:
    grouped = generate_namedays(_catalog(), 2026, 2026)

    assert "Μαγδαληνή" in grouped[date(2026, 7, 22)]
    assert "Μαγδαληνή" not in grouped.get(date(2026, 5, 19), ())


def test_existing_names_include_their_supported_july_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 7, 1): {"Ανάργυρος"},
        date(2026, 7, 7): {"Κίκα", "Ντομένικα", "Κορίνα"},
        date(2026, 7, 8): {"Θεοφίλη"},
        date(2026, 7, 11): {"Εύφη", "Εύφημος"},
        date(2026, 7, 12): {"Παΐσιος"},
        date(2026, 7, 17): {"Μαρίνος", "Αλίκη", "Αλεξάνδρα"},
        date(2026, 7, 18): {"Αιμιλιανή", "Αιμιλιανός"},
        date(2026, 7, 20): {"Λιάκος", "Ηλιάνα"},
        date(2026, 7, 25): {"Άννα", "Ολυμπία"},
        date(2026, 7, 24): {"Χριστινάκι"},
        date(2026, 7, 26): {"Παρασκευάς", "Πάρης", "Ζήλια"},
        date(2026, 7, 28): {"Ειρήνη", "Δρόσος", "Χρυσοβαλαντία"},
        date(2026, 7, 29): {"Θεόδοτος", "Θεοδότης"},
        date(2026, 7, 30): {"Ανδρόνικος", "Ανδρονίκη"},
        date(2026, 7, 31): {
            "Ιωσήφ",
            "Ζοζεφίνα",
            "Φρειδερίκος",
            "Φρειδερίκη",
        },
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert "Παΐσιος" in grouped[date(2026, 6, 19)]
    assert by_id["aimilios"].feast == "feast_aimilios"
    assert by_id["iliana"].feast == "feast_iliana"
    assert by_id["paraschos"].feast == "feast_paraschos"
    assert by_id["drosos"].feast == "feast_drosos"
    assert by_id["andronikos"].feast == "feast_andronikos"


def test_existing_names_include_their_supported_august_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 8, 3): {"Σαλώμα"},
        date(2026, 8, 4): {"Βιολέτα", "Εξακουστοδιανός"},
        date(2026, 8, 6): {"Σωτήρης", "Σωτήρω"},
        date(2026, 8, 7): {"Αστέρης", "Αστρούλα", "Αστερινός"},
        date(2026, 8, 8): {"Τριανταφύλλης", "Φυλλίτσα", "Ρόζα"},
        date(2026, 8, 10): {"Ήρων", "Ιππόλυτος", "Λώρα", "Λαυρέντης"},
        date(2026, 8, 15): {
            "Πάνος",
            "Γιώτα",
            "Μαίρη",
            "Ιεσθημανή",
            "Κρουστάλλω",
            "Πρεσβεία",
        },
        date(2026, 8, 16): {"Απόστολος", "Σεραφείμ", "Άλτσος"},
        date(2026, 8, 17): {"Στράτος", "Στράτων", "Στρατία", "Λευκοθέη"},
        date(2026, 8, 18): {"Αρσινόη", "Λάουρα"},
        date(2026, 8, 20): {"Ορέστης", "Θεοχάρης", "Ρηγίνος"},
        date(2026, 8, 24): {"Ευτύχιος", "Κοσμάς", "Διονύσιος"},
        date(2026, 8, 26): {"Ναταλίνα", "Αδριανή"},
        date(2026, 8, 27): {"Φανουρία", "Όσιος"},
        date(2026, 8, 30): {
            "Αλέξανδρος",
            "Αλεξάνδρα",
            "Αλέξιος",
            "Ευλάλιος",
        },
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["apostolos"].feast == "feast_apostolos"
    assert by_id["serafeim"].feast == "feast_serafeim"
    assert by_id["eystratios"].feast == "feast_eystratios_december"
    assert by_id["orestis"].feast == "feast_orestis"
    assert by_id["alexandra"].feast == "feast_saint_alexandra"
    assert by_id["alexios"].feast == "feast_alexios"


def test_existing_names_include_their_supported_september_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 9, 1): {"Ράνια", "Φρέγια", "Καλλιρόη", "Μόσχω"},
        date(2026, 9, 3): {"Άνθιμος", "Άνθιμη", "Αρίστη", "Πολυδώρα"},
        date(2026, 9, 4): {"Μωσής", "Μωϋσία"},
        date(2026, 9, 6): {"Ανδρόνικος", "Ανδρονίκη", "Ευδόξης"},
        date(2026, 9, 7): {"Κασιανή", "Κασσία"},
        date(2026, 9, 9): {"Άννα", "Άννη"},
        date(2026, 9, 11): {"Θεοδώρα", "Δώρα", "Ευάνθης"},
        date(2026, 9, 13): {"Αριστέα", "Άρης", "Αριστίνα"},
        date(2026, 9, 14): {"Σταυριανός", "Θεοκλής"},
        date(2026, 9, 16): {"Ευφημία", "Εύφημος", "Μελιτίνη"},
        date(2026, 9, 17): {"Αγάπιος", "Σοφιανή", "Αγαθόκλεια"},
        date(2026, 9, 20): {"Αγάπιος", "Θεόπιστος"},
        date(2026, 9, 22): {"Λουίζα", "Λοΐζος"},
        date(2026, 9, 23): {"Ίρις", "Ίριδα", "Ξανθή"},
        date(2026, 9, 24): {"Μυρτιδιώτισσα", "Μυρσώ", "Αμέρσα"},
        date(2026, 9, 25): {"Φρόσω", "Φροσούλα"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["andronikos"].feast == "feast_andronikos"
    assert by_id["anna"].feast == "feast_anna"
    assert by_id["theodora"].feast == "feast_theodora"
    assert by_id["eyfimia"].feast == "feast_eyfimia"
    assert by_id["agapios"].feast == "feast_agapios"
    assert "Κασσιανός" not in grouped[date(2026, 9, 16)]
    assert "Κοσμάς" not in grouped[date(2026, 9, 22)]
    assert "Γεράσιμος" not in grouped[date(2026, 9, 15)]


def test_existing_names_include_their_supported_december_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 12, 4): {"Σεραφείμ"},
        date(2026, 12, 13): {"Ευστράτιος", "Ευγένιος", "Λουκία", "Ορέστης"},
        date(2026, 12, 15): {"Σωσάννα"},
        date(2026, 12, 17): {"Διονύσιος", "Ρεβέκκα"},
        date(2026, 12, 18): {"Φλώρα"},
        date(2026, 12, 19): {"Άρης"},
        date(2026, 12, 20): {"Ιγνάτιος", "Ιγνάτης"},
        date(2026, 12, 21): {"Θεμιστοκλής", "Ιουλία"},
        date(2026, 12, 22): {"Αναστασία", "Νατάσα"},
        date(2026, 12, 28): {"Θεόφιλος", "Θεοφίλη"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert "Λουκάς" not in grouped[date(2026, 12, 13)]
    assert "Αναστάσιος" not in grouped[date(2026, 12, 22)]
    assert by_id["ignatios"].feast == "feast_ignatios_december"
    assert by_id["eystratios"].feast == "feast_eystratios_december"
    assert "Ιγνάτιος" in grouped[date(2026, 10, 14)]
    assert by_id["anastasia"].feast == "feast_orthodox_easter"
    assert by_id["anastasia"].additional_feasts == (
        "feast_anastasios_persian",
        "feast_anastasia_roman",
        "feast_anastasia_pharmakolytria",
    )
    assert by_id["revekka"].feast == "feast_revekka_december"
    assert {"Εμμανουήλ", "Μανώλης", "Εμμανουέλα"} <= set(
        grouped[date(2026, 12, 25)]
    )
    assert {"Εμμανουήλ", "Μανώλης", "Εμμανουέλα"} <= set(
        grouped[date(2026, 12, 26)]
    )


def test_existing_names_include_their_supported_january_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 1, 1): {"Βασίλης", "Τηλεμάχη", "Εμμέλεια"},
        date(2026, 1, 2): {"Σεραφείμ", "Σιλβέστρης"},
        date(2026, 1, 6): {"Φώτης", "Θεοφανία", "Ουρανία"},
        date(2026, 1, 16): {"Δανάη", "Δαν"},
        date(2026, 1, 17): {"Θεοδόσιος", "Αντώνης"},
        date(2026, 1, 21): {"Αγνούλα", "Νεόφυτος", "Πατρόκλεια"},
        date(2026, 1, 22): {"Αναστάσιος", "Αναστασία", "Ανέστης"},
        date(2026, 1, 23): {
            "Διονύσιος",
            "Κλήμης",
            "Κλημεντίνη",
            "Κλημεντίνα",
            "Κλεμεντίνη",
            "Κλεμεντίνα",
            "Αγαθάγγελος",
            "Αγαθαγγέλα",
            "Αγαθαγγέλη",
        },
        date(2026, 1, 24): {"Νεόφυτος", "Ξένια", "Ξένος"},
        date(2026, 1, 25): {"Γρηγόρης", "Μαργαρίτα"},
        date(2026, 1, 26): {"Ξένια", "Ξενοφώντας"},
        date(2026, 1, 27): {"Χρυσόστομος"},
        date(2026, 1, 29): {"Βαρσιμαίος", "Βαλσάμης"},
        date(2026, 1, 30): {"Χρυσή", "Χρυσαλία", "Μαύρος"},
        date(2026, 1, 31): {"Ευδοξούλα", "Κύρης"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["danai"].feast == "feast_danai_january"
    assert by_id["anastasios"].feast == "feast_orthodox_easter"
    assert by_id["anastasios"].additional_feasts == (
        "feast_anastasios_persian",
        "feast_anastasios_september",
    )
    assert by_id["neofytos"].feast == "feast_neofytos_recluse"
    assert by_id["klimis"].feast == "feast_klimis"
    assert "feast_clement_ancyra_agathangelos" in by_id["klimis"].additional_feasts
    assert by_id["klimentini"].feast == "feast_klimentini"
    assert (
        "feast_clement_ancyra_agathangelos"
        in by_id["klimentini"].additional_feasts
    )
    assert by_id["agathangelos"].feast == "feast_clement_ancyra_agathangelos"
    assert "Θεωνάς" not in grouped[date(2026, 1, 18)]
    assert "Ξένος" not in grouped[date(2026, 1, 26)]
    assert "Ξενοφών" not in grouped[date(2026, 1, 24)]
    assert "Χρυσαλία" not in grouped[date(2026, 12, 25)]

    assert "Φώτιος" in grouped[date(2026, 2, 6)]
    assert {"Θεοφάνης", "Θεοφανία"} <= set(grouped[date(2026, 3, 12)])
    assert "Κύριλλος" in grouped[date(2026, 6, 9)]
    assert "Αναστάσιος" in grouped[date(2026, 9, 17)]
    assert "Νεόφυτος" in grouped[date(2026, 9, 28)]


def test_existing_names_include_their_supported_february_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 2, 1): {"Τρύφωνας", "Τρυφωνία"},
        date(2026, 2, 2): {"Μαρία", "Μάριος", "Υπαπαντή"},
        date(2026, 2, 3): {"Σταμάτης", "Μάτα", "Ασημίνα", "Συμεών"},
        date(2026, 2, 4): {"Ισιδώρα", "Ισίδωρος", "Σιδέρης"},
        date(2026, 2, 5): {"Αγαθή", "Αγαθώ", "Αγαθία"},
        date(2026, 2, 6): {"Φωτεινή", "Φανή", "Φώτης"},
        date(2026, 2, 7): {"Λουκάς", "Λουκία", "Παρθένιος"},
        date(2026, 2, 8): {"Μάρθα", "Ζαχαρίας", "Ζάκης"},
        date(2026, 2, 10): {"Χαράλαμπος", "Χαρίκλεια", "Χάρης"},
        date(2026, 2, 11): {"Θεοδώρα", "Βλάσης", "Αυγή"},
        date(2026, 2, 12): {"Μελέτιος", "Μελέτης"},
        date(2026, 2, 15): {"Ευσέβιος", "Ευσεβεία", "Σέβη"},
        date(2026, 2, 17): {"Θεόδωρος", "Θεοδώρα", "Τεό", "Πουλχερία"},
        date(2026, 2, 19): {"Φιλόθεος", "Φιλοθέη"},
        date(2026, 2, 21): {"Ευστάθιος", "Στάθης"},
        date(2026, 2, 23): {"Πολύκαρπος", "Πολυχρόνιος"},
        date(2026, 2, 25): {"Ρηγίνος", "Ρηγίνα", "Ταράσιος"},
        date(2026, 2, 26): {"Φωτεινή", "Ανατολή"},
        date(2026, 2, 28): {"Κύρα", "Κυράτσα"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["foteini"].feast == "feast_foteini"
    assert by_id["eystathios"].feast == "feast_eystathios_september"
    assert by_id["theodoros"].feast == "feast_saint_theodore_saturday"
    assert by_id["teo"].feast == "feast_saint_theodore_saturday"
    assert by_id["maria"].feast == "feast_dormition"

    assert "Σταμάτης" in grouped[date(2026, 8, 16)]
    assert "Συμεών" in grouped[date(2026, 9, 1)]
    assert "Μελέτιος" in grouped[date(2026, 9, 1)]
    assert "Ζαχαρίας" in grouped[date(2026, 9, 5)]
    assert "Ευστάθιος" in grouped[date(2026, 9, 20)]
    assert "Ρηγίνος" in grouped[date(2026, 7, 16)]
    assert "Ρηγίνος" in grouped[date(2026, 8, 20)]
    assert "Μαρία" in grouped[date(2026, 11, 21)]
    assert "Φωτεινή" in grouped[date(2026, 5, 10)]


def test_existing_names_include_their_supported_may_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 5, 1): {"Ισιδώρα", "Ταμάρα"},
        date(2026, 5, 2): {"Αθανάσιος", "Αυγέρης"},
        date(2026, 5, 3): {"Ξένια", "Μαύρα", "Μαυρουδής", "Ροδώπη"},
        date(2026, 5, 4): {"Πελαγία", "Πελαγιώ"},
        date(2026, 5, 5): {
            "Ειρήνγκω",
            "Ειρηναίος",
            "Εφραίμ",
            "Ευφραίμ",
            "Ευφραίμιος",
            "Ευφραίμης",
            "Ευφραιμάκης",
            "Ευφραιμία",
            "Ευφραιμίτσα",
        },
        date(2026, 5, 8): {"Αρσένιος", "Αρσινόη", "Θολόγος", "Μήλιος"},
        date(2026, 5, 9): {"Χριστοφόρης", "Ησαΐας"},
        date(2026, 5, 10): {"Φωτεινή", "Σίμων"},
        date(2026, 5, 11): {"Αργύρης", "Αργυρώ", "Ασημίνα", "Όλια"},
        date(2026, 5, 12): {"Θεόδωρος", "Θεοδώρα", "Τεό"},
        date(2026, 5, 13): {"Γλυκερία", "Σέργιος", "Σεργιούλα"},
        date(2026, 5, 14): {"Ισιδώρα", "Ισίδωρος", "Τέλης"},
        date(2026, 5, 15): {"Αχιλλέας", "Καλή"},
        date(2026, 5, 17): {"Σόλωνας", "Σολόχων"},
        date(2026, 5, 18): {"Γαλατία", "Ιουλία"},
        date(2026, 5, 19): {"Θεόγνωστος", "Πατρίκιος"},
        date(2026, 5, 20): {"Λυδία", "Λήδα", "Λύδα"},
        date(2026, 5, 21): {"Κωστής", "Κωνσταντία", "Λένα"},
        date(2026, 5, 22): {"Εμιλία", "Μίλιος", "Καλή", "Κάλη"},
        date(2026, 5, 24): {"Φωτεινή", "Φωτούλα"},
        date(2026, 5, 29): {"Θεοδόσω"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert "lito" not in by_id
    assert "Λητώ" not in {
        name for names in grouped.values() for name in names
    }
    assert {"Καλή", "Κάλη"} <= set(grouped[date(2026, 4, 18)])
    assert by_id["efraim"].feast == "feast_ephraim_nea_makri"


def test_existing_names_include_their_supported_june_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 6, 1): {
            "Γερακίνα",
            "Ιέραξ",
            "Πύρρος",
            "Πύρα",
            "Τριάς",
            "Κορίνος",
        },
        date(2026, 6, 2): {"Μαρίνος"},
        date(2026, 6, 3): {"Υπατία", "Υπατούλα", "Υπάτιος"},
        date(2026, 6, 4): {"Μάρθα"},
        date(2026, 6, 5): {
            "Δωρόθεος",
            "Απόλλωνας",
            "Σεληνιάδα",
            "Νίκη",
        },
        date(2026, 6, 7): {"Σεβαστιανή", "Σεβαστούλα"},
        date(2026, 6, 8): {"Καλλιόπη", "Καλλιοπία", "Πόπη"},
        date(2026, 6, 9): {"Ροδάνθη", "Ροζάνθη", "Κύριλλος"},
        date(2026, 6, 11): {"Λουκάς", "Λουκία", "Ζαφείρης"},
        date(2026, 6, 12): {"Ονούφριος", "Ονούφρης", "Ονουφρία"},
        date(2026, 6, 14): {"Ελισσαίος", "Ελισσώ"},
        date(2026, 6, 15): {"Μόνικα", "Μόνα", "Αύγουστος", "Αυγούστα"},
        date(2026, 6, 19): {"Παΐσιος", "Ζήσιμος", "Ζήσης", "Ζώσιμος"},
        date(2026, 6, 22): {"Ευσέβιος", "Ευσεβεία", "Ζήνων"},
        date(2026, 6, 25): {"Φεβρωνία", "Φεύρω", "Φεβρούλα"},
        date(2026, 6, 26): {"Δαυίδ"},
        date(2026, 6, 28): {"Ανάργυρος"},
        date(2026, 6, 29): {"Πέτρος", "Πετράκης", "Παύλος", "Πάολα"},
        date(2026, 6, 30): {"Απόστολος", "Αποστόλης", "Αποστολίνα"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["ypatia"].feast == "feast_ypatia"
    assert by_id["zinon"].feast == "feast_zinon_september"
    assert by_id["paisios"].feast == "feast_paisios_athonite"
    assert by_id["zisimos"].feast == "feast_life_giving_spring"


def test_kassianos_is_celebrated_only_in_leap_years() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    leap_year = generate_namedays(catalog, 2024, 2024)
    common_year = generate_namedays(catalog, 2025, 2025)

    assert {"Κασσιανός", "Κασσιανή"} <= set(
        leap_year[date(2024, 2, 29)]
    )
    assert {"Κασσιανός", "Κασσιανή"}.isdisjoint(
        common_year[date(2025, 2, 28)]
    )
    assert by_id["kassianos"].feast == "feast_kassianos"
    assert by_id["kassiani"].feast == "feast_kassiani"
    assert "feast_kassianos" in by_id["kassiani"].additional_feasts
    assert "Κασσιανή" in leap_year[date(2024, 9, 7)]
    assert "Κασσιανή" in common_year[date(2025, 9, 7)]


def test_existing_names_include_their_supported_march_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 3, 1): {"Ευδοκούλα", "Πάρης", "Ρωξάνα"},
        date(2026, 3, 2): {"Ευθαλία", "Θάλεια"},
        date(2026, 3, 3): {"Κλεονίκη", "Νίκη"},
        date(2026, 3, 4): {"Γεράσιμος", "Μάκης"},
        date(2026, 3, 7): {"Ευγένιος", "Ευγένης"},
        date(2026, 3, 8): {"Γρηγόρης", "Θεοφύλακτος"},
        date(2026, 3, 9): {"Ηλιάννα", "Σμαραγδένια"},
        date(2026, 3, 11): {"Θεοδώρα", "Ζαμπίνα", "Σωφρόνιος"},
        date(2026, 3, 12): {"Φανή", "Θεοφάνης", "Θεοφανία"},
        date(2026, 3, 15): {"Αγάπη", "Αγάπιος"},
        date(2026, 3, 16): {"Χριστόδουλος", "Χριστοδούλη"},
        date(2026, 3, 17): {"Αλέξιος", "Αλέξης", "Αλέξα"},
        date(2026, 3, 18): {"Εδουάρδος", "Έντυ"},
        date(2026, 3, 20): {"Ροδιανός", "Ροδή"},
        date(2026, 3, 22): {"Δρόσος", "Δροσίδα", "Δρόσω"},
        date(2026, 3, 25): {"Ευάγγελος", "Βαγγέλης", "Άγγελος", "Εύα"},
        date(2026, 3, 26): {"Γαβριήλ", "Γαβριέλα"},
        date(2026, 3, 27): {"Λυδία", "Λήδα", "Λύδα"},
        date(2026, 3, 31): {"Υπατία", "Υπάτιος", "Ύπατος"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["eygenios"].feast == "feast_eygenios"
    assert "feast_eygenios_january" in by_id["eygenios"].additional_feasts
    assert by_id["lydia"].feast == "feast_lydia"
    assert "feast_lydia_march" in by_id["lydia"].additional_feasts
    assert "Ευγένιος" in grouped[date(2026, 1, 21)]
    assert "Λυδία" in grouped[date(2026, 5, 20)]


def test_existing_names_include_their_supported_april_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 4, 2): {"Τίτος", "Τίτα"},
        date(2026, 4, 4): {"Λάζαρος", "Λαζαρούλα"},
        date(2026, 4, 5): {"Παναγιώτης", "Βάιος", "Δάφνης"},
        date(2026, 4, 6): {"Ευτύχιος", "Ευτυχίτσα", "Έφη"},
        date(2026, 4, 10): {"Διονύσιος", "Ξενοφών", "Σωκράτης"},
        date(2026, 4, 12): {"Νατάσα", "Νεόφυτος", "Λαμπρίνα"},
        date(2026, 4, 14): {"Νικόλαος", "Ειρήνη", "Σάββας", "Ραφαήλ"},
        date(2026, 4, 15): {"Λεωνίδης", "Θεοχάρης", "Χαρούλα"},
        date(2026, 4, 16): {"Γαληνός", "Νίκη", "Χιονάτη"},
        date(2026, 4, 17): {"Ζωΐτσα", "Ζησούλα", "Κρηνιώ"},
        date(2026, 4, 19): {"Θωμάς", "Θωμαΐς", "Φιλίππα"},
        date(2026, 4, 21): {"Αλεξάνδρα", "Σάντρα"},
        date(2026, 4, 23): {"Γιώργος", "Γιωρίκας", "Γωγώ"},
        date(2026, 4, 24): {"Αχιλλεύς", "Δούκας", "Ελισσάβετ"},
        date(2026, 4, 25): {"Μάρκος", "Μαρκία", "Νίκη"},
        date(2026, 4, 29): {"Ιάσων", "Ιάσωνας"},
        date(2026, 4, 30): {
            "Αργυρώ",
            "Ασημίνα",
            "Μαλαματή",
            "Μίνα",
            "Δονάτα",
            "Ιακωβίνα",
        },
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    expected_primary_feasts = {
        "titos": "feast_titos_august",
        "sokratis": "feast_sokratis_october",
        "themistoklis": "feast_themistoklis_december",
        "zinon": "feast_zinon_september",
        "thomas": "feast_sunday_of_thomas",
        "iakovos": "feast_iakovos_april",
        "theocharis": "feast_theocharis",
    }
    for identity, feast in expected_primary_feasts.items():
        assert by_id[identity].feast == feast

    assert "Τίτος" in grouped[date(2026, 8, 25)]
    assert "Ζήνων" in grouped[date(2026, 9, 27)]
    assert "Σωκράτης" in grouped[date(2026, 10, 21)]
    assert "Θωμάς" in grouped[date(2026, 10, 6)]
    assert "Ιάκωβος" in grouped[date(2026, 10, 23)]
    assert "Θεμιστοκλής" in grouped[date(2026, 12, 21)]
    assert "Θεοχάρης" in grouped[date(2026, 8, 20)]
    assert "feast_bright_wednesday" in by_id["theocharis"].additional_feasts


def test_existing_names_include_their_supported_october_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 10, 1): {"Θηρεσία", "Θηρέσιος"},
        date(2026, 10, 4): {"Ιερόθεος", "Ιεροθέα", "Καλλισθένης"},
        date(2026, 10, 5): {"Χαριτίνη", "Χαριτίνα", "Χαρίτη"},
        date(2026, 10, 6): {"Θωμάς", "Τόμας"},
        date(2026, 10, 7): {"Πολυχρόνης", "Πολυχρονούλα"},
        date(2026, 10, 10): {"Αμαρυλλίς", "Αμαριλίζ", "Ευλάμπιος"},
        date(2026, 10, 12): {"Ανδρομάχη", "Ανδρόμαχος", "Συμεών"},
        date(2026, 10, 13): {"Χρυσή", "Φλωρέντιος", "Ντία"},
        date(2026, 10, 18): {"Λουκάς", "Μαρίνος"},
        date(2026, 10, 19): {"Κλεοπάτρα", "Κλειώ"},
        date(2026, 10, 20): {
            "Άρτεμις",
            "Αρτεμισία",
            "Αρτέμης",
            "Γεράσιμος",
            "Κερασία",
        },
        date(2026, 10, 21): {"Χριστόδουλος", "Χριστοδούλη"},
        date(2026, 10, 22): {"Αβέρκιος", "Αβερκία"},
        date(2026, 10, 24): {"Σεβαστιανή", "Σεβαστούλα"},
        date(2026, 10, 26): {"Δημήτρης", "Μήτσος", "Δημητρούλα", "Μιμίκα"},
        date(2026, 10, 27): {"Νέστωρ", "Νεστορία"},
        date(2026, 10, 29): {"Αναστασία", "Νατάσα", "Μελίνα", "Μελιτίνη"},
        date(2026, 10, 30): {"Αστέριος", "Άστρης", "Αστέρω", "Ζηνοβία", "Τζίνα"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["symeon"].feast == "feast_symeon"
    assert by_id["chrysi"].feast == "feast_chrysi"
    assert by_id["gerasimos"].feast == "feast_gerasimos"
    assert by_id["christodoylos"].feast == "feast_christodoylos"
    assert by_id["anastasia"].feast == "feast_orthodox_easter"
    assert by_id["natasa"].feast == "feast_natasa"
    assert "Αναστάσιος" not in grouped[date(2026, 10, 29)]


def test_existing_names_include_their_supported_november_celebrations() -> None:
    catalog = _catalog()
    by_id = {item.id: item for item in catalog.namedays}
    grouped = generate_namedays(catalog, 2026, 2026)

    expected = {
        date(2026, 11, 1): {
            "Αργύριος",
            "Κοσμάς",
            "Δαμιανός",
            "Ανάργυρος",
            "Δαβίδ",
        },
        date(2026, 11, 2): {"Αφθονία", "Αφθόνιος"},
        date(2026, 11, 5): {"Επιστήμη", "Σύλβια", "Σιλβάνα"},
        date(2026, 11, 7): {"Αθηνοδώρα", "Δώρης", "Σαλόνικος"},
        date(2026, 11, 8): {
            "Άγγελος",
            "Μιχάλης",
            "Σταμάτης",
            "Σεραφείμ",
            "Ταξούλα",
            "Γαβριηλίτσα",
            "Μιχαέλλα",
            "Στρατηγός",
            "Ταξιαρχούλα",
            "Ραφαήλ",
        },
        date(2026, 11, 9): {"Νεκτάρης", "Νεκταρίνα", "Μαυρούλα"},
        date(2026, 11, 10): {"Αρσένιος", "Ροδίων", "Ροζαλία"},
        date(2026, 11, 11): {"Βίκτορας", "Μηναΐς", "Μίνως", "Βικέντιος"},
        date(2026, 11, 14): {"Γρηγόριος", "Φιλιππής", "Φίλιππας"},
        date(2026, 11, 16): {"Ιφιγένεια", "Μαθαίος", "Ματθούλα"},
        date(2026, 11, 20): {"Σωσάννα", "Σωσάνα"},
        date(2026, 11, 21): {"Μαρία", "Μάριος", "Σούζυ", "Βιργινία"},
        date(2026, 11, 22): {"Φιλήμονας", "Φιλημονή"},
        date(2026, 11, 25): {"Κατερίνα", "Κάτια", "Μερκούρης"},
        date(2026, 11, 26): {
            "Στέλιος",
            "Στελίτσα",
            "Στέργης",
            "Στεργιούλα",
            "Παρέσια",
        },
        date(2026, 11, 29): {
            "Φαίδρος",
            "Φαιδρής",
            "Φαιδρινός",
            "Φαιδρούλα",
            "Φιλούμενος",
            "Φιλομίνα",
        },
        date(2026, 11, 30): {"Αντρέας", "Ανδρίκος", "Αντρούλα"},
    }
    for celebration_date, names in expected.items():
        assert names <= set(grouped[celebration_date])

    assert by_id["argyris"].feast == "feast_argyris"
    assert by_id["serafeim"].feast == "feast_serafeim"
    assert by_id["arsenios"].feast == "feast_arsenios"
    assert by_id["grigoris"].feast == "feast_grigoris"
    assert by_id["marios"].feast == "feast_marios"
    assert by_id["andreas"].feast == "feast_andreas"
    assert "Ανδρέας" in grouped[date(2026, 5, 15)]
    assert "Αγγελής" not in grouped[date(2026, 11, 8)]
    assert "Στρατής" not in grouped[date(2026, 11, 8)]
    assert "Τάνια" not in grouped[date(2026, 11, 21)]
    assert "Τέλης" not in grouped[date(2026, 11, 26)]
    assert "Σίλβα" not in grouped[date(2026, 11, 5)]


def test_documented_selection_examples_match_the_production_data() -> None:
    catalog = _catalog()

    top_100 = select_namedays(catalog.namedays, top=100)
    minimum_80 = select_namedays(catalog.namedays, min_popularity=80)

    assert (len(top_100), sum(len(item.names) for item in top_100)) == (100, 589)
    assert (len(minimum_80), sum(len(item.names) for item in minimum_80)) == (
        164,
        803,
    )
    assert len(generate_namedays(catalog, 2026, 2026, top=100)) == 110
    assert len(
        generate_namedays(catalog, 2026, 2026, min_popularity=80)
    ) == 155
