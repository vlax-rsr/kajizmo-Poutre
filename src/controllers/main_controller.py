# src/controllers/main_controller.py
from PySide6.QtWidgets import QLineEdit
from models.engine import Poutre
from models.formatting import *
from views.main_view import MainView
from views.console_view import *
from .status_manager import StatusBarManager, CalculStatus
from src.utils import safe_float

class MainController:
    """Contrôleur principal guidant les flux de données et appels moteurs."""
    def __init__(self):
        self.view = MainView()
        self.ui = self.view.ui  # Garde la compatibilité avec l'extérieur

        self.status_manager = StatusBarManager(self.ui.statusbar)
        self.status_manager.set_status(CalculStatus.IDLE)

        self.A_reelle = 0.0
        self.A_t_final = 0.0
        self.poutre_calcule = None
        self.phi_l_min_mm = None
        self.compositions = []
        self.nb_brin = 0
        self.phi_t = 0

        self._connect_signals()

    def _connect_signals(self):
        v = self.view
        # Actions boutons
        if v.b_armLong:
            v.b_armLong.clicked.connect(self.calculer_section_theorique)
            v.b_armLong.clicked.connect(self.verifier_fleche)
        if v.b_armTrans:
            v.b_armTrans.clicked.connect(self.calculer_armature_transversale)
        if v.b_reset:
            v.b_reset.clicked.connect(self._reset)

        # Suivi dynamique des modifications (Warnings)
        for w in [v.e_b, v.e_h, v.e_Mu, v.e_Mser, v.e_Vu, v.e_L]:
            if w:
                w.textChanged.connect(lambda t, widget=w: v.reset_styles_entrer(widget))
                w.textChanged.connect(lambda t, widget=w: self._changement_sans_calcul(widget))
        for w in [v.cb_fc28, v.cb_fe, v.cb_fis]:
            if w:
                w.currentTextChanged.connect(lambda t, widget=w: self._changement_sans_calcul(widget))

        # Recalcul de section réelle instantané
        for w in [v.spin_nb_1, v.spin_nb_2, v.spin_nb_3]:
            if w: w.valueChanged.connect(self._mettre_a_jour_section_reelle)
        for w in [v.cb_phi_1, v.cb_phi_2, v.cb_phi_3]:
            if w: w.currentTextChanged.connect(self._mettre_a_jour_section_reelle)

        if v.spin_nb_4:
            v.spin_nb_4.valueChanged.connect(lambda val, widget=v.spin_nb_4: v.reset_styles_entrer(widget))

    def _build_poutre_from_inputs(self):
        v = self.view
        b_cm = safe_float(v.e_b.text() if v.e_b else "0")
        h_cm = safe_float(v.e_h.text() if v.e_h else "0")
        l_m = safe_float(v.e_L.text() if v.e_L else "0")
        fc28_MPa = safe_float(v.cb_fc28.currentText() if v.cb_fc28 else "25", 25)
        fe_MPa = safe_float(v.cb_fe.currentText() if v.cb_fe else "500", 500)
        fis = str(v.cb_fis.currentText() if v.cb_fis else "FP")
        M_u_kNm = safe_float(v.e_Mu.text() if v.e_Mu else "0")
        M_ser_kNm = safe_float(v.e_Mser.text() if v.e_Mser else "0")
        V_u_kN = safe_float(v.e_Vu.text() if v.e_Vu else "0")

        erreurs = []
        if b_cm <= 0: 
            erreurs.append("La largeur b doit être supérieure à 0 cm")
            self.view.applique_erreur_entree(v.e_b)
        if h_cm <= 0: 
            erreurs.append("La hauteur h doit être supérieure à 0 cm")
            self.view.applique_erreur_entree(v.e_h)
        if l_m <= 0: 
            erreurs.append("La portée L doit être supérieure à 0 m")
            self.view.applique_erreur_entree(v.e_L)
        if M_u_kNm <= 0: 
            erreurs.append("Le moment à l'ELU Mu est requis")
            self.view.applique_erreur_entree(v.e_Mu)
        if M_ser_kNm <= 0: 
            erreurs.append("Le moment à l'ELS Mser est requis")
            self.view.applique_erreur_entree(v.e_Mser)
        if V_u_kN <= 0: 
            erreurs.append("L'effort tranchant à l'ELU Vu est requis")
            self.view.applique_erreur_entree(v.e_Vu)

        if erreurs:
            self.status_manager.set_status(CalculStatus.ERROR, f"{len(erreurs)} erreur(s) trouvée(s)", duration_ms=5000)
            """self.view.show_error("Erreur de saisie", "Données d'entrée invalides.", "• " + "\n• ".join(erreurs))"""
            return None
        return Poutre(b_cm, h_cm, l_m, fc28_MPa, fe_MPa, fis, M_u_kNm, M_ser_kNm, V_u_kN, "HA")

    def _changement_sans_calcul(self, widget_modifie):
        if self.poutre_calcule is None or widget_modifie is None or isinstance(widget_modifie, str):
            return
        if isinstance(widget_modifie, QLineEdit) and not widget_modifie.text().strip():
            return
        
        self.view.applique_warning(widget_modifie)
        self.status_manager.set_status(CalculStatus.WARNING, "Valeurs modifiées, veuillez recalculer.", duration_ms=5000)

    def calculer_section_theorique(self):
        try:
            v = self.view
            v.reset_tous_styles()
            self.status_manager.set_status(CalculStatus.CALCULATING)
            
            self.poutre_calcule = self._build_poutre_from_inputs()
            if self.poutre_calcule is None: return

            arm_long = self.poutre_calcule.calculer_ferraillage_longitudinal()
            cis = self.poutre_calcule.verifier_cisaillement()
            self.A_t_final = arm_long["A_t_final_cm2"]

            # Update UI via View
            v.actualisation_section(arm_long["condition"], arm_long["A_t_final_cm2"], v.lbl_sec)
            v.actualisation_icon(v.lbl_cis, cis["condition"])
            qtext_long(self.poutre_calcule, v.tb_resultat)

            self.status_manager.set_status(CalculStatus.SUCCESS, f"A_t = {self.A_t_final:.2f} cm²", duration_ms=3000)

            nb1 = int(v.spin_nb_1.value() if v.spin_nb_1 else 0)
            nb2 = int(v.spin_nb_2.value() if v.spin_nb_2 else 0)
            nb3 = int(v.spin_nb_3.value() if v.spin_nb_3 else 0)
            if sum([nb1, nb2, nb3]) > 0:
                print(sum([nb1, nb2, nb3]))
                self._mettre_a_jour_section_reelle()

        except Exception as e:
            self.status_manager.set_status(CalculStatus.ERROR, str(e))
            v.show_error("Erreur de calcul", "Le calcul longitudinal a échoué.", str(e))

    def verifier_fleche(self):
        if self.poutre_calcule:
            r_fleche = self.poutre_calcule.verifier_fleche()
            self.view.actualisation_icon(self.view.lbl_f, r_fleche["condition"])

    def _mettre_a_jour_section_reelle(self):
        v = self.view
        try:
            if self.poutre_calcule is None: return
            self.compositions = [
                (int(v.spin_nb_1.value() if v.spin_nb_1 else 0), safe_float(v.cb_phi_1.currentText() if v.cb_phi_1 else "0")),
                (int(v.spin_nb_2.value() if v.spin_nb_2 else 0), safe_float(v.cb_phi_2.currentText() if v.cb_phi_2 else "0")),
                (int(v.spin_nb_3.value() if v.spin_nb_3 else 0), safe_float(v.cb_phi_3.currentText() if v.cb_phi_3 else "0")),
            ]
            phis_utilises = [phi for nb, phi in self.compositions if nb > 0 and phi > 0]
            self.phi_l_min_mm = min(phis_utilises) if phis_utilises else None
            self._mettre_a_jour_diametre_arm_trans()

            a_reel = Poutre.calculer_section_reelle(self.compositions)
            if v.lbl_areel:
                if self.A_t_final > 0:
                    condition = a_reel >= self.A_t_final
                    self.view.actualisation_section(condition, a_reel, v.lbl_areel)
                    if v.lbl_valid:
                        v.lbl_valid.setPixmap(v.pixmap_valide if condition else v.pixmap_erreur)
                        v.lbl_valid.show()
                else:
                    v.lbl_areel.setText("Non calculée")
                    if v.lbl_valid: v.lbl_valid.hide()
        except Exception:
            self.status_manager.set_status(CalculStatus.ERROR, "Erreur section réelle")

    def _mettre_a_jour_diametre_arm_trans(self):
        cb = self.view.cb_phi_4
        if cb is None: return
        cb.blockSignals(True)
        cb.clear()
        if self.poutre_calcule and self.phi_l_min_mm:
            diametres = self.poutre_calcule.diametre_possible_arm_trans(self.phi_l_min_mm)
            cb.addItems([str(d) for d in diametres])
        cb.blockSignals(False)

    def calculer_armature_transversale(self):
        v = self.view
        if self.poutre_calcule is None:
            self.status_manager.set_status(CalculStatus.ERROR, "Calculez d'abord l'armature longitudinale", duration_ms=4000)
            return
            
        try:
            self.status_manager.set_status(CalculStatus.CALCULATING)
            
            # 1. Réinitialiser les styles d'erreur du bloc transversal avant de valider
            for widget in [v.spin_nb_4, v.cb_phi_4]:
                if widget:
                    widget.setObjectName("")
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)

            # 2. Récupération et validation du nombre de brins
            self.nb_brin = int(v.spin_nb_4.value() if v.spin_nb_4 else 0)
            if self.nb_brin <= 0:
                self.status_manager.set_status(CalculStatus.ERROR, "Le nombre de brins doit être supérieur à 0", duration_ms=3000)
                if v.spin_nb_4:
                    v.spin_nb_4.setObjectName("ErreurEntree")
                    v.spin_nb_4.style().unpolish(v.spin_nb_4)
                    v.spin_nb_4.style().polish(v.spin_nb_4)
                return

            # 3. Validation du diamètre
            if not v.cb_phi_4 or not v.cb_phi_4.currentText():
                self.status_manager.set_status(CalculStatus.ERROR, "Sélectionnez un diamètre d'armature", duration_ms=3000)
                if v.cb_phi_4:
                    v.cb_phi_4.setObjectName("ErreurEntree")
                    v.cb_phi_4.style().unpolish(v.cb_phi_4)
                    v.cb_phi_4.style().polish(v.cb_phi_4)
                return

            self.phi_t = int(safe_float(v.cb_phi_4.currentText()))
            if self.phi_t <= 0:
                self.status_manager.set_status(CalculStatus.ERROR, "Diamètre invalide", duration_ms=3000)
                if v.cb_phi_4:
                    v.cb_phi_4.setObjectName("ErreurEntree")
                    v.cb_phi_4.style().unpolish(v.cb_phi_4)
                    v.cb_phi_4.style().polish(v.cb_phi_4)
                return

            qtext_trans(self.poutre_calcule, v.tb_resultat_2, self.nb_brin, self.phi_t)
            
            self.status_manager.set_status(CalculStatus.SUCCESS, "Calcul transversal réussi")
            
        except Exception as e:
            self.status_manager.set_status(CalculStatus.ERROR, str(e))

    def _reset(self):
        v = self.view
        self.poutre_calcule, self.A_t_final, self.phi_l_min_mm = None, 0.0, None
        
        v._reset_label(v.lbl_sec)
        v._reset_label(v.lbl_cis, "Non effectuée")
        v._reset_label(v.lbl_f, "Non effectuée")
        v._reset_label(v.lbl_areel)
        
        if v.lbl_cis: v.lbl_cis.setText("Non effectuée")
        if v.lbl_f: v.lbl_f.setText("Non effectuée")

        if v.tb_resultat: v.tb_resultat.clear()
        if v.tb_resultat_2: v.tb_resultat_2.clear()

        for spin in [v.spin_nb_1, v.spin_nb_2, v.spin_nb_3, v.spin_nb_4]:
            if spin: spin.setValue(0)

        if v.cb_fc28: v.cb_fc28.setCurrentIndex(1)
        if v.cb_fe: v.cb_fe.setCurrentIndex(1)
        if v.cb_fis: v.cb_fis.setCurrentIndex(1)
        
        if v.cb_phi_1: v.cb_phi_1.setCurrentIndex(1)
        if v.cb_phi_2: v.cb_phi_2.setCurrentIndex(1)
        if v.cb_phi_3: v.cb_phi_3.setCurrentIndex(1)

        v.reset_tous_styles()

        self.status_manager.set_status(CalculStatus.IDLE, "Calcul réinitialisé")

    def show(self):
        if self.ui: self.ui.show()