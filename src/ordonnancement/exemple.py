from ordonnancement.data import CahierDesCharges, Tache

CAHIER_MAISON = CahierDesCharges(
    taches=[
        Tache(nom="A", duree=3, prerequis=[]),
        Tache(nom="B", duree=4, prerequis=["A", "I"]),
        Tache(nom="C", duree=1, prerequis=["B"]),
        Tache(nom="D", duree=4, prerequis=[]),
        Tache(nom="E", duree=2, prerequis=["D", "H"]),
        Tache(nom="F", duree=5, prerequis=["E", "I"]),
        Tache(nom="G", duree=1, prerequis=[]),
        Tache(nom="H", duree=3, prerequis=["G"]),
        Tache(nom="I", duree=5, prerequis=["H"]),
        Tache(nom="J", duree=6, prerequis=[]),
        Tache(nom="K", duree=3, prerequis=["J", "I"]),
        Tache(nom="L", duree=14, prerequis=[]),
        Tache(nom="M", duree=2, prerequis=["I"]),
        Tache(nom="N", duree=2, prerequis=["M", "L"]),
        Tache(nom="O", duree=3, prerequis=["M", "F", "C"]),
        Tache(nom="P", duree=3, prerequis=["O", "N"]),
        Tache(nom="Q", duree=2, prerequis=["P"]),
        Tache(nom="R", duree=1, prerequis=["N", "K", "O"]),
        Tache(nom="S", duree=3, prerequis=["R"]),
    ]
)

LIVRAISONS = ["A", "D", "J", "L"]