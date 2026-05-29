# main.py
"""
main.py - Point d'entrée de l'application Kajizmo Enhanced
Intègre tous les modules améliorés: statusbar, style moderne
"""

import sys
import os
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from config import APP_CONFIG

# Ajouter les chemins du projet
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

# Imports après configuration des chemins
from src.controllers.main_controller import MainController

def resource_path(relative_path):
    """ Rend les chemins d'accès compatibles avec PyInstaller et le mode Dev """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def setup_logging():
    """Configure le système de logging."""
    log_level = logging.INFO if APP_CONFIG['log_level'] == 'INFO' else logging.DEBUG

    if sys.platform == "win32":
        for stream_name in ("stdout", "stderr"):
            stream = getattr(sys, stream_name, None)
            if stream is not None and hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding='utf-8')
    
    log_stream = (
        getattr(sys, "stdout", None)
        or getattr(sys, "__stdout__", None)
        or getattr(sys, "stderr", None)
        or getattr(sys, "__stderr__", None)
    )
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('kajizmo.log', encoding='utf-8'),
            logging.StreamHandler(log_stream)
        ]
    )
    
    return logging.getLogger(__name__)

def load_stylesheet():
    """Charge et retourne la feuille de style CSS."""
    stylesheet_path = resource_path(os.path.join("assets", "styles", "stylesheet_enhanced.css"))
    
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        logger.warning(f"Stylesheet non trouvé: {stylesheet_path}")
        return ""

def show_splash_screen(app):
    """Affiche un écran de démarrage (splash screen) optionnel."""
    try:
        splash_path = resource_path(os.path.join("assets", "icons", "splash.png"))
        
        if os.path.exists(splash_path):
            splash_pixmap = QPixmap(splash_path)
            splash = QSplashScreen(splash_pixmap)
            splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            splash.show()
            
            splash.showMessage(
                f"Initialisation de {APP_CONFIG['app_name']} v{APP_CONFIG['app_version']}...",
                Qt.AlignBottom | Qt.AlignCenter,
                Qt.white
            )
            
            app.processEvents()
            return splash
    except Exception as e:
        logger.warning(f"Impossible de charger le splash screen: {e}")
    
    return None


def main():
    """Point d'entrée principal de l'application."""
    # Créer l'application
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName(APP_CONFIG['app_name'])
    app.setApplicationVersion(APP_CONFIG['app_version'])
    
    # Logging
    global logger
    logger = setup_logging()
    logger.info(f"Démarrage de {APP_CONFIG['app_name']} v{APP_CONFIG['app_version']}")
    
    # Splash screen
    splash = show_splash_screen(app)
    
    # Charger le stylesheet
    logger.info("Chargement du stylesheet...")
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
        logger.info("Stylesheet chargé avec succès")
    else:
        logger.warning("Utilisation du style par défaut")
    
    # Créer le contrôleur principal
    logger.info("Initialisation du contrôleur...")
    try:
        controller = MainController()
        logger.info("Contrôleur initialisé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du contrôleur: {e}", exc_info=True)
        if splash:
            splash.close()
        
        # Afficher un message d'erreur
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Erreur d'initialisation",
            f"Impossible de démarrer l'application:\n{e}"
        )
        return 1
    
    # Afficher la fenêtre principale
    logger.info("Affichage de la fenêtre principale...")
    controller.show()
    
    # Fermer le splash screen
    if splash:
        QTimer.singleShot(1000, splash.close)
    
    # Boucle d'événements
    logger.info("Application démarrée. En attente d'entrée utilisateur...")
    exit_code = app.exec()
    
    logger.info(f"Application fermée (code: {exit_code})")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
