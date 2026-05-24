from .constant import *
from math import sqrt
from .exceptions import *

def calculer_ferraillage_elu(poutre) -> dict:
        """Calcule le besoin d'acier a l'etat limite ultime."""
        mu = poutre.M_u_MNm / (
             poutre.b_m * (poutre.d_m**2) * poutre.fbu_MPa
        )
        
        sol = {
            "utilite": True,
            "config": "Simple",
            "pivot": "A",
            "mu": round(mu, 3),
            "alpha": None,
            "z": None,
            "M_r": None,
            "sigma_sc": None,
            "A_c": None,
            "A_t": None,
        }

        # Armatures comprimés si µ >= µ_lim
        if mu >= MU_LIM:
            sol["config"] = "Double"
            sol["pivot"] = "B"
            sol["alpha"] = ALPHA_LIM
            sol["z"] = round(poutre.d_m * (1 - 0.4 * ALPHA_LIM), 3)
            sol["M_r"] = round(MU_LIM * poutre.b_m * poutre.d_m**2 * poutre.fbu_MPa, 3)
            sol["sigma_sc"] = poutre.fsu_MPa
            sol["A_c"] = round(
                (
                    (poutre.M_u_MNm - sol["M_r"])
                    / ((poutre.d_m - poutre.d_prim_m) * sol["sigma_sc"])
                )
                * M2_TO_CM2,
                2,
            )
            sol["A_t"] = round(
                (
                    (
                        (sol["M_r"] / sol["z"])
                        + ((poutre.M_u_MNm - sol["M_r"]) / (poutre.d_m - poutre.d_prim_m))
                    )
                    * (1 / poutre.fsu_MPa)
                )
                * M2_TO_CM2,
                2,
            )
        else:
            sol["alpha"] = round(1.25 * (1 - sqrt(1 - 2 * mu)), 3)
            sol["z"] = round(poutre.d_m * (1 - 0.4 * sol["alpha"]), 3)
            sol["A_t"] = round(
                (poutre.M_u_MNm / (poutre.fsu_MPa * sol["z"])) * M2_TO_CM2, 2
            )

        if poutre.fis == "FTP":
            sol["utilite"] = False

        return sol

def calculer_ferraillage_els(poutre) -> dict:
        """Calcule le besoin d'acier a l'etat limite de service."""
        alpha_bar = (COEF_EQUIVALENCE * poutre.sigma_bc_bar_MPa) / (
            COEF_EQUIVALENCE * poutre.sigma_bc_bar_MPa + poutre.sigma_st_bar_MPa
        )
        y1 = alpha_bar * poutre.d_m
        z_els = poutre.d_m * (1 - alpha_bar / 3)
        m_rsb = 0.5 * poutre.b_m * y1 * poutre.sigma_bc_bar_MPa * z_els

        sol = {
            "utilite": True,
            "config": "Simple",
            "alpha": round(alpha_bar, 3),
            "y1": round(y1, 3),
            "z": round(z_els, 3),
            "M_rsb": round(m_rsb, 3),
            "sigma_sc": None,
            "A_c": None,
            "A_t": None,
        }

        if poutre.M_ser_MNm > m_rsb:
            sol["config"] = "Double"
            sol["sigma_sc"] = round(
                (COEF_EQUIVALENCE * poutre.sigma_bc_bar_MPa * (y1 - poutre.d_prim_m) / y1),
                2,
            )
            sol["A_c"] = round(
                (
                    (poutre.M_ser_MNm - m_rsb)
                    / ((poutre.d_m - poutre.d_prim_m) * sol["sigma_sc"])
                )
                * M2_TO_CM2,
                2,
            )
            sol["A_t"] = round(
                (
                    (
                        (m_rsb / z_els)
                        + ((poutre.M_ser_MNm - m_rsb) / (poutre.d_m - poutre.d_prim_m))
                    )
                    * (1 / poutre.sigma_st_bar_MPa)
                )
                * M2_TO_CM2,
                2,
            )
        
        else:
            sol["A_t"] = round(
                (poutre.M_ser_MNm / (z_els * poutre.sigma_st_bar_MPa)) * M2_TO_CM2, 2
            )

        if poutre.fis == "FPP":
            sol["utilite"] = False
        return sol

def calculer_ferraillage_longitudinal(poutre) -> dict:
        """Retourne la section longitudinale finale par enveloppe ELU/ELS."""
        res_elu = calculer_ferraillage_elu(poutre)
        res_els = calculer_ferraillage_els(poutre)

        a_t_elu = res_elu["A_t"] if poutre.fis != "FTP" else 0
        a_t_els = res_els["A_t"] if poutre.fis != "FPP" else 0
        a_t_final = max(a_t_elu, a_t_els, poutre.A_min_cm2)

        a_c_elu = res_elu["A_c"] or 0
        a_c_els = res_els["A_c"] or 0
        a_c_final = max(a_c_elu, a_c_els)

        # C'est ici qu'on lève l'erreur spécifique
        if a_t_final > poutre.A_max_cm2:
            raise SectionDepasseeError(
                f"La section d'acier tendu dépasse le maximum admissible ({a_t_final:.2f} cm² >{poutre.A_max_cm2:.2f} cm²)."
            )

        return {
            "A_t_final_cm2": a_t_final,
            "A_c_final_cm2": a_c_final,
            "A_min_cm2": poutre.A_min_cm2,
            "A_max_cm2": poutre.A_max_cm2,
            "res_elu": res_elu,
            "res_els": res_els,
            "condition": a_t_final <= poutre.A_max_cm2,
            "arm_comp": a_c_final != 0,
        }