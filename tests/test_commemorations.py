from pathlib import Path
import re

from grecal.parser import _load_yaml, load_catalog


ROOT = Path(__file__).resolve().parents[1]
COMMEMORATIONS_PATH = ROOT / "data" / "commemorations.yaml"
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _collection():
    return _load_yaml(COMMEMORATIONS_PATH)


def _commemorations():
    return _collection()["commemorations"]


def _feast_mappings():
    return _collection()["feasts"]


def test_commemorations_are_a_standalone_validated_collection() -> None:
    collection = _collection()
    entries = _commemorations()
    mappings = _feast_mappings()

    assert isinstance(collection, dict)
    assert set(collection) == {"commemorations", "feasts"}
    assert isinstance(entries, list)
    assert entries
    assert all(isinstance(entry, dict) for entry in entries)
    assert all(set(entry) == {"id", "title"} for entry in entries)
    assert all(
        isinstance(entry["id"], str) and ID_PATTERN.fullmatch(entry["id"])
        for entry in entries
    )
    assert all(
        isinstance(entry["title"], str) and entry["title"].strip()
        for entry in entries
    )

    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids))
    titles = [entry["title"] for entry in entries]
    assert len(titles) == len(set(titles))
    assert len(entries) == 288

    assert isinstance(mappings, dict)
    assert mappings
    assert all(
        isinstance(feast_id, str) and feast_id.strip()
        for feast_id in mappings
    )
    assert all(
        isinstance(commemoration_ids, list) and commemoration_ids
        for commemoration_ids in mappings.values()
    )
    assert all(
        len(commemoration_ids) == len(set(commemoration_ids))
        for commemoration_ids in mappings.values()
    )
    referenced_ids = {
        commemoration_id
        for commemoration_ids in mappings.values()
        for commemoration_id in commemoration_ids
    }
    assert referenced_ids == set(ids)


def test_related_feast_rules_share_canonical_commemorations() -> None:
    mappings = _feast_mappings()

    assert mappings["feast_athina"] == ["ammon_and_forty_virgin_martyrs"]
    assert mappings["feast_afroditi"] == ["ammon_and_forty_virgin_martyrs"]
    assert mappings["feast_agapios_eustathios"] == ["eustathios_and_family"]
    assert mappings["feast_eystathios_september"] == ["eustathios_and_family"]
    assert mappings["feast_theopisti"] == ["eustathios_and_family"]
    assert mappings["feast_amaryllis"] == ["eulampios_and_eulampia"]
    assert mappings["feast_eylampia"] == ["eulampios_and_eulampia"]
    assert mappings["feast_artemis"] == ["artemios_the_great_martyr"]
    assert mappings["feast_artemios"] == ["artemios_the_great_martyr"]
    assert mappings["feast_ntiana"] == ["artemios_the_great_martyr"]
    assert mappings["feast_dimitra"] == ["demetrios_the_myrrh_streamer"]
    assert mappings["feast_dimitris"] == ["demetrios_the_myrrh_streamer"]
    assert mappings["feast_aggelos"] == [
        "synaxis_archangels_bodiless_powers"
    ]
    assert mappings["feast_synaxis_archangels"] == [
        "synaxis_archangels_bodiless_powers"
    ]
    assert mappings["feast_arsinoi"] == ["arsenios_of_cappadocia"]
    assert mappings["feast_arsenios_cappadocia"] == [
        "arsenios_of_cappadocia"
    ]


def test_every_commemoration_references_an_existing_feast_rule() -> None:
    catalog = load_catalog(
        ROOT / "data" / "feasts.yaml",
        ROOT / "data" / "names.yaml",
    )
    feast_ids = {feast.id for feast in catalog.feasts}

    assert set(_feast_mappings()) <= feast_ids


def test_observance_feasts_are_not_repeated_as_commemorations() -> None:
    catalog = load_catalog(
        ROOT / "data" / "feasts.yaml",
        ROOT / "data" / "names.yaml",
        ROOT / "data" / "observances.yaml",
    )
    observance_feasts = {
        observance.feast for observance in catalog.observances
    }

    assert set(_feast_mappings()).isdisjoint(observance_feasts)


def test_namedays_reuse_canonical_observance_feast_rules() -> None:
    catalog = load_catalog(
        ROOT / "data" / "feasts.yaml",
        ROOT / "data" / "names.yaml",
    )
    namedays = {item.id: item for item in catalog.namedays}

    assert namedays["sotiris"].feast == "feast_transfiguration"
    assert namedays["eymorfia"].feast == "feast_transfiguration"
    assert namedays["morfoyla"].feast == "feast_transfiguration"
    assert namedays["stayros"].feast == "feast_exaltation_holy_cross"
    assert namedays["soyltana"].feast == "feast_entry_theotokos"
    assert namedays["virginia"].feast == "feast_entry_theotokos"
    assert namedays["lemonia"].feast == "feast_entry_theotokos"


def test_requested_clement_and_ephraim_commemorations_are_mapped() -> None:
    entries = {entry["id"]: entry["title"] for entry in _commemorations()}
    mappings = _feast_mappings()

    assert entries["clement_of_ancyra_and_agathangelos"] == (
        "Άγιοι Κλήμης Επίσκοπος Αγκύρας και Αγαθάγγελος"
    )
    assert mappings["feast_clement_ancyra_agathangelos"] == [
        "clement_of_ancyra_and_agathangelos"
    ]
    assert entries["ephraim_of_nea_makri"] == (
        "Άγιος Εφραίμ ο εν Νέα Μάκρη Αττικής"
    )
    assert mappings["feast_ephraim_nea_makri"] == ["ephraim_of_nea_makri"]


def test_may_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_isidora",
        "feast_tamara",
        "feast_athanasius_relics",
        "feast_aygerinos",
        "feast_timothy_and_mavra",
        "feast_xenia_may",
        "feast_rodopi",
        "feast_pelagia_may",
        "feast_eirini",
        "feast_eirinaios_may",
        "feast_ephraim_nea_makri",
        "feast_serafeim",
        "feast_theologos",
        "feast_milios",
        "feast_arsenios_may",
        "feast_christoforos",
        "feast_isaias",
        "feast_simonas",
        "feast_olympia",
        "feast_argyris",
        "feast_theodoros_kithira",
        "feast_glykeria",
        "feast_sergios_may",
        "feast_aristotelis",
        "feast_isidoros_may",
        "feast_kali",
        "feast_kali_may22",
        "feast_bright_saturday",
        "feast_achillios_may",
        "feast_andreas_may",
        "feast_andronikos",
        "feast_solon",
        "feast_ioylia",
        "feast_galateia",
        "feast_theognostos",
        "feast_patrikios",
        "feast_lydia",
        "feast_konstantinos",
        "feast_aimilios",
        "feast_meletios_martyrs",
        "feast_theodosia",
        "feast_saint_emmeleia",
    } <= feast_ids


def test_june_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_gerakina",
        "feast_pyrros",
        "feast_marinos",
        "feast_ypatios_june",
        "feast_martha",
        "feast_dorotheos",
        "feast_selini",
        "feast_apollon",
        "feast_nikandros_june",
        "feast_sevastiani",
        "feast_kalliopi",
        "feast_rodanthi",
        "feast_kyrillos_june",
        "feast_zafeirios",
        "feast_luke_crimea",
        "feast_onoyfrios",
        "feast_elissaios",
        "feast_monika",
        "feast_aygoysta",
        "feast_aygoystinos",
        "feast_paisios",
        "feast_zosimos_june",
        "feast_eysevios",
        "feast_zenon_zenas",
        "feast_fevronia",
        "feast_david",
        "feast_anargyros",
        "feast_petros",
        "feast_paylos",
        "feast_apostolos",
    } <= feast_ids


def test_july_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_kosmas",
        "feast_anargyros_july",
        "feast_damianos",
        "feast_zoympoylia",
        "feast_yakinthos",
        "feast_kyriaki",
        "feast_theofilos",
        "feast_theofili_july",
        "feast_prokopis",
        "feast_amalia",
        "feast_olga",
        "feast_eyfimia",
        "feast_veroniki",
        "feast_paisios_athonite",
        "feast_sara",
        "feast_nikodimos",
        "feast_vladimiros",
        "feast_ioylitta",
        "feast_kirykos",
        "feast_riginos_july",
        "feast_marina",
        "feast_marinos_july",
        "feast_aliki",
        "feast_aimilianos_july",
        "feast_garyfallia",
        "feast_makrina",
        "feast_ilias",
        "feast_magdalini",
        "feast_markella",
        "feast_menelaos",
        "feast_christina",
        "feast_eypraxia",
        "feast_anna_dormition",
        "feast_olympia_deaconess",
        "feast_paraskeyi",
        "feast_paraskeyas_july",
        "feast_ersi",
        "feast_oraiozili",
        "feast_ermolaos",
        "feast_pantelis",
        "feast_chrysovalantis",
        "feast_eirini_chrysovalantou",
        "feast_drosida_july",
        "feast_theodoti",
        "feast_andronikos_july",
        "feast_freideriki",
        "feast_iosif_arimatheas",
    } <= feast_ids


def test_august_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_adriani",
        "feast_adrianos",
        "feast_alexandros",
        "feast_alkiviadis",
        "feast_apostolos_august",
        "feast_arsenios",
        "feast_asterios",
        "feast_astero",
        "feast_astrini",
        "feast_dionysis_relics_august",
        "feast_eirinaios",
        "feast_exakoystodianos",
        "feast_eylalios",
        "feast_eytychios_august",
        "feast_fanoyris",
        "feast_floros",
        "feast_gerasimos",
        "feast_gesthimani",
        "feast_ippolytos",
        "feast_iro",
        "feast_kosmas_aitolos",
        "feast_krystallo",
        "feast_laurus_august",
        "feast_layrentios",
        "feast_leykothea",
        "feast_lora",
        "feast_malamati",
        "feast_natalia",
        "feast_orestis_august",
        "feast_osios",
        "feast_presveia",
        "feast_riginos_august",
        "feast_salomi",
        "feast_serafeim_august",
        "feast_stamatios_august",
        "feast_straton_august",
        "feast_symela",
        "feast_theocharis",
        "feast_titos_august",
        "feast_triantafyllia",
        "feast_triantafyllos",
        "feast_violeta",
    } <= feast_ids


def test_september_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_afroditi",
        "feast_agapi",
        "feast_agapios_eustathios",
        "feast_agathoklis",
        "feast_akrivi",
        "feast_anastasios_september",
        "feast_andronikos_september",
        "feast_anthimos",
        "feast_antigoni",
        "feast_ariadni",
        "feast_aristea",
        "feast_aristeidis",
        "feast_archontia",
        "feast_aspasia",
        "feast_athina",
        "feast_chaido",
        "feast_charikleia",
        "feast_diamanto",
        "feast_elpiniki",
        "feast_elpida",
        "feast_erasmia",
        "feast_erato",
        "feast_ermioni",
        "feast_eyanthia",
        "feast_eydoxios",
        "feast_eyfimia_september",
        "feast_eyfrosyni",
        "feast_eystathios_september",
        "feast_eyterpi",
        "feast_foivos",
        "feast_ioakeim",
        "feast_iris",
        "feast_ismini",
        "feast_kalliroi",
        "feast_kassiani",
        "feast_kleoniki",
        "feast_kleopatra",
        "feast_klimentini",
        "feast_klimis",
        "feast_koralia",
        "feast_kornilios",
        "feast_kyriakos",
        "feast_loyiza",
        "feast_lygeri",
        "feast_margarita",
        "feast_meletios_september",
        "feast_melina",
        "feast_melpomeni",
        "feast_mitrodora",
        "feast_moscho",
        "feast_moysis",
        "feast_myrsini",
        "feast_myrto",
        "feast_neofytos_september",
        "feast_nikitas",
        "feast_oyrania",
        "feast_pandora",
        "feast_persefoni",
        "feast_pinelopi",
        "feast_polydoros",
        "feast_polymnia",
        "feast_polyniki",
        "feast_polytimi",
        "feast_polyxeni",
        "feast_poylcheria",
        "feast_rallia",
        "feast_rallis",
        "feast_sapfo",
        "feast_savvatios",
        "feast_sofia",
        "feast_sonia",
        "feast_symeon_september",
        "feast_terpsichori",
        "feast_thaleia",
        "feast_theano",
        "feast_thekla",
        "feast_theodora_september",
        "feast_theoklis",
        "feast_theonymfi",
        "feast_theopisti",
        "feast_tsampika",
        "feast_vissarion",
        "feast_xanthippi",
        "feast_zacharias_september",
        "feast_zinon_september",
        "feast_zografia",
    } <= feast_ids


def test_october_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_agathoniki",
        "feast_amaryllis",
        "feast_anastasia_roman",
        "feast_andromachi",
        "feast_artemios",
        "feast_artemis",
        "feast_asterios_october",
        "feast_averkios",
        "feast_avraam",
        "feast_charitini",
        "feast_christodoylos_october",
        "feast_chrysi_october",
        "feast_dimitra",
        "feast_dimitris",
        "feast_dionysis",
        "feast_eylampia",
        "feast_florentia",
        "feast_gerasimos_october",
        "feast_iakovos",
        "feast_ierotheos",
        "feast_ignatios",
        "feast_kallisthenis",
        "feast_kerasia",
        "feast_kleopatra_october",
        "feast_loykas",
        "feast_marinos_october",
        "feast_melitini_october",
        "feast_nestor",
        "feast_ntiana",
        "feast_orsalia",
        "feast_pelagia",
        "feast_polychronis",
        "feast_sergios",
        "feast_sevastiani_october",
        "feast_sokratis_october",
        "feast_symeon_new_theologian",
        "feast_thiresia",
        "feast_thomas",
        "feast_zinovia",
    } <= feast_ids


def test_november_nameday_rules_have_collected_commemorations() -> None:
    feast_ids = set(_feast_mappings())

    assert {
        "feast_afthonios",
        "feast_aggelos",
        "feast_aikaterini",
        "feast_anargyroi_november",
        "feast_andreas",
        "feast_arsenios_cappadocia",
        "feast_arsinoi",
        "feast_athinodoros",
        "feast_chrysostomos",
        "feast_david_evia",
        "feast_epistimi",
        "feast_faidra",
        "feast_filimon",
        "feast_filippa",
        "feast_filomeni",
        "feast_filippos",
        "feast_gavriil",
        "feast_gregory_palamas_november",
        "feast_ifigeneia",
        "feast_kyparissia",
        "feast_leonardos",
        "feast_matthaios",
        "feast_mayra",
        "feast_merkoyris",
        "feast_metaxia",
        "feast_michaela",
        "feast_michail",
        "feast_minas",
        "feast_minos",
        "feast_nektarios",
        "feast_orestis",
        "feast_rodion",
        "feast_silvanos_november",
        "feast_sossana_november",
        "feast_stergios",
        "feast_stratigos",
        "feast_stylianos",
        "feast_synaxis_archangels",
        "feast_taxiarchis",
        "feast_thessaloniki",
        "feast_vikentios",
        "feast_viktoras",
    } <= feast_ids
