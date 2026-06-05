import pytest

from ordonnancement.data import CahierDesCharges, Tache
from ordonnancement.exemple import CAHIER_MAISON, LIVRAISONS
from ordonnancement.resolution import (
    _serialise_groupe,
    a_une_solution,
    construit_graphe,
    resoud_avec_groupe_non_simultane,
    resoud_ordonnancement,
)


@pytest.fixture
def cahier_simple() -> CahierDesCharges:
    return CahierDesCharges(
        taches=[
            Tache(nom="A", duree=1.0, prerequis=[]),
            Tache(nom="B", duree=2.0, prerequis=["A"]),
            Tache(nom="C", duree=1.0, prerequis=["A"]),
            Tache(nom="D", duree=3.0, prerequis=["B", "C"]),
        ]
    )


@pytest.fixture
def cahier_cycle() -> CahierDesCharges:
    return CahierDesCharges(
        taches=[
            Tache(nom="A", duree=1.0, prerequis=["B"]),
            Tache(nom="B", duree=1.0, prerequis=["A"]),
        ]
    )


def test_construit_graphe_contient_les_noeuds(cahier_simple: CahierDesCharges):
    graphe = construit_graphe(cahier=cahier_simple)

    assert set(graphe.nodes) == {"A", "B", "C", "D"}


def test_construit_graphe_contient_les_aretes(cahier_simple: CahierDesCharges):
    graphe = construit_graphe(cahier=cahier_simple)

    assert graphe.has_edge("A", "B")
    assert graphe.has_edge("A", "C")
    assert graphe.has_edge("B", "D")
    assert graphe.has_edge("C", "D")


def test_construit_graphe_stocke_les_durees(cahier_simple: CahierDesCharges):
    graphe = construit_graphe(cahier=cahier_simple)

    assert graphe.nodes["A"]["duree"] == 1.0
    assert graphe.edges["A", "B"]["duree"] == 1.0


def test_a_une_solution_si_pas_de_cycle(cahier_simple: CahierDesCharges):
    assert a_une_solution(cahier=cahier_simple) is True


def test_a_une_solution_si_cycle(cahier_cycle: CahierDesCharges):
    assert a_une_solution(cahier=cahier_cycle) is False


def test_resoud_ordonnancement_simple(cahier_simple: CahierDesCharges):
    planning = resoud_ordonnancement(cahier=cahier_simple)

    assert planning["A"].debut == 0.0
    assert planning["A"].fin == 1.0
    assert planning["B"].debut == 1.0
    assert planning["C"].debut == 1.0
    assert planning["D"].debut == 3.0
    assert planning.duree_totale == 6.0


def test_resoud_ordonnancement_dates_tard(cahier_simple: CahierDesCharges):
    planning = resoud_ordonnancement(cahier=cahier_simple)

    assert planning["A"].debut_tard == 0.0
    assert planning["B"].debut_tard == 1.0
    assert planning["C"].debut_tard == 2.0
    assert planning["D"].debut_tard == 3.0


def test_resoud_ordonnancement_chemin_critique(cahier_simple: CahierDesCharges):
    planning = resoud_ordonnancement(cahier=cahier_simple)

    assert planning.chemin_critique == ["A", "B", "D"]


def test_resoud_ordonnancement_refuse_cycle(cahier_cycle: CahierDesCharges):
    with pytest.raises(ValueError):
        resoud_ordonnancement(cahier=cahier_cycle)


def test_serialise_groupe_ajoute_des_prerequis(cahier_simple: CahierDesCharges):
    cahier = _serialise_groupe(cahier=cahier_simple, groupe=["A", "C"])

    assert cahier["C"].prerequis == ["A", "A"]


def test_groupe_vide(cahier_simple: CahierDesCharges):
    planning = resoud_avec_groupe_non_simultane(cahier=cahier_simple, groupe=[])

    assert planning.duree_totale == 6.0


def test_groupe_un_seul_element(cahier_simple: CahierDesCharges):
    planning = resoud_avec_groupe_non_simultane(cahier=cahier_simple, groupe=["A"])

    assert planning.duree_totale == 6.0


def test_groupe_non_simultane(cahier_simple: CahierDesCharges):
    planning = resoud_avec_groupe_non_simultane(
        cahier=cahier_simple,
        groupe=["B", "C"],
    )

    assert planning.duree_totale == 7.0


def test_groupe_non_simultane_impossible(cahier_cycle: CahierDesCharges):
    with pytest.raises(ValueError):
        resoud_avec_groupe_non_simultane(
            cahier=cahier_cycle,
            groupe=["A", "B"],
        )


def test_exemple_maison_duree_totale():
    planning = resoud_ordonnancement(cahier=CAHIER_MAISON)

    assert planning.duree_totale == 22.0


def test_exemple_maison_livraisons_non_simultanees():
    planning = resoud_avec_groupe_non_simultane(
        cahier=CAHIER_MAISON,
        groupe=LIVRAISONS,
    )

    assert planning.duree_totale == 34.0
    assert planning.chemin_critique == ["A", "D", "J", "L", "N", "P", "Q"]