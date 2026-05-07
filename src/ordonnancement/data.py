from typing import Self

from pydantic import BaseModel, NonNegativeFloat, PositiveFloat, model_validator


class Tache(BaseModel):
    nom: str
    duree: PositiveFloat
    prerequis: list[str]

    @model_validator(mode="after")
    def verifie_auto_prerequis(self) -> Self:
        """Vérifie que la tâche n'est pas son propre prérequis."""
        if self.nom in self.prerequis:
            raise ValueError("La tâche ne peut pas être son propre prérequis.")
        return self


class CahierDesCharges(BaseModel):
    taches: list[Tache]

    @model_validator(mode="after")
    def verifie_noms_distincts(self) -> Self:
        """Vérifie que les noms de tâches sont uniques."""
        noms: set[str] = set()
        for tache in self.taches:
            if tache.nom in noms:
                raise ValueError(f"Nom en double : '{tache.nom}'.")
            noms.add(tache.nom)
        return self

    @model_validator(mode="after")
    def verifie_prerequis_existants(self) -> Self:
        """Vérifie que tous les prérequis existent."""
        noms = {tache.nom for tache in self.taches}
        for tache in self.taches:
            for prerequis in tache.prerequis:
                if prerequis not in noms:
                    raise ValueError(f"Prérequis inconnu : '{prerequis}'.")
        return self

    def __getitem__(self, nom: str) -> Tache:
        """Renvoie une tâche à partir de son nom."""
        for tache in self.taches:
            if tache.nom == nom:
                return tache
        raise KeyError(f"Tâche introuvable : '{nom}'.")


class TachePlanifiee(BaseModel):
    tache: Tache
    debut: NonNegativeFloat
    fin: NonNegativeFloat
    debut_tard: NonNegativeFloat
    fin_tard: NonNegativeFloat

    @property
    def marge(self) -> float:
        """Renvoie la marge totale de la tâche."""
        return self.debut_tard - self.debut

    @property
    def est_critique(self) -> bool:
        """Indique si la tâche appartient au chemin critique."""
        return self.marge == 0.0


class Planning(BaseModel):
    cahier_des_charges: CahierDesCharges
    details: list[TachePlanifiee]

    @property
    def duree_totale(self) -> float:
        """Renvoie la durée totale du planning."""
        fins = [detail.fin for detail in self.details]
        return max(fins, default=0.0)

    @property
    def chemin_critique(self) -> list[str]:
        """Renvoie les noms des tâches critiques."""
        return [detail.tache.nom for detail in self.details if detail.est_critique]

    def __getitem__(self, nom: str) -> TachePlanifiee:
        """Renvoie une tâche planifiée à partir du nom de sa tâche."""
        for detail in self.details:
            if detail.tache.nom == nom:
                return detail
        raise KeyError(f"Tâche planifiée introuvable : '{nom}'.")