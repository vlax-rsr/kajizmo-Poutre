"""
Module de visualisation graphique pour Kajizmo.
Gère le dessin de la section transversale et de la coupe longitudinale.
"""

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainterPath


class SectionTransversaleDrawer:
    """Dessine la section transversale de la poutre avec ses armatures."""
    
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.scale = 1.0  # pixels par cm
        
    def dessiner_section(self, b_cm: float, h_cm: float, compositions: list, phi_l_min: float = None):
        """
        Dessine la section transversale de la poutre.
        
        Args:
            b_cm: Largeur en cm
            h_cm: Hauteur en cm
            compositions: Liste de tuples (nombre_barres, diametre)
            phi_l_min: Diamètre minimal des barres
        """
        self.scene.clear()
        self.scale = min(400 / b_cm, 400 / h_cm)  # Adapter l'échelle Ã  la vue
        
        # Béton (fond gris clair)
        concrete_rect = QGraphicsRectItem(0, 0, b_cm * self.scale, h_cm * self.scale)
        concrete_brush = QBrush(QColor(240, 240, 245))
        concrete_pen = QPen(QColor(50, 50, 100), 2)
        concrete_rect.setBrush(concrete_brush)
        concrete_rect.setPen(concrete_pen)
        self.scene.addItem(concrete_rect)
        
        # Armatures longitudinales (tendues en bas)
        self._dessiner_armatures_longitudinales(b_cm, h_cm, compositions)
        
        # Texte informatif
        info_text = QGraphicsTextItem(f"Section: {b_cm:.0f} Ã— {h_cm:.0f} cm")
        info_font = QFont("Inter", 10)
        info_text.setFont(info_font)
        info_text.setPos(10, h_cm * self.scale + 10)
        self.scene.addItem(info_text)
        
        # Dimensions
        self._dessiner_cotes(b_cm, h_cm)
        
    def _dessiner_armatures_longitudinales(self, b_cm: float, h_cm: float, compositions: list):
        """Dessine les armatures longitudinales."""
        # Espacement uniforme depuis les bords
        y_top = 5  # cm depuis le haut (enrobage)
        y_bottom = h_cm - 5  # cm depuis le bas (armatures tendues)
        
        nb_total = sum(nb for nb, _ in compositions)
        if nb_total == 0:
            return
            
        # Distribution horizontale
        x_positions = self._calculer_positions_horizontales(b_cm, nb_total)
        
        index = 0
        for nb_barres, phi in compositions:
            for i in range(nb_barres):
                if index < len(x_positions):
                    x = x_positions[index]
                    
                    # Barres tendues (bas)
                    circle_bottom = QGraphicsEllipseItem(
                        (x - phi/2) * self.scale,
                        (y_bottom - phi/2) * self.scale,
                        phi * self.scale,
                        phi * self.scale
                    )
                    circle_bottom.setPen(QPen(QColor(200, 0, 0), 1.5))
                    circle_bottom.setBrush(QBrush(QColor(255, 100, 100)))
                    self.scene.addItem(circle_bottom)
                    
                    # Numéro de la barre
                    text = QGraphicsTextItem(f"âˆ…{int(phi)}")
                    text.setFont(QFont("Arial", 7))
                    text.setPos((x - 3) * self.scale, (y_bottom + 3) * self.scale)
                    self.scene.addItem(text)
                    
                    index += 1
    
    def _calculer_positions_horizontales(self, b_cm: float, nb_barres: int) -> list:
        """Calcule les positions horizontales des barres."""
        if nb_barres == 1:
            return [b_cm / 2]
        
        spacing = (b_cm - 4) / (nb_barres - 1)  # 4cm = 2cm enrobage de chaque cÃ´té
        return [2 + i * spacing for i in range(nb_barres)]
    
    def _dessiner_cotes(self, b_cm: float, h_cm: float):
        """Dessine les cotes de la section."""
        # Cote largeur (bas)
        line_bottom = QGraphicsLineItem(0, (h_cm + 1) * self.scale, b_cm * self.scale, (h_cm + 1) * self.scale)
        line_bottom.setPen(QPen(QColor(100, 100, 100), 1))
        self.scene.addItem(line_bottom)
        
        text_b = QGraphicsTextItem(f"b = {b_cm:.0f} cm")
        text_b.setFont(QFont("Arial", 9))
        text_b.setPos(b_cm * self.scale / 2 - 30, (h_cm + 2) * self.scale)
        self.scene.addItem(text_b)
        
        # Cote hauteur (droite)
        line_right = QGraphicsLineItem((b_cm + 1) * self.scale, 0, (b_cm + 1) * self.scale, h_cm * self.scale)
        line_right.setPen(QPen(QColor(100, 100, 100), 1))
        self.scene.addItem(line_right)
        
        text_h = QGraphicsTextItem(f"h = {h_cm:.0f} cm")
        text_h.setFont(QFont("Arial", 9))
        text_h.setPos((b_cm + 2) * self.scale, h_cm * self.scale / 2 - 20)
        self.scene.addItem(text_h)


class CoupeLongitudinalDrawer:
    """Dessine la coupe longitudinale avec répartition des armatures transversales."""
    
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.scale = 1.0
        
    def dessiner_coupe(self, l_m: float, h_cm: float, disposition: list, st0: float, st: float, st_max: float):
        """
        Dessine la coupe longitudinale avec la répartition des cadres.
        
        Args:
            l_m: Longueur en mètres
            h_cm: Hauteur en cm
            disposition: Liste des espacements
            st0: Espacement initial
            st: Espacement calculé
            st_max: Espacement maximal
        """
        self.scene.clear()
        
        l_cm = l_m * 100
        self.scale = min(900 / l_cm, 150 / h_cm)
        
        # Béton (contour)
        concrete_rect = QGraphicsRectItem(0, 0, l_cm * self.scale, h_cm * self.scale)
        concrete_brush = QBrush(QColor(240, 240, 245))
        concrete_pen = QPen(QColor(50, 50, 100), 2)
        concrete_rect.setBrush(concrete_brush)
        concrete_rect.setPen(concrete_pen)
        self.scene.addItem(concrete_rect)
        
        # Axe de symétrie
        axe = QGraphicsLineItem(0, h_cm * self.scale / 2, l_cm * self.scale, h_cm * self.scale / 2)
        axe.setPen(QPen(QColor(150, 150, 150), 1, Qt.DashLine))
        self.scene.addItem(axe)
        
        # Répartition des cadres
        self._dessiner_cadres(disposition, l_cm, h_cm)
        
        # Ã‰tiquettes
        self._ajouter_etiquettes(l_m, h_cm, st0, st, st_max)
        
    def _dessiner_cadres(self, disposition: list, l_cm: float, h_cm: float):
        """Dessine les cadres (sections transversales) le long de la poutre."""
        x = 0  # Position actuelle en cm
        
        for i, espacement in enumerate(disposition):
            if x >= l_cm:
                break
            
            # Petite ligne représentant le cadre
            line = QGraphicsLineItem(
                x * self.scale,
                (h_cm/2 - 2) * self.scale,
                x * self.scale,
                (h_cm/2 + 2) * self.scale
            )
            
            # Couleur selon la position
            if i == 0:
                color = QColor(220, 20, 60)  # Crimson pour St0
                line.setPen(QPen(color, 3))
            elif espacement == int(espacement):
                color = QColor(30, 144, 255)  # Bleu pour les espacements réguliers
                line.setPen(QPen(color, 2))
            else:
                color = QColor(100, 149, 237)  # Bleu pÃ¢le
                line.setPen(QPen(color, 1.5))
            
            self.scene.addItem(line)
            
            # Avancer de l'espacement
            x += espacement
        
        # Lignes des parois
        line_top = QGraphicsLineItem(0, 0, l_cm * self.scale, 0)
        line_top.setPen(QPen(QColor(50, 50, 100), 2))
        self.scene.addItem(line_top)
        
        line_bottom = QGraphicsLineItem(0, h_cm * self.scale, l_cm * self.scale, h_cm * self.scale)
        line_bottom.setPen(QPen(QColor(50, 50, 100), 2))
        self.scene.addItem(line_bottom)
    
    def _ajouter_etiquettes(self, l_m: float, h_cm: float, st0: float, st: float, st_max: float):
        """Ajoute les étiquettes informatifs."""
        info_lines = [
            f"Longueur: {l_m:.2f} m",
            f"Stâ‚€ (initial): {st0:.1f} cm",
            f"St (calculé): {st:.1f} cm",
            f"St_max: {st_max:.1f} cm"
        ]
        
        y_offset = 20
        for i, text_str in enumerate(info_lines):
            text_item = QGraphicsTextItem(text_str)
            text_item.setFont(QFont("Arial", 9))
            text_item.setPos(10, y_offset + i * 18)
            self.scene.addItem(text_item)
        
        # Légende des couleurs
        legend_y = y_offset + len(info_lines) * 20
        
        # St0
        legend_st0 = QGraphicsLineItem(10, legend_y + 10, 25, legend_y + 10)
        legend_st0.setPen(QPen(QColor(220, 20, 60), 3))
        self.scene.addItem(legend_st0)
        
        text_st0 = QGraphicsTextItem("= Premier espacement")
        text_st0.setFont(QFont("Arial", 8))
        text_st0.setPos(30, legend_y + 5)
        self.scene.addItem(text_st0)
        
        # St régulier
        legend_st = QGraphicsLineItem(10, legend_y + 30, 25, legend_y + 30)
        legend_st.setPen(QPen(QColor(30, 144, 255), 2))
        self.scene.addItem(legend_st)
        
        text_st = QGraphicsTextItem("= Espacement régulier")
        text_st.setFont(QFont("Arial", 8))
        text_st.setPos(30, legend_y + 25)
        self.scene.addItem(text_st)

