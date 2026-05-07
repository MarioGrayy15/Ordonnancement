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
    from ordonnancement.resolution import (
        a_une_solution,
        construit_graphe,
        resoud_avec_groupe_non_simultane,
        resoud_ordonnancement,
    )
    from ordonnancement.exemple import CAHIER_MAISON, LIVRAISONS
    return (
        CahierDesCharges,
        LIVRAISONS,
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
    groupe = mo.ui.multiselect(options=[], label="Tâches non simultanées")
    mo.vstack([mo.md("### Fichier JSON"), fichier, groupe])
    return fichier, groupe


@app.cell
def _(CahierDesCharges, ValidationError, fichier):
    try:
        contenu = fichier.value[0].contents.decode("utf-8")
        cahier = CahierDesCharges.model_validate_json(contenu)
    except (IndexError, ValidationError):
        cahier = CAHIER_MAISON
    return (cahier,)


@app.cell
def _(cahier, groupe):
    options = [tache.nom for tache in cahier.taches]
    groupe.options = options
    if not groupe.value:
        groupe.value = []
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
def _(df, mo):
    mo.ui.table(df)
    return


@app.cell
def _(construit_graphe, nx, planning, plt):
    graphe = construit_graphe(planning.cahier_des_charges)
    pos = nx.spring_layout(graphe, seed=42)

    critiques = set(planning.chemin_critique)
    couleurs_noeuds = [
        "red" if node in critiques else "lightblue" for node in graphe.nodes
    ]
    couleurs_arretes = [
        "red" if u in critiques and v in critiques else "gray"
        for u, v in graphe.edges
    ]

    plt.figure()
    nx.draw(
        graphe,
        pos,
        with_labels=True,
        node_color=couleurs_noeuds,
        edge_color=couleurs_arretes,
    )
    plt.title("Graphe des tâches (chemin critique en rouge)")
    plt.show()
    return


@app.cell
def _(mo, planning):
    mo.md(f"### Durée totale : {planning.duree_totale:g} semaines")
    mo.md(f"### Chemin critique : {' → '.join(planning.chemin_critique)}")
    return