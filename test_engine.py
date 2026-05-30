# test_engine.py

from src.models.engine import Poutre
from src.models.formatting import afficher_resume


if __name__ == "__main__":
    # Exemple d'utilisation
    poutre = Poutre(
            b_cm=25, h_cm=60, l_m=6.93,
            fc28_MPa=25, fe_MPa=500, fis="FPP",
        )
    
    poutre.sollicitations(100, 50)

    print("\n".join(afficher_resume(poutre)))
    

    