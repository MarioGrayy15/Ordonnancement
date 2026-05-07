import pytest
from pydantic import ValidationError

from ordonnancement.data import CahierDesCharges, Planning, Tache, TachePlanifiee


def test_tache_refuse_duree_nulle():
    with pytest.raises(ValidationError):
        Tache(nom="A", duree=0.0, prerequis=[])


def test_tache_refuse_auto_prerequis():
    with pytest.raises(ValidationError):
        Tache(nom="A", duree=1.0, prerequis=["A"])


def test_cahier_refuse_noms_en_double():
    with pytest.raises(ValidationError):
        CahierDesCharges(
            taches=[
                Tache(nom="A", duree=1.0, prerequis=[]),
                Tache(nom="A", duree=2.0, prerequis=[]),
            ]
        )


def test_cahier_refuse_prerequis_inconnu():
    with pytest.raises(ValidationError):
        CahierDesCharges(
            taches=[
                Tache(nom="A", duree=1.0, prerequis=["B"]),
            ]
        )


@pytest.fixture
def cahier_simple() -> CahierDesCharges:
    return CahierDesCharges(
        taches=[
            Tache(nom="A", duree=1.0, prerequis=[]),
            Tache(nom="B", duree=2.0, prerequis=["A"]),
        ]
    )


@pytest.fixture
def planning_simple(cahier_simple: CahierDesCharges) -> Planning:
    return Planning(
        cahier_des_charges=cahier_simple,
        details=[
            TachePlanifiee(
                tache=cahier_simple["A"],
                debut=0.0,
                fin=1.0,
                debut_tard=0.0,
                fin_tard=1.0,
            ),
            TachePlanifiee(
                tache=cahier_simple["B"],
                debut=1.0,
                fin=3.0,
                debut_tard=1.0,
                fin_tard=3.0,
            ),
        ],
    )


def test_cahier_getitem(cahier_simple: CahierDesCharges):
    assert cahier_simple["A"].duree == 1.0


def test_cahier_getitem_introuvable(cahier_simple: CahierDesCharges):
    with pytest.raises(KeyError):
        cahier_simple["Z"]


def test_tache_planifiee_marge(cahier_simple: CahierDesCharges):
    tache_planifiee = TachePlanifiee(
        tache=cahier_simple["A"],
        debut=0.0,
        fin=1.0,
        debut_tard=2.0,
        fin_tard=3.0,
    )

    assert tache_planifiee.marge == 2.0


def test_tache_planifiee_est_critique(cahier_simple: CahierDesCharges):
    tache_planifiee = TachePlanifiee(
        tache=cahier_simple["A"],
        debut=0.0,
        fin=1.0,
        debut_tard=0.0,
        fin_tard=1.0,
    )

    assert tache_planifiee.est_critique is True


def test_planning_duree_totale(planning_simple: Planning):
    assert planning_simple.duree_totale == 3.0


def test_planning_chemin_critique(planning_simple: Planning):
    assert planning_simple.chemin_critique == ["A", "B"]


def test_planning_getitem(planning_simple: Planning):
    assert planning_simple["B"].debut == 1.0


def test_planning_getitem_introuvable(planning_simple: Planning):
    with pytest.raises(KeyError):
        planning_simple["Z"]


def test_serialisation_json_aller_retour(cahier_simple: CahierDesCharges):
    contenu = cahier_simple.model_dump_json()
    resultat = CahierDesCharges.model_validate_json(contenu)

    assert resultat == cahier_simple