"""
Configuration centralisée pour Kajizmo.
Gère les constantes, couleurs, et paramètres globaux.
"""

from enum import Enum
from PySide6.QtGui import QColor


class Colors(Enum):
    """Palette de couleurs cohérente de l'application."""
    
    # Fond et conteneurs
    BG_PRIMARY = QColor("#F5F7FA")      # Fond principal
    BG_SECONDARY = QColor("#FFFFFF")    # Cartes/conteneurs
    BG_HOVER = QColor("#F8FAFC")       # État hover
    BG_DISABLED = QColor("#F1F5F9")     # État disabled
    
    # Bordures
    BORDER_LIGHT = QColor("#E0E6ED")    # Bordures légères
    BORDER_MEDIUM = QColor("#CBD5E1")   # Bordures normales
    BORDER_DARK = QColor("#94A3B8")     # Bordures au hover
    
    # Texte
    TEXT_PRIMARY = QColor("#0F172A")    # Texte principal
    TEXT_SECONDARY = QColor("#475569")  # Texte secondaire
    TEXT_TERTIARY = QColor("#64748B")   # Texte tertiaire
    TEXT_DISABLED = QColor("#94A3B8")   # Texte désactivé
    
    # États
    SUCCESS = QColor("#16A34A")         # Succès (vert)
    WARNING = QColor("#EA8C55")         # Avertissement (orange)
    ERROR = QColor("#DC2626")           # Erreur (rouge)
    INFO = QColor("#0284C7")            # Information (bleu)
    
    # Spécifiques
    FOCUS = QColor("#3B82F6")           # Couleur focus (bleu)
    CONCRETE = QColor("#F0F0F5")        # Béton
    STEEL = QColor("#FF6464")           # Acier


class Fonts:
    """Configuration des polices."""
    
    FAMILY_PRIMARY = "Inter"
    FAMILY_SECONDARY = "Segoe UI"
    FAMILY_MONOSPACE = "Segoe UI Mono"
    
    SIZE_LARGE = 14          # Titres
    SIZE_NORMAL = 13         # Corps
    SIZE_SMALL = 12          # Sous-titres
    SIZE_TINY = 11           # Texte petit
    
    WEIGHT_BOLD = 600
    WEIGHT_SEMIBOLD = 500
    WEIGHT_NORMAL = 400
    WEIGHT_LIGHT = 300


class Spacing:
    """Constantes d'espacement."""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    
    # Padding des conteneurs
    CONTAINER_PADDING = 15
    SECTION_PADDING = 15
    
    # Gaps entre éléments
    BUTTON_GAP = 10
    FIELD_GAP = 5
    SECTION_GAP = 10


class BorderRadius:
    """Rayons de bordure cohérents."""
    
    SMALL = 6
    MEDIUM = 8
    LARGE = 10
    FULL = 999


class AnimationConfig:
    """Configuration des animations."""
    
    DURATION_FAST = 150      # ms
    DURATION_NORMAL = 300    # ms
    DURATION_SLOW = 500      # ms
    
    EASING_EASE_IN = "CubicEaseIn"
    EASING_EASE_OUT = "CubicEaseOut"
    EASING_EASE_IN_OUT = "CubicEaseInOut"


class StatusBarMessages:
    """Messages pré-configurés de la barre d'état."""
    
    IDLE = "Prêt"
    CALCULATING = "Calcul en cours..."
    SUCCESS = "✓ Calcul réussi"
    WARNING = "⚠ Attention: vérification requise"
    ERROR = "✗ Erreur"
    PARTIAL = "⊘ Calcul partiel"
    RESET = "Réinitialisé"
    
    DURATION_INSTANT = 0        # Persistant
    DURATION_SHORT = 2000       # 2 secondes
    DURATION_NORMAL = 3000      # 3 secondes
    DURATION_LONG = 5000        # 5 secondes


class CalculationDefaults:
    """Valeurs par défaut pour les calculs."""
    
    # Béton (MPa)
    FC28_DEFAULT = 25
    FC28_OPTIONS = [20, 25, 30, 35, 40, 45, 50, 55, 60]
    
    # Acier (MPa)
    FE_DEFAULT = 500
    FE_OPTIONS = [400, 500]
    
    # Fissuration
    FIS_DEFAULT = "FP"
    FIS_OPTIONS = ["FPP", "FP", "FTP"]
    
    # Dimensionnement (cm)
    B_DEFAULT = 25
    H_DEFAULT = 60
    L_DEFAULT = 6.93
    
    # Armatures
    ENROBAGE_HAUT = 5.0       # cm
    ENROBAGE_BAS = 5.0        # cm
    ESPACEMENT_HAUT = 5.0     # cm
    ESPACEMENT_BAS = 5.0      # cm
    
    # Diamètres disponibles (mm)
    DIAMETRES_AVAIL = [6, 8, 10, 12, 14, 16, 20, 25, 32]


class UIConfig:
    """Configuration générale de l'UI."""
    
    # Fenêtre
    MIN_WIDTH = 1000
    MIN_HEIGHT = 800
    MAX_WIDTH = 1400
    MAX_HEIGHT = 1000
    
    # Graphiques
    GRAPHICS_VIEW_MIN_HEIGHT = 250
    GRAPHICS_VIEW_SCALE_FACTOR = 1.2
    
    # Validation
    VALIDATION_TIMEOUT_MS = 500
    
    # Refresh rates
    STATUS_BAR_REFRESH_MS = 100
    GRAPHICS_UPDATE_DELAY_MS = 50


class ValidationRules:
    """Règles de validation pour les champs."""
    
    # Dimensions
    B_MIN = 10
    B_MAX = 200
    H_MIN = 20
    H_MAX = 300
    L_MIN = 1
    L_MAX = 50
    
    # Sollicitations
    MU_MIN = 0.1
    MU_MAX = 10000
    MSER_MIN = 0.1
    MSER_MAX = 10000
    VU_MIN = 0.1
    VU_MAX = 5000
    
    # Messages d'erreur
    ERRORS = {
        'b_invalid': "La largeur doit être entre {min} et {max} cm",
        'h_invalid': "La hauteur doit être entre {min} et {max} cm",
        'l_invalid': "La portée doit être entre {min} et {max} m",
        'mu_invalid': "Le moment ELU doit être positif",
        'mser_invalid': "Le moment ELS doit être positif",
        'vu_invalid': "L'effort tranchant doit être positif",
    }


class ExportConfig:
    """Configuration pour les exports."""
    
    # Format PDF
    PDF_PAGE_SIZE = "A4"
    PDF_MARGIN = 20         # mm
    PDF_FONT_TITLE = 16
    PDF_FONT_BODY = 11
    
    # Format Excel
    EXCEL_COLS_WIDTH = 15
    EXCEL_SHEET_NAMES = {
        'input': "Données d'entrée",
        'output': "Résultats",
        'repartition': "Répartition",
        'history': "Historique"
    }
    
    # Format texte
    TXT_LINE_WIDTH = 80
    TXT_SEPARATOR = "=" * 80


class CacheConfig:
    """Configuration du cache."""
    
    ENABLED = True
    MAX_SIZE = 100          # nombre de calculs en cache
    TTL_SECONDS = 3600      # Durée de vie (1h)


# Configuration Géométrique des graphiques
class GraphicsConfig:
    """Configuration des graphiques."""
    
    # Échelle
    SECTION_SCALE_FACTOR = 1.0
    COUPE_SCALE_FACTOR = 1.0
    
    # Couleurs (béton)
    CONCRETE_COLOR = QColor(240, 240, 245)
    CONCRETE_BORDER = QColor(50, 50, 100)
    CONCRETE_BORDER_WIDTH = 2
    
    # Couleurs (acier tendu)
    STEEL_TENSION_COLOR = QColor(255, 100, 100)
    STEEL_TENSION_BORDER = QColor(200, 0, 0)
    STEEL_TENSION_BORDER_WIDTH = 1.5
    
    # Couleurs (acier comprimé)
    STEEL_COMPRESSION_COLOR = QColor(100, 150, 255)
    STEEL_COMPRESSION_BORDER = QColor(0, 0, 200)
    STEEL_COMPRESSION_BORDER_WIDTH = 1.5
    
    # Cadres
    CADRE_INITIAL_COLOR = QColor(220, 20, 60)     # Crimson
    CADRE_INITIAL_WIDTH = 3
    CADRE_REGULAR_COLOR = QColor(30, 144, 255)   # Dodger Blue
    CADRE_REGULAR_WIDTH = 2
    CADRE_VARIABLE_COLOR = QColor(100, 149, 237)  # Cornflower Blue
    CADRE_VARIABLE_WIDTH = 1.5
    
    # Annotations
    ANNOTATION_FONT_SIZE = 10
    ANNOTATION_COLOR = QColor(100, 100, 100)
    
    # Dimensions de vue
    SECTION_VIEW_WIDTH = 450
    SECTION_VIEW_HEIGHT = 450
    COUPE_VIEW_WIDTH = 950
    COUPE_VIEW_HEIGHT = 200


# Configuration de l'application globale
APP_CONFIG = {
    'app_name': 'Kajizmo',
    'app_version': '2.0',
    'app_subtitle': 'Outil de calcul BAEL pour poutres en béton armé',
    'organization': 'Kajizmo',
    'enable_logging': True,
    'log_level': 'INFO',
}


def get_color_rgb(color: QColor) -> tuple:
    """Extrait les composantes RGB d'une couleur."""
    return (color.red(), color.green(), color.blue())


def get_color_hex(color: QColor) -> str:
    """Retourne la couleur au format hexadécimal."""
    return color.name()