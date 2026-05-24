# status_manager.py
from enum import Enum
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor

class CalculStatus(Enum):
    """États possibles des calculs."""
    IDLE = "Prêt"
    CALCULATING = "Calcul en cours..."
    SUCCESS = "Calcul réussi"
    WARNING = "Attention: "
    ERROR = "Erreur"
    PARTIAL = "Calcul partiel"


class StatusBarManager:
    """Gère la barre de statut avec messages temporaires."""
    
    def __init__(self, statusbar):
        self.statusbar = statusbar
        self.timer = QTimer()
        self.timer.timeout.connect(self._clear_message)
        self.default_message = "Prêt"
        self.status_map = {
            CalculStatus.IDLE: ("Prêt", QColor(34, 139, 34)),
            CalculStatus.CALCULATING: ("Calcul en cours...", QColor(255, 165, 0)),
            CalculStatus.SUCCESS: ("✓ Calcul réussi", QColor(34, 139, 34)),
            CalculStatus.WARNING: ("⚠ Attention ", QColor(217, 119, 6)),
            CalculStatus.ERROR: ("✗ Erreur dans le calcul", QColor(220, 20, 60)),
            CalculStatus.PARTIAL: ("⊘ Calcul partiel", QColor(100, 149, 237)),
        }
        
    def set_status(self, status: CalculStatus, message: str = "", duration_ms: int = 0):
        """Définit le statut avec message optionnel et durée d'affichage."""
        self.timer.stop()
        
        status_text, color = self.status_map.get(status, (status.value, QColor(128, 128, 128)))
        
        if message:
            display_text = f"{status_text} | {message}"
        else:
            display_text = status_text
        
        self.statusbar.showMessage(display_text)
        
        # Style de la barre
        style = f"QStatusBar {{ color: {color.name()}; padding: 2px; }}"
        self.statusbar.setStyleSheet(style)
        
        # Réinitialiser après durée
        if duration_ms > 0:
            self.timer.start(duration_ms)
    
    def _clear_message(self):
        """Réinitialise le message à l'état par défaut."""
        self.timer.stop()
        self.statusbar.showMessage(self.default_message)
        self.statusbar.setStyleSheet("QStatusBar { color: #4B5563; padding: 2px; }")