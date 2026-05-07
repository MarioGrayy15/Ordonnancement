from itertools import permutations

import networkx as nx

from ordonnancement.data import CahierDesCharges, Planning, TachePlanifiee


def construit_graphe(cahier: CahierDesCharges) -> nx.DiGraph:
    """Construit le graphe de précédences à partir du cahier des charges."""
    resultat: nx.DiGraph = nx.DiGraph()
    for tache in cahier.taches:
        resultat.add_node(tache.nom, duree=tache.duree)
    for tache in cahier.taches:
        for prerequis in tache.prerequis:
            resultat.add_edge(prerequis, tache.nom, duree=cahier[prerequis].duree)
    return resultat


def a_une_solution(cahier: CahierDesCharges) -> bool:
    """Détecte si le cahier des charges admet une solution."""
    return nx.algorithms.is_directed_acyclic_graph(construit_graphe(cahier=cahier))


def _calcule_dates_tard(graphe: nx.DiGraph, dates_tot: dict[str, float]) -> dict[str, tuple[float, float]]:
    """Calcule les dates au plus tard pour chaque tâche."""
    duree_totale = max(
        dates_tot[nom_tache] + graphe.nodes[nom_tache]["duree"]
        for nom_tache in graphe.nodes
    )
    resultat: dict[str, tuple[float, float]] = {}
    for nom_tache in reversed(list(nx.algorithms.topological_sort(graphe))):
        successeurs = list(graphe.successors(nom_tache))
        if successeurs:
            fin_tard = min(resultat[successeur][0] for successeur in successeurs)
        else:
            fin_tard = duree_totale
        debut_tard = fin_tard - graphe.nodes[nom_tache]["duree"]
        resultat[nom_tache] = (debut_tard, fin_tard)
    return resultat


def resoud_ordonnancement(cahier: CahierDesCharges, debut: float = 0.0) -> Planning:
    """Résout le problème d'ordonnancement par tri topologique."""
    graphe = construit_graphe(cahier=cahier)
    if not nx.algorithms.is_directed_acyclic_graph(graphe):
        raise ValueError("Le graphe contient un cycle.")
    dates_tot: dict[str, float] = {}
    for nom_tache in nx.algorithms.topological_sort(graphe):
        tache = cahier[nom_tache]
        fins_prerequis = [
            dates_tot[prerequis] + cahier[prerequis].duree
            for prerequis in tache.prerequis
        ]
        dates_tot[nom_tache] = max(fins_prerequis, default=debut)
    dates_tard = _calcule_dates_tard(graphe=graphe, dates_tot=dates_tot)
    details: list[TachePlanifiee] = []
    for nom_tache in nx.algorithms.topological_sort(graphe):
        tache = cahier[nom_tache]
        debut_tache = dates_tot[nom_tache]
        debut_tard, fin_tard = dates_tard[nom_tache]
        details.append(
            TachePlanifiee(
                tache=tache,
                debut=debut_tache,
                fin=debut_tache + tache.duree,
                debut_tard=debut_tard,
                fin_tard=fin_tard,
            )
        )
    return Planning(cahier_des_charges=cahier, details=details)


def _serialise_groupe(cahier: CahierDesCharges, groupe: list[str]) -> CahierDesCharges:
    """Ajoute des précédences pour empêcher les tâches du groupe d'être simultanées."""
    taches = []
    for tache in cahier.taches:
        prerequis = list(tache.prerequis)
        position = groupe.index(tache.nom) if tache.nom in groupe else -1
        if position > 0:
            prerequis.append(groupe[position - 1])
        taches.append(tache.model_copy(update={"prerequis": prerequis}))
    return CahierDesCharges(taches=taches)


def resoud_avec_groupe_non_simultane(
    cahier: CahierDesCharges,
    groupe: list[str],
    debut: float = 0.0,
) -> Planning:
    """Résout le planning en imposant qu'un groupe de tâches ne soit pas simultané."""
    if len(groupe) <= 1:
        return resoud_ordonnancement(cahier=cahier, debut=debut)

    meilleur_planning: Planning | None = None
    for ordre in permutations(groupe):
        cahier_modifie = _serialise_groupe(cahier=cahier, groupe=list(ordre))
        if a_une_solution(cahier=cahier_modifie):
            planning = resoud_ordonnancement(cahier=cahier_modifie, debut=debut)
            if meilleur_planning is None or planning.duree_totale < meilleur_planning.duree_totale:
                meilleur_planning = planning

    if meilleur_planning is None:
        raise ValueError("Aucun ordre ne permet de satisfaire la contrainte.")

    return meilleur_planning