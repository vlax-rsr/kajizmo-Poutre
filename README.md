# KAJIZMO — POUTRE

Application de bureau pour le **dimensionnement des poutres en béton armé** selon les règles **BAEL 91**.  
Interface graphique développée avec **PySide6**, moteur de calcul entièrement en Python.

---

## Fonctionnalités

- **Ferraillage longitudinal** — calcul à l'ELU et à l'ELS (section simple ou doublement armée)
- **Ferraillage transversal** — dimensionnement des cadres et étriers, séquence de répartition (méthode de Caquot)
- **Vérification du cisaillement** — contrainte τ_u vs τ_lim
- **Vérification de la flèche** — conditions forfaitaires BAEL
- **Sélection des armatures réelles** — combinaison de barres HA avec vérification de la section réelle vs théorique
- **Export TXT** — génération d'une note de calcul technique complète et formatée

---

## Architecture du projet

```
kajizmo/
├── src/
│   ├── models/
│   │   ├── engine.py              # Dataclass Poutre — cœur du moteur de calcul
│   │   ├── longitudinal.py        # Ferraillage longitudinal (ELU + ELS)
│   │   ├── cisaillement.py        # Vérification cisaillement
│   │   ├── transversal.py         # Ferraillage transversal + disposition
│   │   ├── fleche.py              # Vérification des flèches
│   │   ├── formatting.py          # Mise en forme textuelle des résultats
│   │   ├── constant.py            # Constantes réglementaires BAEL
│   │   └── exceptions.py          # Exceptions métier personnalisées
│   ├── views/
│   │   ├── main_view.py           # Chargement de l'UI Qt et gestion des widgets
│   │   ├── console_view.py        # Mise à jour des zones de texte Qt
│   │   └── kajizmo_interface.ui   # Fichier d'interface Qt Designer
│   ├── controllers/
│   │   ├── main_controller.py     # Orchestrateur principal — signaux et workflows
│   │   ├── calculation_coordinator.py  # Coordinateur des calculs métier
│   │   ├── input_validators.py    # Validation des entrées utilisateur
│   │   ├── status_manager.py      # Gestion de la barre de statut
│   │   └── ui_helpers.py          # Helpers de mise à jour de l'interface
│   └── utils.py                   # Utilitaires (safe_float, etc.)
├── assets/
│   └── icons/                     # Icônes de l'application
├── main.py                        # Point d'entrée de l'application
└── README.md
```

---

## Données d'entrée

| Paramètre | Description | Unité |
|---|---|---|
| b | Largeur de la section | cm |
| h | Hauteur de la section | cm |
| L | Portée de la poutre | m |
| f_c28 | Résistance caractéristique du béton | MPa |
| f_e | Limite élastique de l'acier | MPa |
| Classe de fissuration | FPP / FP / FTP | — |
| M_u | Moment fléchissant ultime | kN·m |
| M_ser | Moment de service | kN·m |
| V_u | Effort tranchant ultime | kN |

> FPP : Fissuration peu préjudiciable
> FP : Fissuration préjudiciable
> FTP : Fissuration très préjudiciable

---

## Résultats produits

**Ferraillage longitudinal**
- Moment réduit μ et μ_lim → configuration simple ou double armature
- Section théorique A_t (aciers tendus) et A_c (aciers comprimés) à l'ELU et à l'ELS
- Section retenue finale, vérification A_min et A_max

**Ferraillage transversal**
- Espacement initial S_t0, espacement calculé S_t, espacement maximal S_tmax
- Répartition des cadres sur la demi-portée (séquence de Caquot)

**Vérifications réglementaires**
- Cisaillement : τ_u ≤ τ_lim
- Flèche : f ≤ f_lim

---

## Installation

### Prérequis

- Python 3.10+
- PySide6

### Dépendances

```bash
pip install PySide6
```

### Lancement en mode développement

```bash
python main.py
```

### Compilation en exécutable (PyInstaller)

```bash
pyinstaller --onefile --windowed --add-data "src/views/kajizmo_interface.ui;src/views" --add-data "assets;assets" main.py
```

> L'application gère automatiquement les chemins de ressources selon l'environnement (développement ou exécutable PyInstaller) via la fonction `resource_path`.

---

## Normes de référence

- **BAEL 91 révisé 99** — Règles techniques de conception et de calcul des ouvrages et constructions en béton armé suivant la méthode des états limites

---

## Licence

Projet privé — tous droits réservés.
