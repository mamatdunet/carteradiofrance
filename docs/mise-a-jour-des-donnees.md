# Mettre à jour les données

L'ANFR publie un nouvel export chaque mois, en général dans la première semaine. Pour que l'outil suive les réattributions de fréquences, il faut régénérer `data/emetteurs.js` puis `index.html`. La liste des sites DAB+ de Radio France (dabplus.fr) se met à jour en même temps.

## Prérequis

Python 3.9 ou plus récent. Aucune dépendance externe : les scripts n'utilisent que la bibliothèque standard.

## Procédure

```bash
# 1. Télécharger l'export ANFR le plus récent, la liste des communes et les pages de dabplus.fr
#    (dans sources/, ignoré par git)
python3 scripts/telecharger_donnees.py

# 2. Lister les sites DAB+ qui diffusent Radio France
python3 scripts/extraire_multiplex.py sources/dabplus data/multiplex-radio-france.csv

# 3. Extraire les sites FM et DAB+, et leur rattacher les multiplex de Radio France
python3 scripts/extraire_emetteurs.py sources/anfr-AAAAMMJJ sources/communes.json data/emetteurs.js data/multiplex-radio-france.csv

# 4. Reconstruire la page
python3 scripts/assembler_page.py

# 5. Vérifier localement, puis publier
python3 -m http.server 8000
```

Remplacez `AAAAMMJJ` par la date du dossier créé à l'étape 1 (par exemple `anfr-20260930`).

L'étape 3 liste les sites de Radio France qu'elle n'a pas pu rattacher à un support ANFR. Si un nouveau site M2 y apparaît, vérifiez sa commune dans l'export ANFR. Au besoin, ajoutez un rattachement manuel dans `MANUEL` (`scripts/extraire_emetteurs.py`).

**Pensez aussi à mettre à jour :**
- la date de l'export et celle du relevé dabplus.fr citées dans `src/page.html` (volet « Données et hypothèses ») ;
- les mêmes dates et les décomptes dans [donnees.md](donnees.md).

## Comparer deux exports

Pour suivre l'évolution du parc d'émetteurs (retraits FM, déploiement du DAB+) :

```bash
python3 scripts/telecharger_donnees.py --mois "juin 2026"
python3 scripts/telecharger_donnees.py            # le plus récent
python3 scripts/comparer_exports.py sources/anfr-20260630 sources/anfr-20260930 analyses/comparaison.csv
```

Le script affiche les totaux et écrit la liste détaillée des émetteurs retirés ou ajoutés. Ses limites sont décrites dans [incertitudes.md](incertitudes.md#5-comparaison-des-exports-anfr).

## Automatiser

Les étapes 1 à 4 pourraient tourner chaque mois dans une action GitHub planifiée, qui ouvrirait une *pull request* pour relecture. Cette automatisation n'est pas encore en place.
