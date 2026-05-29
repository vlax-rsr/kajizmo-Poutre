"""
Contrôleur principal optimisé pour Kajizmo.
Orchestration claire des différentes couches.
"""

import logging
from PySide6.QtWidgets import QLineEdit, QComboBox, QSpinBox, QLabel, QTextBrowser
from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.views.main_view import MainView
from src.views.console_view import qtext_long, qtext_trans, qtext_fleche
from src.controllers.status_manager import StatusBarManager, CalculStatus
from src.controllers.input_validators import InputValidator
from src.controllers.calculation_coordinator import CalculationCoordinator
from src.controllers.ui_helpers import UIUpdater, WidgetNames
from src.utils import safe_float

logger = logging.getLogger(__name__)


class MainController:
    """
    Orchestrateur principal - gère les workflows utilisateur.
    
    Responsabilités:
    - Orchestration des workflows (validation -> calcul -> UI)
    - Gestion des signaux/slots
    - Coordination entre Vue et Métier
    """
    
    def __init__(self):
        """Initialise le contrôleur avec ses dépendances."""
        logger.info("Initialisation du MainController")
        
        self.view = MainView()
        self.ui = self.view.ui
        self.status_manager = StatusBarManager(self.ui.statusbar)
        self.calc_coordinator = CalculationCoordinator()
        
        self.status_manager.set_status(CalculStatus.IDLE)
        
        # Caches des widgets pour accès rapide
        self._init_widget_cache()
        self._connect_signals()
        
        logger.info("MainController initialisé avec succès")
    
    # ==================== INITIALISATION ====================
    
    def _init_widget_cache(self):
        """Cache les références aux widgets importants."""
        logger.debug("Initialisation du cache de widgets")
        
        # Entrées géométrie et sollicitations
        self.input_widgets = {
            'b': self.ui.findChild(QLineEdit, WidgetNames.E_B),
            'h': self.ui.findChild(QLineEdit, WidgetNames.E_H),
            'L': self.ui.findChild(QLineEdit, WidgetNames.E_L),
            'Mu': self.ui.findChild(QLineEdit, WidgetNames.E_MU),
            'Mser': self.ui.findChild(QLineEdit, WidgetNames.E_MSER),
            'Vu': self.ui.findChild(QLineEdit, WidgetNames.E_VU),
        }
        
        # Combobox (matériaux et armatures)
        self.combo_widgets = {
            'fc28': self.ui.findChild(QComboBox, WidgetNames.CB_FC28),
            'fe': self.ui.findChild(QComboBox, WidgetNames.CB_FE),
            'fis': self.ui.findChild(QComboBox, WidgetNames.CB_FIS),
            'phi_1': self.ui.findChild(QComboBox, WidgetNames.CB_PHI_1),
            'phi_2': self.ui.findChild(QComboBox, WidgetNames.CB_PHI_2),
            'phi_3': self.ui.findChild(QComboBox, WidgetNames.CB_PHI_3),
            'phi_4': self.ui.findChild(QComboBox, WidgetNames.CB_PHI_4),
        }
        
        # Spinbox (nombre de barres)
        self.spin_widgets = {
            'nb_1': self.ui.findChild(QSpinBox, WidgetNames.SPIN_NB_1),
            'nb_2': self.ui.findChild(QSpinBox, WidgetNames.SPIN_NB_2),
            'nb_3': self.ui.findChild(QSpinBox, WidgetNames.SPIN_NB_3),
            'nb_4': self.ui.findChild(QSpinBox, WidgetNames.SPIN_NB_4),
        }
        
        # Labels de résultat
        self.result_labels = {
            'sec': self.ui.findChild(QLabel, WidgetNames.LBL_SEC),
            'cis': self.ui.findChild(QLabel, WidgetNames.LBL_CIS),
            'areel': self.ui.findChild(QLabel, WidgetNames.LBL_AREEL),
            'valid': self.ui.findChild(QLabel, WidgetNames.LBL_VALID),
            'f': self.ui.findChild(QLabel, WidgetNames.LBL_F),
        }
        
        # Text browsers pour affichage résultats
        self.text_browsers = {
            'long': self.ui.findChild(QTextBrowser, WidgetNames.TB_RESULTAT),
            'trans': self.ui.findChild(QTextBrowser, WidgetNames.TB_RESULTAT_2),
        }
        
        logger.debug("Cache de widgets initialisé")
    
    def _connect_signals(self):
        """Connecte tous les signaux aux slots."""
        logger.debug("Connexion des signaux")
        
        # Boutons principaux
        if self.ui.b_armLong:
            self.ui.b_armLong.clicked.connect(self.calculer_section_theorique)
        if self.ui.b_armTrans:
            self.ui.b_armTrans.clicked.connect(self.calculer_armature_transversale)
        if self.ui.b_export:
            self.ui.b_export.clicked.connect(self.action_export_txt)
        if self.ui.b_reset:
            self.ui.b_reset.clicked.connect(self._reset)
        
        # Suivi des modifications
        for widget in self.input_widgets.values():
            if widget:
                widget.textChanged.connect(lambda t, w=widget: self._on_input_after_warning(w))
                widget.textChanged.connect(lambda t, w=widget: self._on_input_changed(w))
        
        for entry_widget in [self.combo_widgets['fc28'], self.combo_widgets['fe'], self.combo_widgets['fis']]:
            if entry_widget:
                entry_widget.currentTextChanged.connect(lambda t, w=entry_widget: self._on_input_after_warning(w))
                entry_widget.currentTextChanged.connect(lambda t, w=entry_widget: self._on_input_changed(w))
        
        # Recalcul instantané de la section réelle
        for nb_widget in [self.spin_widgets['nb_1'], self.spin_widgets['nb_2'], self.spin_widgets['nb_3']]:
            if nb_widget:
                nb_widget.valueChanged.connect(self._mettre_a_jour_section_reelle)
        
        for phi_widget in [self.combo_widgets['phi_1'], self.combo_widgets['phi_2'], self.combo_widgets['phi_3']]:
            if phi_widget:
                phi_widget.currentTextChanged.connect(self._mettre_a_jour_section_reelle)
        
        logger.debug("Signaux connectés")
    
    # ==================== CALLBACKS SIGNAUX ====================
    
    def _on_input_changed(self, widget):
        """Appelé quand une entrée change."""
        if self.calc_coordinator.poutre_actuelle is None:
            return
        
        # Ignorer les champs vides
        if isinstance(widget, QLineEdit) and not widget.text().strip():
            return
        
        if isinstance(widget, QComboBox) and not widget.currentText().strip():
            return
        
        UIUpdater.apply_warning_style(widget)
        self.status_manager.set_status(
            CalculStatus.WARNING,
            "Valeurs modifiées - recalculez",
            duration_ms=5000
        )

        logger.debug(f"Input modifié: {widget.objectName()}")

    def _on_input_after_warning(self, widget):
        if widget:
            UIUpdater.reset_after_warning(widget)

    # ==================== CALCUL LONGITUDINAL ====================
    
    def calculer_section_theorique(self):
        """Calcule la section d'armature longitudinale théorique."""
        logger.info("=" * 70)
        logger.info("Début du calcul section théorique")
        logger.info("=" * 70)
        
        try:
            # Étape 1: Valider les entrées
            self.status_manager.set_status(CalculStatus.CALCULATING)
            UIUpdater.reset_all_input_styles(list(self.input_widgets.values()))
            UIUpdater.reset_all_input_styles(list(self.combo_widgets.values()))
            logger.debug("Validation des entrées en cours...")
            
            b = safe_float(self.input_widgets['b'].text() if self.input_widgets['b'] else "0")
            h = safe_float(self.input_widgets['h'].text() if self.input_widgets['h'] else "0")
            l = safe_float(self.input_widgets['L'].text() if self.input_widgets['L'] else "0")
            mu = safe_float(self.input_widgets['Mu'].text() if self.input_widgets['Mu'] else "0")
            mser = safe_float(self.input_widgets['Mser'].text() if self.input_widgets['Mser'] else "0")
            vu = safe_float(self.input_widgets['Vu'].text() if self.input_widgets['Vu'] else "0")
            
            is_valid, errors = InputValidator.valider_toutes_entrees(
                str(b), str(h), str(l), str(mu), str(mser), str(vu)
            )
            
            if not is_valid:
                logger.warning(f"Validation échouée: {len(errors)} erreur(s)")
                self._handle_validation_errors(errors)
                return
            
            logger.info(f"✓ Validation réussie: b={b} cm, h={h} cm, L={l} m, Mu={mu} kN.m, Mser={mser} kN.m, Vu={vu} kN")
            
            # Étape 2: Construire la poutre
            logger.debug("Construction de la poutre...")
            fc28 = safe_float(self.combo_widgets['fc28'].currentText(), 25)
            fe = safe_float(self.combo_widgets['fe'].currentText(), 500)
            fis = self.combo_widgets['fis'].currentText()
            
            poutre = self.calc_coordinator.construire_poutre(
                b, h, l, fc28, fe, fis, mu, mser, vu
            )
            
            if not poutre:
                logger.error("Impossible de créer la poutre")
                self.status_manager.set_status(CalculStatus.ERROR, "Erreur création poutre")
                return
            
            # Étape 3: Calculer ferraillage longitudinal
            logger.debug("Calcul du ferraillage longitudinal...")
            arm_long = self.calc_coordinator.calculer_ferraillage_longitudinal()
            A_t_final = arm_long.get("A_t_final_cm2", 0.0)
            
            # Étape 4: Vérifier cisaillement
            logger.debug("Vérification du cisaillement...")
            cis = self.calc_coordinator.verifier_cisaillement()
            
            # Étape 5: Vérifier flèche
            logger.debug("Vérification de la flèche...")
            fleche = self.calc_coordinator.verifier_fleche()
            
            # Étape 6: Mettre à jour l'interface
            logger.debug("Mise à jour de l'interface...")
            self._update_longitudinal_results(arm_long, cis, fleche, A_t_final)
            
            # Étape 7: Mettre à jour les diamètres transversaux si composition saisie
            self._mettre_a_jour_section_reelle()
            
            # ✓ Succès
            self.status_manager.set_status(
                CalculStatus.SUCCESS,
                f"Aₜ = {A_t_final:.2f} cm²",
                duration_ms=3000
            )
            
            logger.info(f"✓ Calcul réussi: Aₜ = {A_t_final:.2f} cm²")
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"✗ Erreur calcul section théorique: {e}", exc_info=True)
            self.status_manager.set_status(CalculStatus.ERROR, str(e))
            self.view.show_error(
                "Erreur de calcul",
                "Le calcul longitudinal a échoué",
                str(e)
            )
    
    def _handle_validation_errors(self, errors: list):
        """Gère les erreurs de validation."""
        logger.warning(f"Erreurs de validation: {errors}")
        
        # Appliquer les styles d'erreur aux champs concernés
        for error_msg in errors:
            if "largeur" in error_msg.lower():
                UIUpdater.apply_error_style(self.input_widgets['b'])
            elif "hauteur" in error_msg.lower():
                UIUpdater.apply_error_style(self.input_widgets['h'])
            elif "portée" in error_msg.lower():
                UIUpdater.apply_error_style(self.input_widgets['L'])
            elif "Mu" in error_msg:
                UIUpdater.apply_error_style(self.input_widgets['Mu'])
            elif "Mser" in error_msg:
                UIUpdater.apply_error_style(self.input_widgets['Mser'])
            elif "Vu" in error_msg:
                UIUpdater.apply_error_style(self.input_widgets['Vu'])
        
        self.status_manager.set_status(
            CalculStatus.ERROR,
            f"{len(errors)} erreur(s)",
            duration_ms=5000
        )
        self.view.show_error(
            "Erreur de saisie",
            "Données invalides",
            "• " + "\n• ".join(errors)
        )
    
    def _update_longitudinal_results(self, arm_long, cis, fleche, A_t_final):
        """Met à jour les résultats du ferraillage longitudinal."""
        logger.debug("Mise à jour des résultats longitudinaux...")
        
        # Section théorique
        UIUpdater.update_result_label(
            self.result_labels['sec'],
            A_t_final,
            arm_long.get("condition", False),
            unit="cm²"
        )
        
        # Cisaillement
        UIUpdater.update_check_icon(
            self.result_labels['cis'],
            cis.get("condition", False),
            self.view.pixmap_valide,
            self.view.pixmap_erreur
        )
        
        # Flèche
        UIUpdater.update_check_icon(
            self.result_labels['f'],
            fleche.get("condition", False),
            self.view.pixmap_valide,
            self.view.pixmap_erreur
        )
        
        # Afficher les résultats en texte
        qtext_long(self.calc_coordinator.poutre_actuelle, self.text_browsers['long'])
        
        logger.debug("✓ Résultats longitudinaux mis à jour")
    
    # ==================== SECTION RÉELLE ====================
    
    def _mettre_a_jour_section_reelle(self):
        """Met à jour la section réelle d'armature longitudinale."""
        try:
            if not self.calc_coordinator.poutre_actuelle:
                return
            
            logger.debug("Mise à jour de la section réelle...")
            
            # Récupérer les compositions
            nb1 = int(self.spin_widgets['nb_1'].value() or 0)
            nb2 = int(self.spin_widgets['nb_2'].value() or 0)
            nb3 = int(self.spin_widgets['nb_3'].value() or 0)
            
            if nb1 == 0 and nb2 == 0 and nb3 == 0:
                if self.result_labels['areel']:
                    self.result_labels['areel'].setText("Non calculée")
                if self.result_labels['valid']:
                    self.result_labels['valid'].hide()
                logger.debug("Mise à jour inutile.")
                return

            compositions = [
                (int(self.spin_widgets['nb_1'].value() or 0), safe_float(self.combo_widgets['phi_1'].currentText() or "0")),
                (int(self.spin_widgets['nb_2'].value() or 0), safe_float(self.combo_widgets['phi_2'].currentText() or "0")),
                (int(self.spin_widgets['nb_3'].value() or 0), safe_float(self.combo_widgets['phi_3'].currentText() or "0")),
            ]
            

            # Mettre à jour via le coordinateur
            a_reel = self.calc_coordinator.mettre_a_jour_compositions(compositions)
            
            # Mettre à jour diamètres transversaux
            diametres = self.calc_coordinator.get_diametres_arm_trans()
            UIUpdater.update_diametres_combo(self.combo_widgets['phi_4'], diametres)
            
            # Vérifier si ça respecte le minimum
            if self.calc_coordinator.A_t_final_cm2 > 0:
                is_valid = a_reel >= self.calc_coordinator.A_t_final_cm2
                UIUpdater.update_result_label(
                    self.result_labels['areel'],
                    a_reel,
                    is_valid,
                    unit="cm²"
                )
                
                if self.result_labels['valid']:
                    UIUpdater.update_check_icon(
                        self.result_labels['valid'],
                        is_valid,
                        self.view.pixmap_valide,
                        self.view.pixmap_erreur
                    )
                    self.result_labels['valid'].show()
                
                logger.debug(f"✓ Section réelle MAJ: {a_reel:.2f} cm² ({is_valid})")
            else:
                if self.result_labels['areel']:
                    self.result_labels['areel'].setText("Non calculée")
                if self.result_labels['valid']:
                    self.result_labels['valid'].hide()
        
        except Exception as e:
            logger.error(f"Erreur MAJ section réelle: {e}", exc_info=True)
            self.status_manager.set_status(CalculStatus.ERROR, "Erreur section réelle")
    
    # ==================== CALCUL TRANSVERSAL ====================
    
    def calculer_armature_transversale(self):
        """Calcule l'armature transversale."""
        logger.info("=" * 70)
        logger.info("Début du calcul armature transversale")
        logger.info("=" * 70)
        
        if not self.calc_coordinator.poutre_actuelle:
            logger.warning("Tentative de calcul transversal sans poutre calculée")
            self.status_manager.set_status(
                CalculStatus.ERROR,
                "Calculez d'abord l'armature longitudinale",
                duration_ms=4000
            )
            return
        
        try:
            self.status_manager.set_status(CalculStatus.CALCULATING)
            
            # Réinitialiser les styles d'erreur
            UIUpdater.reset_style(self.spin_widgets['nb_4'])
            UIUpdater.reset_style(self.combo_widgets['phi_4'])
            
            # Valider les entrées transversales
            logger.debug("Validation des entrées transversales...")
            nb_brin = int(self.spin_widgets['nb_4'].value() or 0)
            is_valid, msg = InputValidator.valider_nb_brins(nb_brin)
            if not is_valid:
                logger.warning(f"Validation nb_brins échouée: {msg}")
                UIUpdater.apply_error_style(self.spin_widgets['nb_4'])
                self.status_manager.set_status(CalculStatus.ERROR, msg, duration_ms=3000)
                return
            
            phi_t_text = self.combo_widgets['phi_4'].currentText()
            is_valid, msg = InputValidator.valider_diametre(phi_t_text)
            if not is_valid:
                logger.warning(f"Validation diamètre échouée: {msg}")
                UIUpdater.apply_error_style(self.combo_widgets['phi_4'])
                self.status_manager.set_status(CalculStatus.ERROR, msg, duration_ms=3000)
                return
            
            phi_t = int(safe_float(phi_t_text))
            logger.info(f"✓ Validation réussie: nb_brin={nb_brin}, phi_t={phi_t}")
            
            # Calculer ferraillage transversal
            logger.debug("Calcul du ferraillage transversal...")
            result = self.calc_coordinator.calculer_ferraillage_transversale(nb_brin, phi_t)
            
            # Afficher résultats
            qtext_trans(
                self.calc_coordinator.poutre_actuelle,
                self.text_browsers['trans'],
                nb_brin,
                phi_t
            )
            
            self.status_manager.set_status(
                CalculStatus.SUCCESS,
                f"Calcul transversal réussi | Sₜ = {result.get('st', 0):.2f} cm",
                duration_ms=3000
            )
            logger.info(f"✓ Calcul réussi: St₀={result.get('st0', 0):.1f} cm, Sₜ={result.get('st', 0):.1f} cm")
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"✗ Erreur calcul transversal: {e}", exc_info=True)
            self.status_manager.set_status(CalculStatus.ERROR, str(e))
    
    # ==================== BOUTON EXPORT ====================

    def action_export_txt(self):
        """Méthode de slot liée au bouton d'export dans le contrôleur."""
        # Sécurité : récupération du vrai widget QMainWindow/QWidget de l'interface
        parent_widget = None
        if hasattr(self, 'view') and hasattr(self.view, 'ui'):
            parent_widget = self.view.ui
        elif hasattr(self, 'ui'):
            parent_widget = self.ui

        # 1. Ouvrir l'explorateur natif pour choisir l'emplacement du fichier
        chemin, _ = QFileDialog.getSaveFileName(
            parent_widget,                     
            "Enregistrer le rapport technique",
            "Note_de_calcul_poutre_BAEL.txt",
            "Fichiers Texte (*.txt)"
        )
        
        # Si l'utilisateur clique sur "Annuler" ou ferme la fenêtre
        if not chemin:
            logger.info("Export TXT annulé par l'utilisateur.")
            return
            
        try:
            # 2. Récupération dynamique des paramètres transversaux actuels
            phi_t = 0
            nb_brins = 0
            
            # Récupération sécurisée du diamètre transversal (ex: cb_phi_4 ou phi_4 dans vos caches)
            combo_phi = self.combo_widgets.get('phi_4') or self.combo_widgets.get('cb_phi_4')
            if combo_phi:
                try:
                    phi_t = int(combo_phi.currentText())
                except ValueError:
                    phi_t = 0
                    
            # Récupération sécurisée du nombre de brins (ex: spin_nb_4 ou nb_4)
            spin_nb = self.spin_widgets.get('nb_4') or self.spin_widgets.get('spin_nb_4')
            if spin_nb:
                nb_brins = spin_nb.value()

            # 3. Exécution du traitement de génération de fichier via le Coordinateur
            self.calc_coordinator.export_txt(
                chemin_fichier=chemin,
                phi_t=phi_t,
                nb_brins=nb_brins
            )
            
            # 4. Message visuel de succès pour l'utilisateur
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                parent_widget, 
                "Export Réussi", 
                "La note de calcul technique BAEL a été enregistrée avec succès !"
            )
            self.status_manager.set_status(CalculStatus.SUCCESS, "Export TXT réussi")
            
        except Exception as e:
            logger.error(f"Échec de l'action d'exportation TXT : {e}", exc_info=True)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                parent_widget, 
                "Erreur d'Export", 
                f"Impossible d'exporter la note de calcul :\n{str(e)}"
            )
            self.status_manager.set_status(CalculStatus.ERROR, "Échec de l'export")

    # ==================== RÉINITIALISATION ====================
    
    def _reset(self):
        """Réinitialise tous les calculs et l'interface."""
        logger.info("=" * 70)
        logger.info("Réinitialisation complète de l'application")
        logger.info("=" * 70)
        
        # 1. Réinitialiser l'état métier
        self.calc_coordinator.reinitialiser()
        
        # 2. Réinitialiser les labels de résultat
        UIUpdater.reset_all_result_labels(self.result_labels)
        
        # 3. Vider les text browsers
        UIUpdater.clear_text_browsers(list(self.text_browsers.values()))
        
        # 4. Réinitialiser les spinbox
        for spin in self.spin_widgets.values():
            if spin:
                spin.setValue(0)
        
        # 5. Réinitialiser les combo à défaut
        if self.combo_widgets['fc28']:
            self.combo_widgets['fc28'].setCurrentIndex(1)
        if self.combo_widgets['fe']:
            self.combo_widgets['fe'].setCurrentIndex(1)
        if self.combo_widgets['fis']:
            self.combo_widgets['fis'].setCurrentIndex(0)
        
        for phi_key in ['phi_1', 'phi_2', 'phi_3']:
            if self.combo_widgets[phi_key]:
                self.combo_widgets[phi_key].setCurrentIndex(1)
        
        # 6. Réinitialiser les styles
        UIUpdater.reset_all_input_styles(list(self.input_widgets.values()))
        UIUpdater.reset_all_input_styles(list(self.combo_widgets.values()))
        
        # 7. Update status
        self.status_manager.set_status(CalculStatus.IDLE, "Réinitialisé", duration_ms=2000)
        
        logger.info("✓ Réinitialisation complète")
        logger.info("=" * 70)
    
    # ==================== AFFICHAGE ====================
    
    def show(self):
        """Affiche la fenêtre principale."""
        if self.ui:
            self.ui.show()
            logger.info("Fenêtre principale affichée")
