# Ordonnancement de tâches (CPM)

Librairie Python permettant de résoudre des problèmes d’ordonnancement de tâches avec contraintes de précédence, basée sur la méthode CPM (Critical Path Method).

---

## Description

Ce projet permet de :

- modéliser un ensemble de tâches avec durées et prérequis
- calculer un planning optimal (dates au plus tôt / au plus tard)
- identifier les marges et le chemin critique
- déterminer la durée totale d’un projet
- gérer des contraintes supplémentaires : tâches non simultanées

---

## Installation

### 1. Installer les dépendances

```bash
uv sync
```
### 2. Activer l’environnement (optionnel)
```bash
.venv\Scripts\activate
```
### Utilisation en Python
```python
from ordonnancement.data import CahierDesCharges, Tache
from ordonnancement.resolution import resoud_ordonnancement

cahier = CahierDesCharges(
    taches=[
        Tache(nom="A", duree=1.0, prerequis=[]),
        Tache(nom="B", duree=2.0, prerequis=["A"]),
    ]
)

planning = resoud_ordonnancement(cahier)

print(planning.duree_totale)
print(planning.chemin_critique)
```
### Interface en ligne de commande (CLI)

### Exemple simple
```bash
ordonnancement exemple
```

### Exemple avec contrainte
```bash
ordonnancement exemple-contraint
```

### Depuis un fichier JSON
```bash
ordonnancement depuis-fichier chemin/vers/fichier.json
```
### Format JSON attendu
```json
{
  "taches": [
    { "nom": "A", "duree": 1.0, "prerequis": [] },
    { "nom": "B", "duree": 2.0, "prerequis": ["A"] }
  ]
}
```

### Interface graphique
```bash
marimo run src/ordonnancement/app.py
```
### Fonctionnalités

- import d’un fichier JSON
- sélection de tâches non simultanées
- affichage du planning
- visualisation du graphe avec chemin critique

### Tests
```bash
pytest
```
Avec couverture :
```bash
pytest --cov
```
### Développement
```bash
ruff check .
ruff format .
```

## Structure du projet
ordonnancement/
├── src/ordonnancement/
│   ├── data.py
│   ├── resolution.py
│   ├── exemple.py
│   ├── cli.py
│   ├── app.py
│   └── __init__.py
├── tests/
├── pyproject.toml
└── README.md


Projet réalisé dans le cadre d’un TP d’ordonnancement.

