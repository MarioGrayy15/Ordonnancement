from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ordonnancement.data import CahierDesCharges, Planning
from ordonnancement.exemple import CAHIER_MAISON, LIVRAISONS
from ordonnancement.resolution import resoud_avec_groupe_non_simultane, resoud_ordonnancement

app = typer.Typer()
console = Console()


def _affiche_planning(planning: Planning) -> None:
    """Affiche un planning sous forme de tableau."""
    table = Table(title=f"Durée totale : {planning.duree_totale:g} semaines")
    table.add_column("Tâche")
    table.add_column("Durée", justify="right")
    table.add_column("Début tôt", justify="right")
    table.add_column("Fin tôt", justify="right")
    table.add_column("Début tard", justify="right")
    table.add_column("Fin tard", justify="right")
    table.add_column("Marge", justify="right")
    table.add_column("Critique")

    for detail in planning.details:
        table.add_row(
            detail.tache.nom,
            f"{detail.tache.duree:g}",
            f"{detail.debut:g}",
            f"{detail.fin:g}",
            f"{detail.debut_tard:g}",
            f"{detail.fin_tard:g}",
            f"{detail.marge:g}",
            "oui" if detail.est_critique else "non",
        )

    console.print(table)
    console.print(f"Chemin critique : {' → '.join(planning.chemin_critique)}")


@app.command()
def exemple() -> None:
    """Résout l'exemple de construction de maison."""
    planning = resoud_ordonnancement(cahier=CAHIER_MAISON)
    _affiche_planning(planning=planning)


@app.command()
def exemple_contraint() -> None:
    """Résout l'exemple avec les livraisons non simultanées."""
    planning = resoud_avec_groupe_non_simultane(
        cahier=CAHIER_MAISON,
        groupe=LIVRAISONS,
    )
    _affiche_planning(planning=planning)


@app.command()
def depuis_fichier(chemin: Path) -> None:
    """Résout un cahier des charges depuis un fichier JSON."""
    contenu = chemin.read_text(encoding="utf-8")
    cahier = CahierDesCharges.model_validate_json(contenu)
    planning = resoud_ordonnancement(cahier=cahier)
    _affiche_planning(planning=planning)

if __name__ == "__main__":
    app()
