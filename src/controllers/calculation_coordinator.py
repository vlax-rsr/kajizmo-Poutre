"""
Coordinateur des calculs BAEL.
Gère l'orchestration des calculs du moteur.
"""

import logging
from typing import Optional, Dict, Any
from src.models.engine import Poutre
from src.models.exceptions import BaelError, SectionDepasseeError
from src.utils import safe_float
from src.models.formatting import *


logger = logging.getLogger(__name__)


class CalculationCoordinator:
    """Coordonne tous les calculs du moteur BAEL."""
    
    def __init__(self):
        self.poutre_actuelle: Optional[Poutre] = None
        self.A_t_final_cm2: float = 0.0
        self.phi_l_min_mm: Optional[float] = None
        self.compositions: list = []
    
    def construire_poutre(
        self, b_cm: float, h_cm: float, l_m: float,
        fc28_MPa: float, fe_MPa: float, fis: str,
        M_u_kNm: float, M_ser_kNm: float, V_u_kN: float
    ) -> Optional[Poutre]:
        """
        Construit une poutre à partir des paramètres.
        
        Args:
            b_cm: Largeur en cm
            h_cm: Hauteur en cm
            l_m: Longueur en m
            fc28_MPa: Résistance béton en MPa
            fe_MPa: Limite élastique acier en MPa
            fis: Classe de fissuration
            M_u_kNm: Moment ELU en kN.m
            M_ser_kNm: Moment ELS en kN.m
            V_u_kN: Effort tranchant ELU en kN
        
        Returns:
            Poutre instance ou None en cas d'erreur
        """
        try:
            self.poutre_actuelle = Poutre(
                b_cm=b_cm, h_cm=h_cm, l_m=l_m,
                fc28_MPa=fc28_MPa, fe_MPa=fe_MPa, fis=fis,
                M_u_kNm=M_u_kNm, M_ser_kNm=M_ser_kNm, V_u_kN=V_u_kN
            )
            logger.info(f"Poutre créée: {b_cm} x {h_cm}, L={l_m} m, fc28={fc28_MPa} MPa")
            return self.poutre_actuelle
        except Exception as e:
            logger.error(f"Erreur création poutre: {e}", exc_info=True)
            return None
    
    def calculer_ferraillage_longitudinal(self) -> Dict[str, Any]:
        """Calcule le ferraillage longitudinal."""
        if not self.poutre_actuelle:
            raise ValueError("Aucune poutre calculée")
        
        try:
            result = self.poutre_actuelle.calculer_ferraillage_longitudinal()
            self.A_t_final_cm2 = result.get("A_t_final_cm2", 0.0)
            logger.info(f"Ferraillage longitudinal calculé: A_t = {self.A_t_final_cm2:.2f} cm²")
            return result
        except SectionDepasseeError as e:
            logger.error(f"Section dépassée: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur calcul ferraillage longitudinal: {e}", exc_info=True)
            raise
    
    def verifier_cisaillement(self) -> Dict[str, Any]:
        """
        Vérifie le cisaillement.
        
        Returns:
            Dict avec résultats de vérification
        """
        if not self.poutre_actuelle:
            raise ValueError("Aucune poutre calculée")
        
        try:
            result = self.poutre_actuelle.verifier_cisaillement()
            condition_str = "✓ OK" if result["condition"] else "✗ ERREUR"
            logger.info(f"Cisaillement: {result['tau_u_MPa']:.2f}/{result['tau_lim_MPa']:.2f} MPa - {condition_str}")
            return result
        except Exception as e:
            logger.error(f"Erreur vérification cisaillement: {e}", exc_info=True)
            raise
    
    def verifier_fleche(self) -> Dict[str, Any]:
        """
        Vérifie la flèche.
        
        Returns:
            Dict avec résultats de vérification
        """
        if not self.poutre_actuelle:
            raise ValueError("Aucune poutre calculée")
        
        try:
            result = self.poutre_actuelle.verifier_fleche()
            condition_str = "✓ OK" if result["condition"] else "✗ ERREUR"
            logger.info(f"Flèche: {result['f_cm']:.2f}/{result['f_lim_cm']:.2f} cm - {condition_str}")
            return result
        except Exception as e:
            logger.error(f"Erreur vérification flèche: {e}", exc_info=True)
            raise
    
    def mettre_a_jour_compositions(self, compositions: list) -> float:
        """
        Met à jour les compositions d'armature et retourne la section réelle.
        
        Args:
            compositions: Liste de tuples (nombre, diamètre)
        
        Returns:
            Section réelle en cm²
        """
        self.compositions = [
            (nb, phi) for nb, phi in compositions 
            if nb > 0 and phi > 0
        ]
        
        phis_utilises = [phi for nb, phi in self.compositions if nb > 0 and phi > 0]
        self.phi_l_min_mm = min(phis_utilises) if phis_utilises else None
        
        if self.poutre_actuelle and self.phi_l_min_mm:
            logger.debug(f"Compositions MAJ: phi_min = {self.phi_l_min_mm} mm")
        
        section_reelle = Poutre.calculer_section_reelle(self.compositions)
        logger.debug(f"Section réelle calculée: {section_reelle:.2f} cm²")
        return section_reelle
    
    def calculer_ferraillage_transversale(
        self, nb_brin: int, phi_t: int
    ) -> Dict[str, Any]:
        """
        Calcule le ferraillage transversal.
        
        Args:
            nb_brin: Nombre de brins
            phi_t: Diamètre des cadres en mm
        
        Returns:
            Dict avec résultats du calcul
        """
        if not self.poutre_actuelle:
            raise ValueError("Aucune poutre calculée")
        
        try:
            result = self.poutre_actuelle.calculer_ferraillage_transversale(
                nb_brin=nb_brin, phi_t=phi_t
            )
            logger.info(f"Ferraillage transversal calculé: St₀={result.get('st0', 0):.1f} cm, St={result.get('st', 0):.1f} cm")
            return result
        except Exception as e:
            logger.error(f"Erreur calcul ferraillage transversal: {e}", exc_info=True)
            raise
    
    def get_diametres_arm_trans(self) -> list:
        """Retourne les diamètres admissibles pour les armatures transversales."""
        if not self.poutre_actuelle or not self.phi_l_min_mm:
            logger.debug("Pas de diamètres transversaux disponibles (poutre non calculée)")
            return []
        
        try:
            diametres = self.poutre_actuelle.diametre_possible_arm_trans(self.phi_l_min_mm)
            logger.debug(f"Diamètres arm transv admis: {diametres}")
            return diametres
        except Exception as e:
            logger.error(f"Erreur détermination diamètres transversaux: {e}", exc_info=True)
            return []
        
    def export_txt(self, chemin_fichier: str, phi_t: int = 0, nb_brins: int = 0) -> bool:
        """Génère un rapport technique complet au format TXT et l'enregistre sur le disque."""
        if not self.poutre_actuelle:
            logger.error("Export impossible : aucune poutre n'a été calculée.")
            raise ValueError("Aucune poutre n'est disponible pour l'export.")

        logger.info(f"Début de la génération de l'export TXT vers : {chemin_fichier}")
        
        try:
            lignes_rapport = []

            lignes_rapport.extend(afficher_resume(self.poutre_actuelle))
            lignes_rapport.extend(afficher_result_long(self.poutre_actuelle))
            
            if self.compositions:
                lignes_rapport.extend(afficher_choix(self.poutre_actuelle, self.compositions))
            
            if phi_t > 0 and nb_brins > 0:
                lignes_rapport.extend(afficher_result_trans(self.poutre_actuelle, phi_t, nb_brins))
                lignes_rapport.append(afficher_repartition_arm_trans(self.poutre_actuelle, nb_brins, phi_t))
            
            lignes_rapport.extend(afficher_result_fleche(self.poutre_actuelle))
            
            with open(chemin_fichier, "w", encoding="utf-8") as fichier:
                fichier.write("\n".join(lignes_rapport))
                
            logger.info(f"✓ Rapport technique exporté avec succès ({len(lignes_rapport)} lignes écrites).")
            return True
            
        except IOError as e:
            logger.error(f"Erreur d'écriture disque lors de l'export TXT : {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la génération de l'export : {e}", exc_info=True)
            raise
    
    def reinitialiser(self):
        """Réinitialise l'état du coordinateur."""
        self.poutre_actuelle = None
        self.A_t_final_cm2 = 0.0
        self.phi_l_min_mm = None
        self.compositions = []
        logger.info("Coordinateur réinitialisé")
