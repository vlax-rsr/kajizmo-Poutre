# test_engine.py

from src.models.engine import Poutre
from src.models.formatting import *

# Exemple d'utilisation
poutre = Poutre(
        b_cm=25, h_cm=60, l_m=6.93,
        fc28_MPa=25, fe_MPa=500, fis="FPP",
        M_u_kNm=154, M_ser_kNm=113, V_u_kN=163
    )

print("-" * 70 + "\n")
print(poutre.calculer_ferraillage_longitudinal())
print("-" * 70 + "\n")
print(poutre.verifier_cisaillement())
print("-" * 70 + "\n")
print(poutre.calculer_ferraillage_transversale(nb_brin=4, phi_t=6))
print("-" * 70 + "\n")
print(poutre.verifier_fleche())
print("-" * 70 + "\n")
print(afficher_resume(poutre))
print("-" * 70 + "\n")
print("\n".join(afficher_result_long(poutre)))
print("-" * 70 + "\n")
print("\n".join(afficher_result_trans(poutre, phi_t=6, nb_brins=4)))
