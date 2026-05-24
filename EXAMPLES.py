"""
EXEMPLES D'UTILISATION - Kajizmo
Démonstration des nouvelles fonctionnalités et API
"""

# ============================================================================
# 1. UTILISATION DE LA BARRE DE STATUT
# ============================================================================

from main_control import MainController, CalculStatus

# Initialiser le contrôleur
controller = MainController()

# Exemple 1: Message temporaire (succès)
# ─────────────────────────────────────
controller.status_manager.set_status(
    CalculStatus.SUCCESS,
    f"Calcul terminé - A_t = 18.50 cm²",
    duration_ms=3000  # Affiche 3 secondes puis s'efface
)
# Affichage: ✓ Calcul réussi - A_t = 18.50 cm²


# Exemple 2: Message persistant (erreur)
# ───────────────────────────────────────
controller.status_manager.set_status(
    CalculStatus.ERROR,
    "Erreur: Largeur invalide"
)
# Affichage: ✗ Erreur - Erreur: Largeur invalide
# Reste affiché jusqu'à prochaine update


# Exemple 3: Message pendant traitement
# ──────────────────────────────────────
controller.status_manager.set_status(CalculStatus.CALCULATING)
# Affichage: Calcul en cours... (spinner implicite)

# ... effectuer le traitement ...

# Retour au succès
controller.status_manager.set_status(
    CalculStatus.SUCCESS,
    "Traitement terminé",
    duration_ms=2000
)


# Exemple 4: Avertissement non-critique
# ──────────────────────────────────────
controller.status_manager.set_status(
    CalculStatus.PARTIAL,
    "Configuration incomplète - Certains champs vides",
    duration_ms=4000
)


# ============================================================================
# 2. UTILISATION DES GRAPHIQUES - SECTION TRANSVERSALE
# ============================================================================

from graphics_manager import SectionTransversaleDrawer
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

# Créer une scène
scene = QGraphicsScene()

# Créer le drawer
drawer = SectionTransversaleDrawer(scene)

# Exemple 1: Dessin simple
# ────────────────────────
drawer.dessiner_section(
    b_cm=25,        # largeur 25 cm
    h_cm=60,        # hauteur 60 cm
    compositions=[  # listes (nb_barres, diamètre)
        (3, 12),    # 3 barres de ∅12
        (3, 14),    # 3 barres de ∅14
        (0, 10)     # 0 barre de ∅10 (pas utilisé)
    ],
    phi_l_min=10    # diamètre min pour arm. transversales
)
# Résultat: Section dessinée avec armatures annotées


# Exemple 2: Après recalcul
# ──────────────────────────
# Si l'utilisateur change la configuration:
new_compositions = [
    (4, 12),    # 4 barres de ∅12
    (2, 14),    # 2 barres de ∅14
    (0, 10)
]

drawer.dessiner_section(25, 60, new_compositions, 10)
# Résultat: Section mise à jour instantanément


# Exemple 3: Intégration dans Qt
# ───────────────────────────────
graphics_view = QGraphicsView()
graphics_view.setScene(scene)
# La scène se met à jour automatiquement lors des appels dessiner_section()


# ============================================================================
# 3. UTILISATION DES GRAPHIQUES - COUPE LONGITUDINALE
# ============================================================================

from graphics_manager import CoupeLongitudinalDrawer

scene_coupe = QGraphicsScene()
drawer_coupe = CoupeLongitudinalDrawer(scene_coupe)

# Exemple 1: Dessin de la coupe après calcul transversal
# ───────────────────────────────────────────────────────
drawer_coupe.dessiner_coupe(
    l_m=6.93,                          # longueur 6.93 m
    h_cm=60,                           # hauteur 60 cm
    disposition=[3.5, 7, 8, 8, 9, 10, 11, 13, 16, 20, 25, 30],  # espacements
    st0=3.5,                           # espacement initial
    st=8.5,                            # espacement calculé
    st_max=40                          # espacement maximal
)
# Résultat: Coupe avec cadres répartis selon Caquot


# Exemple 2: Mise à jour après changement de diamètre
# ────────────────────────────────────────────────────
drawer_coupe.dessiner_coupe(
    l_m=6.93,
    h_cm=60,
    disposition=[4, 8, 9, 10, 11, 13, 16, 20, 25],  # nouvelle répartition
    st0=4,      # nouveau st0
    st=9,       # nouveau st
    st_max=40
)
# Résultat: Coupe rafraîchie avec nouvelles valeurs


# ============================================================================
# 4. UTILISATION DE LA CONFIGURATION CENTRALISÉE
# ============================================================================

from config import Colors, Fonts, Spacing, CalculationDefaults, GraphicsConfig
from PySide6.QtGui import QColor

# Exemple 1: Accéder aux couleurs
# ────────────────────────────────
couleur_succes = Colors.SUCCESS.value
print(f"Couleur succès: {couleur_succes.name()}")  # #16A34A

couleur_erreur = Colors.ERROR.value
# Utiliser dans du code:
label.setStyleSheet(f"color: {couleur_erreur.name()}")


# Exemple 2: Utiliser les espacements standards
# ──────────────────────────────────────────────
from config import Spacing

widget.setContentsMargins(
    Spacing.CONTAINER_PADDING,
    Spacing.CONTAINER_PADDING,
    Spacing.CONTAINER_PADDING,
    Spacing.CONTAINER_PADDING
)

button.setStyleSheet(f"padding: {Spacing.MD}px {Spacing.LG}px")


# Exemple 3: Accéder aux valeurs par défaut
# ───────────────────────────────────────────
from config import CalculationDefaults

# Remplir une combobox
fc28_values = CalculationDefaults.FC28_OPTIONS
for val in fc28_values:
    combo_fc28.addItem(str(val))

# Utiliser valeurs par défaut
default_b = CalculationDefaults.B_DEFAULT  # 25 cm
default_h = CalculationDefaults.H_DEFAULT  # 60 cm

# Diamètres disponibles
diametres = CalculationDefaults.DIAMETRES_AVAIL
print(f"Diamètres: {diametres}")  # [6, 8, 10, 12, 14, 16, 20, 25, 32]


# Exemple 4: Configuration graphique
# ──────────────────────────────────
from config import GraphicsConfig

# Couleur du béton
couleur_beton = GraphicsConfig.CONCRETE_COLOR

# Couleur de l'acier tendu
couleur_acier = GraphicsConfig.STEEL_TENSION_COLOR


# ============================================================================
# 5. INTÉGRATION COMPLÈTE DANS LE CONTRÔLEUR
# ============================================================================

class MonControleur(MainController):
    """Exemple d'extension du MainController."""
    
    def __init__(self):
        super().__init__()
        
        # Ajouter des signaux custom
        self.mon_signal_personnalise = None
    
    def mon_calcul_personnalise(self):
        """Exemple de fonction personnalisée."""
        
        try:
            # Montrer que c'est en cours
            self.status_manager.set_status(CalculStatus.CALCULATING)
            
            # Faire le calcul
            poutre = self._build_poutre_from_inputs()
            if poutre is None:
                return
            
            # Appeler les méthodes du moteur
            result_long = poutre.calculer_ferraillage_longitudinal()
            result_trans = poutre.calculer_ferraillage_transversale(
                nb_brin=4,
                phi_t=10,
            )
            
            # Mettre à jour les graphiques
            self.section_drawer.dessiner_section(
                poutre.b_cm,
                poutre.h_cm,
                compositions=[(3, 12), (3, 14)],
                phi_l_min=10
            )
            
            # Afficher succès
            self.status_manager.set_status(
                CalculStatus.SUCCESS,
                f"Calcul personnalisé réussi",
                duration_ms=3000
            )
            
        except Exception as e:
            self.status_manager.set_status(
                CalculStatus.ERROR,
                str(e),
                duration_ms=5000
            )


# ============================================================================
# 6. GESTION DES ERREURS ET VALIDATIONS
# ============================================================================

# Exemple 1: Validation avec feedback
# ────────────────────────────────────
def valider_largeur(b_cm):
    """Valide la largeur de la poutre."""
    from config import ValidationRules
    
    if b_cm < ValidationRules.B_MIN:
        controller.status_manager.set_status(
            CalculStatus.ERROR,
            f"Largeur trop petite (min: {ValidationRules.B_MIN} cm)",
            duration_ms=4000
        )
        return False
    
    if b_cm > ValidationRules.B_MAX:
        controller.status_manager.set_status(
            CalculStatus.ERROR,
            f"Largeur trop grande (max: {ValidationRules.B_MAX} cm)",
            duration_ms=4000
        )
        return False
    
    return True


# Exemple 2: Gestion des exceptions
# ──────────────────────────────────
try:
    result = poutre.calculer_ferraillage_longitudinal()
    
    if result['condition']:
        controller.status_manager.set_status(
            CalculStatus.SUCCESS,
            "✓ Toutes les vérifications OK"
        )
    else:
        controller.status_manager.set_status(
            CalculStatus.WARNING,
            "⚠ Une ou plusieurs vérifications échouées",
            duration_ms=5000
        )
        
except ValueError as e:
    controller.status_manager.set_status(
        CalculStatus.ERROR,
        f"Erreur de calcul: {e}",
        duration_ms=5000
    )
    controller._show_error(
        "Erreur de calcul",
        "Impossible d'effectuer le calcul",
        f"Détail: {e}"
    )


# ============================================================================
# 7. EXPORT ET PERSISTENCE
# ============================================================================

import json
from pathlib import Path

# Exemple 1: Sauvegarder une configuration
# ─────────────────────────────────────────
def sauvegarder_configuration(filename="config.json"):
    """Sauvegarde les données d'entrée."""
    config_data = {
        'b_cm': controller.e_b.text(),
        'h_cm': controller.e_h.text(),
        'l_m': controller.e_L.text(),
        'fc28': controller.cb_fc28.currentText(),
        'fe': controller.cb_fe.currentText(),
        'fissuration': controller.cb_fis.currentText(),
        'mu': controller.e_Mu.text(),
        'mser': controller.e_Mser.text(),
        'vu': controller.e_Vu.text(),
    }
    
    with open(filename, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    controller.status_manager.set_status(
        CalculStatus.SUCCESS,
        f"Configuration sauvegardée: {filename}",
        duration_ms=2000
    )


# Exemple 2: Charger une configuration
# ─────────────────────────────────────
def charger_configuration(filename="config.json"):
    """Charge une configuration sauvegardée."""
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)
        
        # Remplir les champs
        controller.e_b.setText(config_data['b_cm'])
        controller.e_h.setText(config_data['h_cm'])
        controller.e_L.setText(config_data['l_m'])
        controller.cb_fc28.setCurrentText(config_data['fc28'])
        controller.cb_fe.setCurrentText(config_data['fe'])
        controller.cb_fis.setCurrentText(config_data['fissuration'])
        controller.e_Mu.setText(config_data['mu'])
        controller.e_Mser.setText(config_data['mser'])
        controller.e_Vu.setText(config_data['vu'])
        
        controller.status_manager.set_status(
            CalculStatus.SUCCESS,
            f"Configuration chargée: {filename}",
            duration_ms=2000
        )
        
    except FileNotFoundError:
        controller.status_manager.set_status(
            CalculStatus.ERROR,
            f"Fichier non trouvé: {filename}",
            duration_ms=3000
        )
    except Exception as e:
        controller.status_manager.set_status(
            CalculStatus.ERROR,
            f"Erreur chargement config: {e}",
            duration_ms=3000
        )


# ============================================================================
# 8. EXTENSIONS PERSONNALISÉES
# ============================================================================

# Exemple: Ajouter un calcul rapide sans recalculer tout
# ──────────────────────────────────────────────────────

def calcul_rapide_estimation(b, h, l):
    """Estimation rapide pour feedback utilisateur."""
    from math import pi
    
    # Formule approximative pour poutres simples
    qser = 10  # charge uniformément répartie kN/m
    m_ser = qser * l**2 / 8
    
    # Estimation section acier
    fc28 = 25
    a_estim = m_ser * 1000 / (0.9 * h/100 * 400)  # approximatif
    
    return a_estim


# Utiliser pour affichage temps réel
def afficher_estimation():
    """Affiche une estimation pendant la saisie."""
    try:
        b = float(controller.e_b.text())
        h = float(controller.e_h.text())
        l = float(controller.e_L.text())
        
        a_estim = calcul_rapide_estimation(b, h, l)
        
        controller.status_manager.set_status(
            CalculStatus.INFO,
            f"Estimation: A ≈ {a_estim:.1f} cm²",
            duration_ms=2000
        )
    except:
        pass


# ============================================================================
# 9. STATISTIQUES ET HISTORIQUE (OPTIONNEL)
# ============================================================================

from collections import deque
from datetime import datetime

class HistoriqueCalculs:
    """Stocke l'historique des calculs."""
    
    def __init__(self, max_items=50):
        self.calculs = deque(maxlen=max_items)
    
    def ajouter(self, poutre, resultats):
        """Ajoute un calcul à l'historique."""
        self.calculs.append({
            'timestamp': datetime.now(),
            'poutre': poutre,
            'resultats': resultats
        })
    
    def obtenir_derniers(self, n=10):
        """Obtient les n derniers calculs."""
        return list(reversed(list(self.calculs)))[:n]
    
    def statistiques(self):
        """Génère des statistiques."""
        if not self.calculs:
            return {}
        
        a_t_values = [c['resultats']['A_t_final_cm2'] for c in self.calculs]
        
        return {
            'total_calculs': len(self.calculs),
            'a_t_min': min(a_t_values),
            'a_t_max': max(a_t_values),
            'a_t_moy': sum(a_t_values) / len(a_t_values),
            'premier_calcul': self.calculs[0]['timestamp'],
            'dernier_calcul': self.calculs[-1]['timestamp'],
        }


# Utilisation
historique = HistoriqueCalculs()

# Dans le contrôleur, après chaque calcul:
# historique.ajouter(poutre_calcule, res_arm_long)

# Afficher stats
stats = historique.statistiques()
print(f"Moyenne A_t: {stats['a_t_moy']:.2f} cm²")


# ============================================================================
# 10. TESTS UNITAIRES
# ============================================================================

import unittest

class TestSectionTransversaleDrawer(unittest.TestCase):
    """Tests pour le dessin de section."""
    
    def setUp(self):
        from PySide6.QtWidgets import QGraphicsScene
        scene = QGraphicsScene()
        self.drawer = SectionTransversaleDrawer(scene)
    
    def test_dessiner_section_simple(self):
        """Test dessin simple."""
        self.drawer.dessiner_section(25, 60, [(3, 12)], 10)
        # Vérifier que des items ont été ajoutés
        items = self.drawer.scene.items()
        self.assertGreater(len(items), 0)
    
    def test_positions_horizontales(self):
        """Test calcul positions."""
        positions = self.drawer._calculer_positions_horizontales(25, 3)
        self.assertEqual(len(positions), 3)
        # Positions symétriques autour du centre
        self.assertAlmostEqual(positions[1], 12.5, places=0)


# ============================================================================
# FIN DES EXEMPLES
# ============================================================================

print("""
Exemples de code chargés avec succès!

Disponible:
- MainController (contrôleur amélioré)
- SectionTransversaleDrawer
- CoupeLongitudinalDrawer
- Gestion de statusbar
- Configuration centralisée

Pour plus d'info, consultez les fichiers:
- GUIDE_AMELIORATIONS.md
- MODIFICATIONS_DETAILLEES.md
- README_IMPLEMENTATION.md
""")
