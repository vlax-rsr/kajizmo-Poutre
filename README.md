# Kajizmo - Poutre BA

Application desktop Python (PySide6) pour le dimensionnement de poutres en béton armé selon le BAEL 91 mod. 99.

## Aperçu

Kajizmo permet de :
- Saisir la géométrie de la poutre,
- Définir les matériaux (béton, acier, fissuration),
- Saisir les sollicitations (ELU / ELS),
- Calculer les armatures longitudinales,
- Vérifier le cisaillement et la flèche,
- Calculer les armatures transversales,
- Comparer section théorique et section réelle choisie.

## Fonctionnalités

- Interface graphique PySide6 chargée depuis un fichier `.ui`
- Architecture MVC (`models/`, `views/`, `controllers/`)
- Validation des entrées utilisateur
- Feedback visuel (styles warning/erreur/succès + barre de statut)
- Journalisation dans `kajizmo.log`
- Compatibilité exécutable (PyInstaller)

## Structure du projet

```text
.
├── main.py
├── config.py
├── src/
│   ├── controllers/
│   ├── models/
│   └── views/
├── assets/
│   ├── icons/
│   └── styles/
├── requirements.txt
└── pyproject.toml
```

## Prérequis

- Python 3.10+
- Windows recommandé (développé et packagé côté Windows)

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
python main.py
```

## Flux d'utilisation

1. Renseigner les données d'entrée (géométrie, matériaux, sollicitations).
2. Cliquer sur **Calcul des armatures longitudinales**.
3. Lire les résultats (section retenue, cisaillement, flèche).
4. Choisir la composition réelle des barres pour comparer à la section théorique.
5. Remplir le nombre de brins et choisir le diamètre des cadres.
6. Cliquer sur **Calcul des armatures transversales**.
7. Utiliser **Réinitialiser** pour repartir de zéro.

## Modules clés

- `main.py` : point d'entrée, chargement style, logging.
- `src/controllers/main_controller.py` : orchestration UI ↔ calcul.
- `src/controllers/calculation_coordinator.py` : coordination des calculs métier.
- `src/models/engine.py` : classe `Poutre` et logique principale BAEL.
- `src/views/main_view.py` : chargement UI, widgets, validateurs.
- `assets/styles/stylesheet_enhanced.css` : thème visuel.

## Tests rapides

Un script d'exemple existe :

```bash
python test_engine.py
```

Il exécute un cas type sur le moteur de calcul (`Poutre`) et affiche les sorties en console.

## Logs

Les logs applicatifs sont écrits dans :

- `kajizmo.log`

## Packaging (PyInstaller)

Des fichiers `.spec` sont présents :
- `main.spec`
- `kajizmo - Poutre.spec`

Ils servent à générer un exécutable desktop.

## Licence

Projet sous licence MIT. Voir `LICENSE`.
