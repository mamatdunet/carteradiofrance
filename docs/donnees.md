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
- **Le nom du programme ou du multiplex diffusé.** Pour le DAB+, il est reconstitué à partir des décisions de l'Arcom (section suivante).
- **La puissance rayonnée et le diagramme d'antenne.**
- **La zone de couverture.**

## Sites DAB+ de Radio France : décisions de l'Arcom relevées par dabplus.fr

L'ANFR ne dit pas quel multiplex passe par quel émetteur. Cette information figure dans les décisions de l'Arcom publiées au Journal officiel : autorisation de chaque multiplex, puis agrément de chaque site d'émission. Elle n'existe pas en données ouvertes structurées. Le site [dabplus.fr](https://www.dabplus.fr/), tenu par un particulier, la recopie zone par zone : radios de chaque multiplex, sites d'émission, puissance apparente rayonnée, altitude, hauteur d'antenne et lien vers la décision au Journal officiel.

**Ce qu'on en retient** (`scripts/extraire_multiplex.py` → `data/multiplex-radio-france.csv`) :
- le **multiplex métropolitain M2**, qui porte France Inter, franceinfo, France Culture, France Musique, FIP et Mouv'. En métropole, ces six radios ne passent en DAB+ que par ce multiplex ;
- les **multiplex locaux et étendus** qui portent une station **ICI** (ex-France Bleu).

Relevé d'octobre 2026 : 515 sites, dont 317 pour le M2. Chaque ligne cite la décision du Journal officiel correspondante, ce qui permet de la vérifier.

**Rattachement aux supports ANFR** (`scripts/extraire_emetteurs.py`). Chaque site de la liste est rattaché au support DAB+ de l'ANFR situé dans le même département et la même commune. Quand plusieurs supports conviennent, on départage par le diffuseur (TDF, towerCast), puis par les mots communs du lieu-dit. Des supports distants de moins de 1 km sont considérés comme un même site. Les communes nouvelles, les anciennes communes et les arrondissements de Paris, Lyon et Marseille sont gérés. Un seul rattachement est manuel (Cases-de-Pène → Baixas, documenté dans le script).

Résultat : 322 supports diffusent le M2 et 190 une station ICI. **7 sites sur 515 ne sont pas rattachés**, faute de support DAB+ déclaré à l'ANFR dans la commune : 2 sites M2 (Morêtel-de-Mailles, La Ferté-sous-Jouarre) et 5 sites de multiplex locaux. Le script les liste à chaque exécution.

**Licence** : dabplus.fr n'affiche pas de licence. Son fichier `robots.txt` autorise la réutilisation, y compris par des outils d'IA. Les informations reprises sont des faits publiés au Journal officiel. Le dépôt ne conserve pas les pages, seulement la liste des sites avec leur source.

## Fréquences remises en appel : Arcom

**Source** : [appel aux candidatures FM du 20 mai 2026](https://www.arcom.fr/vos-services-par-media/appel-candidatures/appel-aux-candidatures-fm-du-20-mai-2026-dans-le-ressort-des-comites-techniques-de-bordeaux-caen-clermont-ferrand-dijon-lille-lyon-marseille-nancy-paris-poitiers-rennes-et-toulouse), annexe de la décision (PDF). 31 fréquences dans 30 zones : 30 libérées par Mouv', qui a quitté la FM le 31 août 2026, et une d'une radio privée dont l'autorisation a été retirée. L'Arcom ne précise pas laquelle.

**Fichier** : `data/frequences-remises-en-appel-2026-05-20.csv`, recopié à la main de l'annexe (fréquence, zone, département, commune d'implantation, altitude maximale des antennes). L'Arcom ne publie pas l'emplacement exact des émetteurs : la carte place chaque fréquence au centre de sa commune d'implantation, dont les coordonnées ont été relevées une fois avec le géocodeur de l'IGN.

L'Arcom n'a pas publié la liste des quelque 300 autres fréquences rendues par Radio France en juillet 2026.

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
