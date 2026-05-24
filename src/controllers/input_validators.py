"""
Module de validation pour Kajizmo.
Gère la validation robuste des entrées utilisateur.
"""

import logging
from typing import Optional, Tuple, List
from src.utils import safe_float

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception levée lors d'une validation échouée."""
    pass


class InputValidator:
    """Validateur centralisé pour les entrées utilisateur."""
    
    # Constantes de validation
    MIN_B, MAX_B = 10, 200
    MIN_H, MAX_H = 20, 300
    MIN_L, MAX_L = 1, 50
    MIN_M, MAX_M = 0.1, 10000
    MIN_V, MAX_V = 0.1, 5000
    
    @staticmethod
    def valider_b(value: float) -> Tuple[bool, str]:
        """Valide la largeur."""
        if value <= 0:
            return False, "La largeur b doit être supérieure à 0 cm"
        if not (InputValidator.MIN_B <= value <= InputValidator.MAX_B):
            return False, f"b doit être entre {InputValidator.MIN_B} et {InputValidator.MAX_B} cm"
        return True, ""
    
    @staticmethod
    def valider_h(value: float) -> Tuple[bool, str]:
        """Valide la hauteur."""
        if value <= 0:
            return False, "La hauteur h doit être supérieure à 0 cm"
        if not (InputValidator.MIN_H <= value <= InputValidator.MAX_H):
            return False, f"h doit être entre {InputValidator.MIN_H} et {InputValidator.MAX_H} cm"
        return True, ""
    
    @staticmethod
    def valider_l(value: float) -> Tuple[bool, str]:
        """Valide la portée."""
        if value <= 0:
            return False, "La portée L doit être supérieure à 0 m"
        if not (InputValidator.MIN_L <= value <= InputValidator.MAX_L):
            return False, f"L doit être entre {InputValidator.MIN_L} et {InputValidator.MAX_L} m"
        return True, ""
    
    @staticmethod
    def valider_moment(label: str, value: float) -> Tuple[bool, str]:
        """Valide un moment."""
        if value <= 0:
            return False, f"Le moment {label} doit être supérieur à 0"
        if not (InputValidator.MIN_M <= value <= InputValidator.MAX_M):
            return False, f"{label} doit être entre {InputValidator.MIN_M} et {InputValidator.MAX_M} kN.m"
        return True, ""
    
    @staticmethod
    def valider_effort_tranchant(value: float) -> Tuple[bool, str]:
        """Valide l'effort tranchant."""
        if value <= 0:
            return False, "L'effort tranchant Vu doit être supérieur à 0"
        if not (InputValidator.MIN_V <= value <= InputValidator.MAX_V):
            return False, f"Vu doit être entre {InputValidator.MIN_V} et {InputValidator.MAX_V} kN"
        return True, ""
    
    @staticmethod
    def valider_nb_brins(value: int) -> Tuple[bool, str]:
        """Valide le nombre de brins."""
        if value <= 0:
            return False, "Le nombre de brins doit être supérieur à 0"
        if value > 12:  # Limite raisonnable
            return False, "Le nombre de brins doit être ≤ 12"
        return True, ""
    
    @staticmethod
    def valider_diametre(value: str) -> Tuple[bool, str]:
        """Valide la sélection d'un diamètre."""
        if not value or value.strip() == "":
            return False, "Sélectionnez un diamètre"
        try:
            phi = int(value)
            if phi <= 0:
                return False, "Diamètre invalide"
            return True, ""
        except ValueError:
            return False, "Diamètre invalide"
    
    @staticmethod
    def valider_toutes_entrees(
        b_text: str, h_text: str, l_text: str,
        mu_text: str, mser_text: str, vu_text: str
    ) -> Tuple[bool, List[str]]:
        """Valide tous les champs de géométrie et sollicitations."""
        errors = []
        
        # Géométrie
        b = safe_float(b_text, -1)
        if b <= 0:
            errors.append("La largeur b doit être supérieure à 0 cm")
        else:
            is_valid, msg = InputValidator.valider_b(b)
            if not is_valid:
                errors.append(msg)
        
        h = safe_float(h_text, -1)
        if h <= 0:
            errors.append("La hauteur h doit être supérieure à 0 cm")
        else:
            is_valid, msg = InputValidator.valider_h(h)
            if not is_valid:
                errors.append(msg)
        
        l = safe_float(l_text, -1)
        if l <= 0:
            errors.append("La portée L doit être supérieure à 0 m")
        else:
            is_valid, msg = InputValidator.valider_l(l)
            if not is_valid:
                errors.append(msg)
        
        # Sollicitations
        mu = safe_float(mu_text, -1)
        is_valid, msg = InputValidator.valider_moment("Mu (ELU)", mu)
        if not is_valid:
            errors.append(msg)
        
        mser = safe_float(mser_text, -1)
        is_valid, msg = InputValidator.valider_moment("Mser (ELS)", mser)
        if not is_valid:
            errors.append(msg)
        
        vu = safe_float(vu_text, -1)
        is_valid, msg = InputValidator.valider_effort_tranchant(vu)
        if not is_valid:
            errors.append(msg)
        
        return len(errors) == 0, errors
