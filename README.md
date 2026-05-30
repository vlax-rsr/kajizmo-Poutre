# 🏗️ KAJIZMO — POUTRE

> Application de bureau pour le **dimensionnement des poutres en béton armé** selon les règles **BAEL 91 révisé 99**.  
> Interface graphique **PySide6** · Moteur de calcul entièrement en **Python**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=flat-square&logo=qt&logoColor=white)
![Norme](https://img.shields.io/badge/Norme-BAEL%2091%20rév.%2099-E8A020?style=flat-square)
![Licence](https://img.shields.io/badge/Licence-Privée-red?style=flat-square)

---

## 🎯 Objectif

Kajizmo — Poutre est un outil de calcul réglementaire destiné aux ingénieurs en génie civil. Il automatise le dimensionnement complet d'une poutre en béton armé (ferraillage longitudinal, transversal, vérifications ELU/ELS) selon la méthode des états limites du BAEL 91.

---

## ✅ Fonctionnalités

| Module | Description | État |
|--------|-------------|:----:|
| **Ferraillage longitudinal** | Calcul ELU + ELS, section simple ou doublement armée | ✅ |
| **Ferraillage transversal** | Dimensionnement des cadres et étriers, séquence de Caquot | ✅ |
| **Vérification cisaillement** | Contrainte τ_u vs τ_lim selon classe de fissuration | ✅ |
| **Vérification flèche** | Conditions forfaitaires BAEL, f ≤ f_lim | ✅ |
| **Armatures réelles** | Combinaison de barres HA, vérification A_réel ≥ A_théorique | ✅ |
| **Export TXT** | Note de calcul technique complète et formatée | ✅ |

---

## 📦 Architecture du projet

```
kajizmo/
├── src/
│   ├── models/                         🧮 Moteur de calcul
│   │   ├── engine.py                   # Dataclass Poutre — cœur du moteur
│   │   ├── longitudinal.py             # Ferraillage longitudinal (ELU + ELS)
│   │   ├── cisaillement.py             # Vérification cisaillement
│   │   ├── transversal.py              # Ferraillage transversal + disposition
│   │   ├── fleche.py                   # Vérification des flèches
│   │   ├── formatting.py               # Mise en forme des résultats
│   │   ├── constant.py                 # Constantes réglementaires BAEL
│   │   └── exceptions.py              # Exceptions métier personnalisées
│   │
│   ├── views/                          🖥️  Interface graphique
│   │   ├── main_view.py                # Chargement UI Qt + gestion widgets
│   │   ├── console_view.py             # Mise à jour des zones de texte Qt
│   │   └── kajizmo_interface.ui        # Fichier Qt Designer
│   │
│   ├── controllers/                    🎮 Orchestration
│   │   ├── main_controller.py          # Orchestrateur principal
│   │   ├── calculation_coordinator.py  # Coordinateur des calculs
│   │   ├── input_validators.py         # Validation des entrées
│   │   ├── status_manager.py           # Gestion barre de statut
│   │   └── ui_helpers.py              # Helpers de mise à jour UI
│   │
│   └── utils.py                        # Utilitaires (safe_float, etc.)
│
├── assets/
│   └── icons/                          🎨 Icônes de l'application
├── main.py                             # Point d'entrée
└── README.md
```

---

## 📊 Données d'entrée

### Géométrie & Matériaux

| Paramètre | Description | Unité |
|-----------|-------------|:-----:|
| `b` | Largeur de la section | cm |
| `h` | Hauteur de la section | cm |
| `L` | Portée de la poutre | m |
| `f_c28` | Résistance caractéristique du béton | MPa |
| `f_e` | Limite élastique de l'acier | MPa |
| Classe de fissuration | `FPP` / `FP` / `FTP` | — |

> FPP : Fissuration peu préjudiciable
> FP : Fissuration préjudiciable
> FTP : Fissuration très préjudiciable

### Sollicitations

| Paramètre | Description | Unité |
|-----------|-------------|:-----:|
| `M_u` | Moment fléchissant ultime | kN·m |
| `M_ser` | Moment de service | kN·m |
| `V_u` | Effort tranchant ultime | kN |

---

## 📈 Résultats produits

### 🔩 Ferraillage longitudinal
- Moment réduit **μ** vs **μ_lim** → configuration simple ou double armature
- Section théorique **A_t** (aciers tendus) et **A_c** (aciers comprimés) à l'ELU et à l'ELS
- Section finale retenue, vérification **A_min** et **A_max**

### 🔗 Ferraillage transversal
- Espacements **S_t0**, **S_t**, **S_tmax**
- Répartition des cadres sur la demi-portée (séquence de Caquot)

### ✔️ Vérifications réglementaires

| Vérification | Condition | Statut |
|-------------|-----------|:------:|
| Cisaillement | τ_u ≤ τ_lim | ✅ / ❌ |
| Flèche | f ≤ f_lim | ✅ / ❌ |
| Section réelle | A_réel ≥ A_théorique | ✅ / ❌ |

---

## 🚀 Installation

### Prérequis

- 🐍 Python **3.10+**
- 🖼️ PySide6

### Étape 1 — Cloner le dépôt

```bash
git clone https://github.com/votre-org/kajizmo-poutre.git
cd kajizmo-poutre
```

### Étape 2 — Installer les dépendances

```bash
pip install PySide6
```

### Étape 3 — Lancer l'application

```bash
python main.py
```

### Étape 4 — Compilation en exécutable *(optionnel)*

```bash
pyinstaller --onefile --windowed \
  --add-data "src/views/kajizmo_interface.ui;src/views" \
  --add-data "assets;assets" \
  main.py
```

> 💡 La fonction `resource_path()` gère automatiquement la résolution des chemins en mode développement ou bundle PyInstaller.

---

## 🏛️ Norme de référence

**BAEL 91 révisé 99** — *Règles techniques de conception et de calcul des ouvrages et constructions en béton armé suivant la méthode des états limites.*  
Ministère de l'Équipement, du Logement et des Transports, France.

---

## 🔐 Sécurité & confidentialité

- ✅ Aucun accès réseau
- ✅ Aucune transmission de données
- ✅ Calculs strictement locaux
- ✅ Compatible 100% hors-ligne
- ✅ Logs locaux uniquement

---

## 📋 Checklist de mise en production

- [ ] Dépendances installées (`pip install PySide6`)
- [ ] Fichier `.ui` accessible via `resource_path`
- [ ] Icônes présentes dans `assets/icons/`
- [ ] Test calcul longitudinal
- [ ] Test calcul transversal
- [ ] Test export TXT
- [ ] Compilation PyInstaller vérifiée

---

## 📄 Licence

Projet privé — tous droits réservés.
