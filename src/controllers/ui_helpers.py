"""
Helpers pour la mise à jour de l'interface graphique.
Centralise la logique UI pour éviter la duplication.
"""

import logging
from typing import Optional, List
from PySide6.QtWidgets import QLineEdit, QComboBox, QSpinBox, QLabel, QTextBrowser
from PySide6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class WidgetNames:
    """Constantes pour les noms des widgets - évite les magic strings."""
    # Entrées géométrie
    E_B = "e_b"
    E_H = "e_h"
    E_L = "e_L"
    
    # Entrées sollicitations
    E_MU = "e_Mu"
    E_MSER = "e_Mser"
    E_VU = "e_Vu"
    
    # Matériaux (combobox)
    CB_FC28 = "cb_fc28"
    CB_FE = "cb_fe"
    CB_FIS = "cb_fis"
    
    # Armatures longitudinales
    CB_PHI_1 = "cb_phi_1"
    CB_PHI_2 = "cb_phi_2"
    CB_PHI_3 = "cb_phi_3"
    SPIN_NB_1 = "spin_nb_1"
    SPIN_NB_2 = "spin_nb_2"
    SPIN_NB_3 = "spin_nb_3"
    
    # Armatures transversales
    CB_PHI_4 = "cb_phi_4"
    SPIN_NB_4 = "spin_nb_4"
    
    # Labels résultats longitudinal
    LBL_SEC = "lbl_sec"
    LBL_CIS = "lbl_cis"
    LBL_AREEL = "lbl_areel"
    LBL_VALID = "lbl_valid"
    LBL_F = "lbl_f"
    
    # Text browsers
    TB_RESULTAT = "tb_resultat"
    TB_RESULTAT_2 = "tb_resultat_2"


class UIUpdater:
    """Gère les mises à jour cohérentes de l'interface."""
    
    @staticmethod
    def reset_style(widget) -> None:
        """Réinitialise le style d'un widget."""
        if widget is None:
            return
        widget.setObjectName("")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
    
    @staticmethod
    def reset_after_warning(widget):
        logger.info(f"Réinitialisation après warning du widget: {widget.objectName()}")
        if widget is None:
            return
            
        nom_actuel = widget.objectName()
        logger.debug(f"ObjectName du widget: {nom_actuel}")
        if nom_actuel != "ErreurEntree":
            logger.info("Réinitialisation du style du widget a échouée")
            return

        nom_origine = ""
        logger.debug(f"ObjectName du widget après modification: {nom_origine}")
        widget.setObjectName(nom_origine)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        logger.info("Style d'erreur/warning nettoyé")


    @staticmethod
    def apply_warning_style(widget) -> None:
        """Applique le style warning (jaune/orange)."""
        if widget is None:
            return
        widget.setObjectName("Warning")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        logger.debug(f"Style warning appliqué à {widget.objectName()}")
    
    @staticmethod
    def apply_error_style(widget) -> None:
        """Applique le style erreur (rouge)."""
        if widget is None:
            return
        widget.setObjectName("ErreurEntree")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        logger.debug(f"Style erreur appliqué à {widget.objectName()}")
    
    @staticmethod
    def update_result_label(
        label: QLabel, 
        value: float, 
        is_valid: bool,
        unit: str = "cm²"
    ) -> None:
        """
        Met à jour un label de résultat avec style approprié.
        
        Args:
            label: Le label à mettre à jour
            value: La valeur à afficher
            is_valid: Si le résultat est valide
            unit: Unité à afficher
        """
        if label is None:
            return
        
        label.setText(f"{value:.2f} {unit}")
        style_name = "ResultatValide" if is_valid else "ResultatErreur"
        label.setObjectName(style_name)
        label.style().unpolish(label)
        label.style().polish(label)
        
        status = "✓ valide" if is_valid else "✗ invalide"
        logger.debug(f"Label {label.objectName()} MAJ: {value:.2f} {unit} ({status})")
    
    @staticmethod
    def update_check_icon(
        label: QLabel, 
        is_valid: bool, 
        pixmap_valide: QPixmap, 
        pixmap_erreur: QPixmap
    ) -> None:
        """
        Met à jour une icône de validation.
        
        Args:
            label: Le label contenant l'icône
            is_valid: Si valide (True = ✓, False = ✗)
            pixmap_valide: Image pour état valide
            pixmap_erreur: Image pour état erreur
        """
        if label is None:
            return
        
        pixmap = pixmap_valide if is_valid else pixmap_erreur
        label.setPixmap(pixmap)
        status = "✓" if is_valid else "✗"
        logger.debug(f"Icône MAJ: {status}")
    
    @staticmethod
    def reset_all_input_styles(widgets: list) -> None:
        """Réinitialise le style de tous les widgets d'entrée."""
        if not widgets:
            return
        
        for widget in widgets:
            if widget:
                UIUpdater.reset_style(widget)
        logger.debug(f"{len([w for w in widgets if w])} widgets d'entrée réinitialisés")

    @staticmethod
    def reset_all_result_labels(labels: dict) -> None:
        """Réinitialise tous les labels de résultat."""
        if not labels:
            return
        
        for label in labels.values():
            if label:
                label.setText("Non calculée")
                UIUpdater.reset_style(label)
        
        logger.debug(f"{len([l for l in labels.values() if l])} labels réinitialisés")
    
    @staticmethod
    def clear_text_browsers(browsers: list) -> None:
        """Vide les text browsers."""
        if not browsers:
            return
        
        for browser in browsers:
            if browser:
                browser.clear()
        
        logger.debug(f"{len([b for b in browsers if b])} text browsers vidés")
    
    @staticmethod
    def disable_transversal_inputs(spin: QSpinBox, combo: QComboBox, enabled: bool) -> None:
        """Active/désactive les contrôles transversaux."""
        if spin:
            spin.setEnabled(enabled)
        if combo:
            combo.setEnabled(enabled)
        
        status = "activés" if enabled else "désactivés"
        logger.debug(f"Contrôles transversaux {status}")
    
    @staticmethod
    def update_diametres_combo(combo: QComboBox, diametres: list) -> None:
        """Met à jour le combo des diamètres."""
        if combo is None:
            return
        
        combo.blockSignals(True)
        combo.clear()
        if diametres:
            combo.addItems([str(d) for d in diametres])
            logger.info(f"Combo diamètres MAJ: {len(diametres)} options disponibles")
        else:
            logger.warning("Aucun diamètre disponible pour le combo")
        combo.blockSignals(False)
