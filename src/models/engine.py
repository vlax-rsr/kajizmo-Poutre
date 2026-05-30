import math
from math import sqrt

from dataclasses import dataclass, field

from .constant import *
from .longitudinal import *
from .exceptions import *
from .cisaillement import *
from .transversal import *
from .fleche import *
from .charge import sollicitations
from .formatting import afficher_resume


"""Moteur BAEL pour calculer les armatures longitudinales et transversales."""

@dataclass
class Poutre:
    """Represente une poutre BA et expose ses verifications normatives."""

    b_cm: float
    h_cm: float
    l_m: float
    fc28_MPa: float
    fe_MPa: float
    fis: str
    M_u_kNm: float = 0.00
    M_ser_kNm: float = 0.00
    V_u_kN: float = 0.00
    type_barre: str = "HA"

    b_m: float = field(init=False)
    h_m: float = field(init=False)
    M_u_MNm: float = field(init=False)
    M_ser_MNm: float = field(init=False)
    V_u_MN: float = field(init=False)
    d_m: float = field(init=False)
    d_prim_m: float = field(init=False)
    ft28_MPa: float = field(init=False)
    fbu_MPa: float = field(init=False)
    fsu_MPa: float = field(init=False)
    A_min_cm2: float = field(init=False)
    A_max_cm2: float = field(init=False)
    sigma_bc_bar_MPa: float = field(init=False)
    sigma_st_bar_MPa: float = field(init=False)
    tau_lim_MPa: float = field(init=False)
    tau_u_MPa: float = field(init=False)
    st0_cm: float = field(init=False)
    st_cm: float = field(init=False)
    st_max_cm: float = field(init=False)
    Eb_MPa: float = field(init=False)
    I_m4: float = field(init=False)
    f_lim_cm: float = field(init=False)
    f_cm: float = field(init=False)
    l_demi_cm: float = field(init=False)
    A_t_final_cm2: float = field(init=False)
    A_c_final_cm2: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialise les parametres derives a partir des donnees d'entree."""
        self._calculer_parametres_derives()


    def _calculer_parametres_derives(self) -> None:
        """Calcule les grandeurs intermediaires utilisees par les methodes."""
        self.b_m = self.b_cm / 100
        self.h_m = self.h_cm / 100
        self.l_demi_cm = self.l_m * M_TO_CM / 2
        self.I_m4 = self.b_m * self.h_m ** 3 / 12

        if self.l_m <= 5:
            self.f_lim_cm = self.l_m * M_TO_CM / 500
        else:
            self.f_lim_cm = 0.5 + self.l_m * M_TO_CM / 1000

        self.M_u_MNm = self.M_u_kNm * KN_TO_MN
        self.M_ser_MNm = self.M_ser_kNm * KN_TO_MN
        self.V_u_MN = self.V_u_kN * KN_TO_MN

        self.d_m = 0.9 * self.h_m
        self.d_prim_m = 0.05

        self.ft28_MPa = round(0.06 * self.fc28_MPa + 0.6, 2)
        self.fbu_MPa = round(0.85 * self.fc28_MPa / GAMMA_B, 2)
        self.fsu_MPa = math.ceil(self.fe_MPa / GAMMA_S)

        self.Eb_MPa = 11000 * self.fc28_MPa ** (1/3)

        self.A_min_cm2 = (
            0.23 * self.ft28_MPa * self.b_m * self.d_m / self.fe_MPa
        ) * M2_TO_CM2
        self.A_max_cm2 = 0.05 * self.b_cm * self.h_cm

        self.sigma_bc_bar_MPa = 0.6 * self.fc28_MPa
        self.sigma_st_bar_MPa = self._calculer_contrainte_acier_els()

        if self.fis == "FPP":
            self.tau_lim_MPa = min(round(0.20 * self.fc28_MPa / GAMMA_B, 2), 5.0)
        else:
            self.tau_lim_MPa = min(round(0.15 * self.fc28_MPa / GAMMA_B, 2), 4.0)

        self.tau_u_MPa = self.V_u_MN / (self.b_m * self.h_m)


    def _calculer_contrainte_acier_els(self) -> float:
        """Calcule la contrainte admissible des aciers a l'ELS."""
        coef_fiss = COEF_FISSURATION.get(self.type_barre, COEF_FISSURATION["HA"])
        limites_sigma_st = {
            "FPP": self.fe_MPa,
            "FP": min(
                2 * self.fe_MPa / 3,
                max(0.5 * self.fe_MPa, 110 * sqrt(coef_fiss * self.ft28_MPa)),
            ),
            "FTP": min(
                0.5 * self.fe_MPa,
                max(0.5 * self.fe_MPa, 90 * sqrt(coef_fiss * self.ft28_MPa)),
            ),
        }
        return round(limites_sigma_st.get(self.fis, limites_sigma_st["FP"]), 2)


    def calculer_ferraillage_longitudinal(self) -> dict:
        """Retourne la section longitudinale finale"""
        self.A_t_final_cm2 = calculer_ferraillage_longitudinal(self)["A_t_final_cm2"]
        self.A_c_final_cm2 = calculer_ferraillage_longitudinal(self)["A_c_final_cm2"]
        return calculer_ferraillage_longitudinal(self)
    

    def verifier_cisaillement(self) -> dict:
        """Verifie la contrainte de cisaillement."""
        return verifier_cisaillement(self)


    @staticmethod
    def calculer_section_reelle(compositions: list[tuple[int, float]]) -> float:
        """Calcule la section d'acier reelle à partir des choix de barres."""
        section = 0.0
        for c in compositions:
            nb_barres, phi = c
            section += nb_barres * SECTIONS_HA[phi] / CM2_TO_MM2
        return round(section, 2)


    def diametre_possible_arm_trans(self, phi_l_min_mm: float) -> list[int]:
        """Retourne les diametres transversaux admissibles pour la poutre."""
        diam_max = min(
            self.h_cm * CM_TO_MM / 35, phi_l_min_mm, self.b_cm * CM_TO_MM / 10
        )
        return [x for x in DIAMETRES if x <= diam_max]


    def calculer_ferraillage_transversale(self, nb_brin: int, phi_t: int, ) -> dict:
        """Retourne l'armature transversale et sa disposition'"""
        return calculer_ferraillage_transversale(self, nb_brin, phi_t)
    

    def verifier_fleche(self) -> bool:
        """Verifie la contrainte de fleche."""
        return verifier_fleche(self)


    def sollicitations(self, G_kN_m: float, Q_kN_m: float):
        eff_interne = sollicitations(G_kN_m, Q_kN_m, self.l_m)
        self.M_u_kNm = eff_interne["M_u"]
        self.M_ser_kNm = eff_interne["M_ser"]
        self.V_u_kN = eff_interne["V_u"]
        return eff_interne