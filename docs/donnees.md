# Données utilisées

## Émetteurs : ANFR

**Jeu de données** : [Données sur les installations radioélectriques de plus de 5 watts](https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1), Agence nationale des fréquences, publié sur data.gouv.fr. Il est mis à jour chaque mois, sous Licence Ouverte 2.0.

**Export utilisé** : celui du **30 septembre 2026**, publié le 6 octobre 2026.

**Tables utilisées** (fichiers `.txt`, séparateur `;`, encodage latin-1) :

| Table | Champs utilisés |
|---|---|
| `SUP_EMETTEUR` | `EMR_ID`, `EMR_LB_SYSTEME` (filtre `FM` et `RDF T-DAB`), `STA_NM_ANFR`, `AER_ID` |
| `SUP_ANTENNE` | `AER_ID`, `SUP_ID`, `AER_NB_ALT_BAS` (hauteur du bas de l'antenne au-dessus du sol) |
| `SUP_SUPPORT` | coordonnées en degrés-minutes-secondes, `COM_CD_INSEE`, `ADR_LB_LIEU`, `SUP_NM_HAUT` |
| `SUP_STATION` | `ADM_ID` (exploitant : TDF, Towercast, site privé…) |

**Extraction** : le script `scripts/extraire_emetteurs.py` produit `data/emetteurs.js`. Il contient 4 666 supports portant au moins un émetteur FM ou DAB+, soit 10 871 émetteurs FM et 1 106 émetteurs DAB+.

**Ce que le jeu de données ne contient pas** :
- **La fréquence exacte.** La table des bandes (`SUP_BANDE`) indique 87,5–108 MHz pour la quasi-totalité des émetteurs FM et 174–223 MHz pour le DAB+.
- **Le nom du programme diffusé.**
- **La puissance rayonnée et le diagramme d'antenne.**
- **La zone de couverture.**

## Communes : geo.api.gouv.fr

La liste des communes vient de `https://geo.api.gouv.fr/communes` (nom, code INSEE, codes postaux). Elle sert uniquement à nommer la commune de chaque site d'émission. Les arrondissements de Paris, Lyon et Marseille, absents de cette liste, sont nommés par la page elle-même.

## Données IGN interrogées en direct

La page interroge la Géoplateforme (`https://data.geopf.fr`). Ces services autorisent les appels depuis n'importe quel site (CORS ouvert).

| Usage | Service | Détail |
|---|---|---|
| Autocomplétion d'adresse | `/geocodage/completion` | types `StreetAddress,PositionOfInterest` |
| Profil du relief | `/altimetrie/1.0/calcul/alti/rest/elevationLine.json` | ressource `ign_rge_alti_wld` (RGE ALTI, modèle numérique de **terrain**, sans bâtiments ni végétation) |
| Bâtiments | `/wfs`, type `BDTOPO_V3:batiment` | propriétés `hauteur`, `nombre_d_etages`, `altitude_minimale_sol`, `altitude_maximale_toit` et géométrie ; filtre `DWITHIN` de 350 m |
| Fond de carte | styles de Carte facile | style `desaturated` (données IGN), bâtiments du fond masqués au profit de la couche BD TOPO en 3D |

L'adresse saisie par l'utilisateur est envoyée au service de géocodage de l'IGN, et les coordonnées du point aux autres services. Aucune autre donnée ne quitte le navigateur.

## Bibliothèques

| Bibliothèque | Version | Chargement |
|---|---|---|
| [MapLibre GL JS](https://maplibre.org/) | 6.11.2 | unpkg, via une import map |
| [Carte facile](https://fab-geocommuns.github.io/carte-facile-site/) | 0.10.2 | unpkg, via une import map |
| Polices Barlow Semi Condensed, Source Sans 3, IBM Plex Mono | — | Google Fonts |

Le moteur de MapLibre (son *worker*) est lancé à partir d'une petite URL `blob:` qui importe le fichier depuis unpkg. Ce détour permet à la carte de fonctionner quel que soit le domaine d'hébergement.

## Licences

- **ANFR** : Licence Ouverte 2.0. La mention de la source suffit.
- **IGN** : Géoplateforme, BD TOPO et RGE ALTI sont diffusés en données ouvertes (Licence Ouverte Etalab 2.0). Le fond Plan IGN et les styles de Carte facile sont soumis à leurs propres conditions, à vérifier sur leurs sites respectifs.
- **MapLibre GL JS** : licence BSD-3-Clause.
- **Code de ce dépôt** : *aucune licence n'est encore choisie* (voir [incertitudes.md](incertitudes.md#7-questions-de-projet)).
