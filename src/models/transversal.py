import math
from .constant import *

def calculer_ferraillage_transversale(poutre, nb_brin: int, phi_t: int) -> dict:
    """Section transversale"""
    A_t_trans_cm2 = poutre.calculer_section_reelle([(nb_brin, phi_t)])
    
    """Espacement calculé St et Stmax"""
    poutre.st_cm = round(
        0.9 * poutre.d_m / M_TO_CM * A_t_trans_cm2 * poutre.fsu_MPa / poutre.V_u_MN, 2
    )
    poutre.st_max_cm = min(
        0.9 * poutre.d_m * M_TO_CM,
        40,
        A_t_trans_cm2 * poutre.fe_MPa / (0.4 * poutre.b_cm),
    )

    """Répartition barres transversales"""
    # CAS 1 : st > st_max
    if poutre.st_cm > poutre.st_max_cm:

        return {
        "phi_t": phi_t,
        "nb_brin": nb_brin,
        "st0": repartition_non_caquot(poutre)["st0"],
        "st": repartition_non_caquot(poutre)["st"],
        "st_max": repartition_non_caquot(poutre)["st_max"],
        "disposition": repartition_non_caquot(poutre)["disposition"],
    }

    # CAS 2 : st <= st_max
    return {
        "phi_t": phi_t,
        "nb_brin": nb_brin,
        "st0": repartition_caquot(poutre)["st0"],
        "st": repartition_caquot(poutre)["st"],
        "st_max": repartition_caquot(poutre)["st_max"],
        "disposition": repartition_caquot(poutre)["disposition"],
    }

def repartition_non_caquot(poutre):
    poutre.st0_cm = poutre.st_max_cm / 2
    poutre.disposition = [round(poutre.st0_cm, 2)]
    distance = poutre.st0_cm

    while distance < poutre.l_demi_cm:
        distance += poutre.st_max_cm
        poutre.disposition.append(poutre.st_max_cm)

    return {
        "st0": poutre.st0_cm,
        "st": poutre.st_cm,
        "st_max": poutre.st_max_cm,
        "disposition": poutre.disposition,
    }

def repartition_caquot(poutre):
    poutre.st0_cm = poutre.st_cm / 2
    repetition = math.ceil(poutre.l_m / 2)
    poutre.disposition = [round(poutre.st0_cm, 2)]

    v_inutiles = [x for x in SUITE_CAQUOT if x <= poutre.st_cm]
    st_debut = max(v_inutiles) if v_inutiles else SUITE_CAQUOT[0]
    
    suite_utilisee = [x for x in SUITE_CAQUOT if x >= st_debut]
    
    distance = poutre.st0_cm
    for d in suite_utilisee:
        for _ in range(repetition):
            distance += d
            if distance > poutre.l_demi_cm:
                return {
                    "st0": poutre.st0_cm,
                    "st": poutre.st_cm,
                    "st_max": poutre.st_max_cm,
                    "disposition": poutre.disposition,
                }
            poutre.disposition.append(d)

    return {
        "st0": poutre.st0_cm,
        "st": poutre.st_cm,
        "st_max": poutre.st_max_cm,
        "disposition": poutre.disposition,        
    }