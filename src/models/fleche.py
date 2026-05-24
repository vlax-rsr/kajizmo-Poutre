# fleche.py
from .constant import *

def calcul_fleche(poutre) -> float:
    """Calcul la flèche à partir de l'équation de la ligne élastique."""
    # équation de la ligne élastique -> Poutre sur 2 appuis simples
    return poutre.M_ser_kNm * KN_TO_MN * (poutre.l_m) ** 2 * M_TO_CM / (
        4 * poutre.Eb_MPa * poutre.I_m4
    )

def verifier_fleche(poutre) -> dict:
    poutre.f_cm = round(calcul_fleche(poutre), 2)
    return {
        "f_cm":poutre.f_cm,
        "f_lim_cm":poutre.f_lim_cm,
        "condition":poutre.f_cm <= poutre.f_lim_cm,
    }