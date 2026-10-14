# Mettre à jour les données

L'ANFR publie un nouvel export chaque mois, en général dans la première semaine. Pour que l'outil suive les réattributions de fréquences, il faut régénérer `data/emetteurs.js` puis `index.html`.

## Prérequis

Python 3.9 ou plus récent. Aucune dépendance externe : les scripts n'utilisent que la bibliothèque standard.

## Procédure

```bash
# 1. Télécharger l'export ANFR le plus récent et la liste des communes (dans sources/, ignoré par git)
python3 scripts/telecharger_donnees.py

# 2. Extraire les sites FM et DAB+
python3 scripts/extraire_emetteurs.py sources/anfr-AAAAMMJJ sources/communes.json data/emetteurs.js

# 3. Reconstruire la page
python3 scripts/assembler_page.py

# 4. Vérifier localement, puis publier
python3 -m http.server 8000
```

Remplacez `AAAAMMJJ` par la date du dossier créé à l'étape 1 (par exemple `anfr-20260930`).

**Pensez aussi à mettre à jour :**
- la date de l'export citée dans `src/page.html` (volet « Données et hypothèses ») ;
- la date de l'export dans [donnees.md](donnees.md).

## Comparer deux exports

Pour suivre l'évolution du parc d'émetteurs (retraits FM, déploiement du DAB+) :

```bash
python3 scripts/telecharger_donnees.py --mois "juin 2026"
python3 scripts/telecharger_donnees.py            # le plus récent
python3 scripts/comparer_exports.py sources/anfr-20260630 sources/anfr-20260930 analyses/comparaison.csv
```

Le script affiche les totaux et écrit la liste détaillée des émetteurs retirés ou ajoutés. Ses limites sont décrites dans [incertitudes.md](incertitudes.md#5-comparaison-des-exports-anfr).

## Automatiser

Les étapes 1 à 3 pourraient tourner chaque mois dans une action GitHub planifiée, qui ouvrirait une *pull request* pour relecture. Cette automatisation n'est pas encore en place.
