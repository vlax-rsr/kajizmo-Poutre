# views/console_views.py

from src.models.engine import Poutre
from collections import Counter
from PySide6.QtWidgets import QTextBrowser, QLabel
from src.models.fleche import *

def qtext_long(poutre: Poutre, widget: QTextBrowser):
    arm_long = poutre.calculer_ferraillage_longitudinal()
    lignes = [
            "<b>Résultats des calculs:</b><br>",
            f"Section minimale : <b>{arm_long['A_min_cm2']:.2f} cm²</b>",
            f"Section maximale : <b>{arm_long['A_max_cm2']:.2f} cm²</b>"]
    if arm_long["arm_comp"]:
        lignes.append(f"Section d'armature comprimée : <b>{arm_long['A_c_final_cm2']:.2f} cm²</b>")
    if widget:
        widget.setText("<br>".join(lignes))

def qtext_fleche(poutre: Poutre, widget: QLabel):
    res_fleche = poutre.verifier_fleche()
    if widget:
        widget.setText(f"flim = {res_fleche['f_lim_cm']:.2f}<br>Flèche calculée f : {res_fleche['f_cm']:.2f}")

def qtext_trans(poutre: Poutre, widget: QTextBrowser, nb_brin: int, phi_t: int):
    res_trans = poutre.calculer_ferraillage_transversale(nb_brin= nb_brin, phi_t= phi_t)

    compte = Counter(res_trans["disposition"])
    mon_dict = {
        str(int(k) if isinstance(k, (int, float)) and k.is_integer() else k): v
        for k, v in compte.items()
    }

    txt_rep = ["<b>Répartition des cadres:</b>"]
    for key, value in mon_dict.items():
        txt_rep.append(f"•  {value}x{key}")

    lignes = [
        "<b>Résultats des calculs:</b>",
        f"Espacement initial S₀ : {res_trans.get('st0', 0):.2f} cm",
        f"Espacement calculé St : {res_trans.get('st', 0):.2f} cm",
        f"Espacement maximal Sₘₐₓ : {res_trans.get('st_max', 0):.2f} cm",
        ""
    ]
    
    lignes.extend(txt_rep)
    if widget:
        widget.setText("<br>".join(lignes))
