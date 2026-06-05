import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import matplotlib.pyplot as plt
    import networkx as nx
    from pydantic import ValidationError
    from ordonnancement.data import CahierDesCharges
    from ordonnancement.exemple import CAHIER_MAISON
    from ordonnancement.resolution import (
        a_une_solution,
        construit_graphe,
        resoud_avec_groupe_non_simultane,
        resoud_ordonnancement,
    )

    return (
        CAHIER_MAISON,
        CahierDesCharges,
        ValidationError,
        a_une_solution,
        construit_graphe,
        mo,
        nx,
        pl,
        plt,
        resoud_avec_groupe_non_simultane,
        resoud_ordonnancement,
    )


@app.cell
def _(mo):
    fichier = mo.ui.file(filetypes=[".json"])
    mo.md("### Fichier JSON")
    fichier
    return (fichier,)


@app.cell
def _(CAHIER_MAISON, CahierDesCharges, ValidationError, fichier):
    try:
        contenu = fichier.value[0].contents.decode("utf-8")
        cahier = CahierDesCharges.model_validate_json(contenu)
    except (IndexError, ValidationError):
        cahier = CAHIER_MAISON
    return (cahier,)


@app.cell
def _(cahier, mo):
    options = [tache.nom for tache in cahier.taches]
    groupe = mo.ui.multiselect(options=options, label="Tâches non simultanées")
    groupe
    return (groupe,)


@app.cell
def _(
    a_une_solution,
    cahier,
    groupe,
    mo,
    resoud_avec_groupe_non_simultane,
    resoud_ordonnancement,
):
    if not a_une_solution(cahier):
        mo.stop("Le graphe contient un cycle.")

    if groupe.value:
        planning = resoud_avec_groupe_non_simultane(
            cahier=cahier,
            groupe=list(groupe.value),
        )
    else:
        planning = resoud_ordonnancement(cahier=cahier)

    return (planning,)


@app.cell
def _(planning, pl):
    df = pl.DataFrame(
        [
            {
                "Tâche": d.tache.nom,
                "Durée": d.tache.duree,
                "Début": d.debut,
                "Fin": d.fin,
                "Marge": d.marge,
                "Critique": d.est_critique,
            }
            for d in planning.details
        ]
    )
    return (df,)


@app.cell
def _(df, mo, planning):
    mo.vstack(
        [
            mo.md(f"### Durée totale : {planning.duree_totale:g} semaines"),
            mo.ui.table(df),
            mo.md(f"### Chemin critique : {' → '.join(planning.chemin_critique)}"),
        ]
    )
    return


@app.cell
def _(construit_graphe, mo, nx, planning, plt):
    graphe = construit_graphe(planning.cahier_des_charges)
    pos = nx.spring_layout(graphe, seed=42)

    critiques = set(planning.chemin_critique)
    couleurs_noeuds = [
        "red" if noeud in critiques else "lightblue" for noeud in graphe.nodes
    ]
    couleurs_arretes = [
        "red" if depart in critiques and arrivee in critiques else "gray"
        for depart, arrivee in graphe.edges
    ]

    figure, axe = plt.subplots()
    nx.draw(
        graphe,
        pos,
        ax=axe,
        with_labels=True,
        node_color=couleurs_noeuds,
        edge_color=couleurs_arretes,
    )
    axe.set_title("Graphe des tâches")
    mo.mpl.interactive(figure)
    return 

def main() -> None:
    """Lance l'interface graphique Marimo."""
    import subprocess
    import sys
    from pathlib import Path

    chemin = Path(__file__).resolve()
    commande = [sys.executable, "-m", "marimo", "run", str(chemin)]
    subprocess.run(commande, check=True)


if __name__ == "__main__":
    main()