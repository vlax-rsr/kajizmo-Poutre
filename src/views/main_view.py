# src/views/main_view.py
import os
import sys  # Ajouté pour sys._MEIPASS
from PySide6.QtCore import QFile, QLocale, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLineEdit, QComboBox, QPushButton, QLabel, QTextBrowser, QSpinBox, QMessageBox
from PySide6.QtGui import QIcon, QDoubleValidator, QPixmap

def resource_path(relative_path):
    """ Rend les chemins d'accès compatibles avec PyInstaller et le mode Dev """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainView:
    """Gère uniquement l'interface graphique et l'état visuel des widgets."""
    def __init__(self):
        loader = QUiLoader()
        
        # CORRECTION : Enveloppement du chemin UI avec resource_path
        ui_path = resource_path(os.path.join("src", "views", "kajizmo_interface.ui"))

        file = QFile(ui_path)
        if not file.open(QFile.ReadOnly):
            raise FileNotFoundError(f"Impossible d'ouvrir le fichier UI: {ui_path}")
        
        self.ui = loader.load(file)
        file.close()

        if self.ui is None:
            raise RuntimeError("Le chargement de l'interface a échoué.")
        
        # CORRECTION : Enveloppement de l'icône de l'application
        self.ui.setWindowIcon(QIcon(resource_path(os.path.join("assets", "icons", "kajizmo_alpha.png"))))
        self._init_widgets()
        self._setup_validators()
        self._init_icons()

    def _init_widgets(self):
        # Entrées Géométrie / Sollicitations
        self.e_b = self.ui.findChild(QLineEdit, "e_b")
        self.e_h = self.ui.findChild(QLineEdit, "e_h")
        self.e_L = self.ui.findChild(QLineEdit, "e_L")
        self.cb_fc28 = self.ui.findChild(QComboBox, "cb_fc28")
        self.cb_fe = self.ui.findChild(QComboBox, "cb_fe")
        self.cb_fis = self.ui.findChild(QComboBox, "cb_fis")
        self.e_Mu = self.ui.findChild(QLineEdit, "e_Mu")
        self.e_Mser = self.ui.findChild(QLineEdit, "e_Mser")
        self.e_Vu = self.ui.findChild(QLineEdit, "e_Vu")

        # Boutons
        self.b_armLong = self.ui.findChild(QPushButton, "b_armLong")
        self.b_armTrans = self.ui.findChild(QPushButton, "b_armTrans")
        self.b_reset = self.ui.findChild(QPushButton, "b_reset")

        # Résultats & Outputs
        self.lbl_sec = self.ui.findChild(QLabel, "lbl_sec")
        self.lbl_cis = self.ui.findChild(QLabel, "lbl_cis")
        self.lbl_areel = self.ui.findChild(QLabel, "lbl_areel")
        self.lbl_valid = self.ui.findChild(QLabel, "lbl_valid")
        self.lbl_f = self.ui.findChild(QLabel, "lbl_f")
        self.tb_resultat = self.ui.findChild(QTextBrowser, "tb_resultat")
        self.tb_resultat_2 = self.ui.findChild(QTextBrowser, "tb_resultat_2")

        # Choix des barres
        self.spin_nb_1 = self.ui.findChild(QSpinBox, "spin_nb_1")
        self.spin_nb_2 = self.ui.findChild(QSpinBox, "spin_nb_2")
        self.spin_nb_3 = self.ui.findChild(QSpinBox, "spin_nb_3")
        self.cb_phi_1 = self.ui.findChild(QComboBox, "cb_phi_1")
        self.cb_phi_2 = self.ui.findChild(QComboBox, "cb_phi_2")
        self.cb_phi_3 = self.ui.findChild(QComboBox, "cb_phi_3")

        # Armatures Transversales
        self.spin_nb_4 = self.ui.findChild(QSpinBox, "spin_nb_4")
        self.cb_phi_4 = self.ui.findChild(QComboBox, "cb_phi_4")

    def _init_icons(self):
        # CORRECTION : Détermination propre du dossier assets extrait par PyInstaller
        dossier_icons = resource_path(os.path.join("assets", "icons"))
        
        self.pixmap_valide = QPixmap(os.path.join(dossier_icons, "valide.png")).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pixmap_erreur = QPixmap(os.path.join(dossier_icons, "erreur.png")).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if self.lbl_valid:
            self.lbl_valid.hide()

    def _setup_validators(self):
        validator = QDoubleValidator()
        validator.setBottom(0.0)
        validator.setNotation(QDoubleValidator.StandardNotation)
        validator.setLocale(QLocale(QLocale.English))
        for field in [self.e_b, self.e_h, self.e_L, self.e_Mu, self.e_Mser, self.e_Vu]:
            if field:
                field.setValidator(validator)

    def show_error(self, title: str, message: str, details: str = ""):
        msg_box = QMessageBox(self.ui)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if details:
            msg_box.setInformativeText(details)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def actualisation_section(self, condition: bool, sec_calcule: float, label: QLabel):
        if label is None: return
        label.setText(f"{sec_calcule:.2f} cm²")
        label.setObjectName("ResultatValide" if condition else "ResultatErreur")
        label.style().unpolish(label)
        label.style().polish(label)

    def actualisation_icon(self, label: QLabel, condition: bool):
        if label:
            label.setPixmap(self.pixmap_valide if condition else self.pixmap_erreur)

    def applique_warning(self, widget):
        if widget and not isinstance(widget, str):
            widget.setObjectName("Warning")
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def applique_erreur_entree(self, widget):
        if widget and not isinstance(widget, str):
            widget.setObjectName("ErreurEntree")
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def reset_styles_entrer(self, widget):
        if widget is None:
            return 
            
        widget.setObjectName("")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def reset_tous_styles(self):
        tous_les_champs = [
            self.e_b, self.e_h, self.e_Mu, self.e_Mser, self.e_Vu,
            self.cb_fc28, self.cb_fe, self.cb_fis, self.e_L,
            self.spin_nb_1, self.spin_nb_2, self.spin_nb_3,
            self.cb_phi_1, self.cb_phi_2, self.cb_phi_3
        ]
        for w in tous_les_champs:
            if w:
                self.reset_styles_entrer(w)

    def _reset_label(self, label: QLabel, texte: str = "Non calculée"):
        """Réinitialise un label de résultat."""
        if label is None:
            return
        label.setText(texte)
        label.setObjectName("")
        label.style().unpolish(label)
        label.style().polish(label)