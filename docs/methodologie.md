# Méthode de calcul

Ce document décrit précisément ce que calcule la page. Le code correspondant se trouve dans `src/page.html`, aux sections « Choix des sites », « Analyse » et « Diagnostic en clair ».

## Vue d'ensemble

```
adresse + étage
   │
   ├─ géocodage (IGN) ──────────────► point (lon, lat)
   │
   ├─ sélection des sites ANFR ─────► jusqu'à 6 sites FM/DAB+ à moins de 50 km
   │
   ├─ pour chaque site :
   │     profil du relief (RGE ALTI) ─► obstacle de relief le plus pénalisant
   │     bâtiments ≤ 350 m (BD TOPO) ─► obstacle bâti le plus pénalisant
   │     → atténuation relief + bâti, en FM et en DAB+
   │
   └─ verdict en clair à partir du site DAB+ le plus favorable
```

## 1. Géocodage

L'adresse est géocodée par le service d'autocomplétion de la Géoplateforme (`/geocodage/completion`, types `StreetAddress` et `PositionOfInterest`). Le point obtenu sert d'emplacement d'écoute.

L'altitude du sol au point d'écoute est la première valeur du profil de relief (RGE ALTI).

## 2. Sélection des sites d'émission

On part des 4 666 supports portant au moins un émetteur FM ou DAB+ dans l'export ANFR (voir [donnees.md](donnees.md)).

1. **Regroupement** : les supports distants de moins de 300 m sont fusionnés en un seul site, car plusieurs pylônes sont souvent installés sur un même point haut. Les nombres d'émetteurs s'additionnent, et on garde la hauteur d'antenne maximale.
2. **Filtre** : seuls les sites situés entre 50 m et 50 km de l'adresse sont retenus.
3. **Score** de chaque site :

   ```
   score   = (nb_FM + nb_DAB) × √max(hauteur_antenne, 5) / (distance_km + 2)²
   score_DAB = nb_DAB × √max(hauteur_antenne, 5) / (distance_km + 2)²
   ```

4. **Retenus** : les 4 meilleurs sites selon `score`, plus les 3 meilleurs selon `score_DAB`, sans doublon. On garde donc jusqu'à 6 sites, triés par distance.

Ce score est une heuristique. Il favorise les sites importants (beaucoup d'émetteurs, antennes hautes) et proches, faute de connaître la puissance réelle des émetteurs.

## 3. Hauteurs

| Grandeur | Valeur |
|---|---|
| Hauteur d'écoute | sol + étage × 3,0 m + 1,2 m |
| Altitude de l'antenne | altitude du sol au pied du support (RGE ALTI) + hauteur d'antenne ANFR |
| Toit d'un bâtiment | `altitude_maximale_toit` de la BD TOPO, ou à défaut `altitude_minimale_sol + hauteur` |

## 4. Atténuation due au relief

Le profil est échantillonné entre 60 et 200 points (un point tous les 40 m environ) par le service `elevationLine` de la Géoplateforme, avec la ressource `ign_rge_alti_wld`.

À chaque point du profil situé à plus de 350 m de l'adresse et à plus de 50 m de l'antenne :

1. on ajoute le renflement de la Terre, avec un rayon terrestre effectif k = 4/3 : `d1·d2 / (2·R·k)` ;
2. on calcule la hauteur `h` du terrain au-dessus de la ligne droite qui relie l'auditeur à l'antenne ;
3. on calcule le paramètre de diffraction de Fresnel-Kirchhoff : `v = h · √(2·D / (λ·d1·d2))`.

On retient le point où `v` est maximal (obstacle unique). L'atténuation suit la formule de la recommandation UIT-R P.526 :

```
J(v) = 0                                          si v ≤ −0,78
J(v) = 6,9 + 20·log10( √((v−0,1)² + 1) + v − 0,1 )   sinon   (en dB)
```

Les longueurs d'onde utilisées sont λ = 3 m pour la FM (environ 100 MHz) et λ = 1,5 m pour le DAB+ (environ 200 MHz, bande III).

## 5. Atténuation due aux bâtiments voisins

1. **Collecte** : les bâtiments situés à moins de 350 m de l'adresse sont récupérés par le service WFS de la Géoplateforme (`BDTOPO_V3:batiment`, filtre `DWITHIN`).
2. **Bâtiment de l'adresse** : ceux à moins de 5 m du point d'adresse sont considérés comme l'immeuble du logement ou un mitoyen, et sont ignorés.
3. **Traversées** : pour chaque site, on trace une demi-droite depuis l'adresse dans la direction de l'émetteur. On repère les bâtiments qu'elle traverse, avec leur distance d'entrée et de sortie.
4. **Diffraction** : chaque arête de toit traversée est traitée comme une lame de couteau, avec la même formule `J(v)` que pour le relief. On retient la plus pénalisante.
5. **Plafond** : l'atténuation due au bâti est plafonnée à **20 dB**. En ville, les réflexions sur les façades et la diffraction latérale ramènent du signal que le modèle à obstacle unique ignore. Ce plafond est un choix de modélisation (voir [incertitudes.md](incertitudes.md)).

Atténuation totale d'un site = relief + bâti (plafonné).

## 6. Du chiffre au verdict

Pour chaque site, on calcule un **indice d'effort** qui combine le masquage et l'éloignement :

```
effort = atténuation_totale + 20·log10( max(distance_km, 1) / 5 )
```

Le terme de distance applique une pénalité de 20 dB par décade, à partir de 5 km.

**Verdict DAB+.** On prend le site DAB+ qui a l'effort le plus faible :

| Effort DAB+ | Verdict affiché |
|---|---|
| ≤ 16 | Oui, très probablement |
| ≤ 28 | Oui, probablement |
| ≤ 38 | C'est incertain |
| > 38 | Difficilement |

**Cas sans DAB+.** Si aucun site DAB+ n'est retenu à moins de 50 km, le verdict est « Probablement pas en DAB+ ».

**Verdict FM.** Il utilise les mêmes paliers décalés de 8 dB : bonne ≤ 24, correcte ≤ 36, fragile ≤ 46, difficile au-delà. La FM se dégrade en effet progressivement (souffle, passage en mono), et ses émetteurs principaux sont en général puissants.

**Conseils affichés.** Ils sont déduits du calcul :
- direction de l'émetteur le plus favorable ;
- gain ou perte si l'on monte ou descend de trois étages ;
- suggestion d'une antenne extérieure quand le verdict est « incertain » ou « difficile ».

**Ces seuils ne sont pas calibrés sur des mesures.** Ils ont été fixés de façon à donner des résultats vraisemblables sur quelques adresses tests : Nantes centre au rez-de-chaussée, Saint-Flour, Paris 4ᵉ. C'est la principale incertitude du projet : voir [incertitudes.md](incertitudes.md#2-seuils-non-calibrés).

## 7. Changement d'étage

Le relief, les bâtiments et les profils ne sont téléchargés qu'une fois par adresse. Changer d'étage relance seulement le calcul local, qui est instantané. Pour chaque site, l'outil calcule l'étage courant, le rez-de-chaussée et l'étage ± 3, afin de produire les comparaisons affichées.

## Paramètres

| Paramètre | Valeur | Où |
|---|---|---|
| Hauteur d'un niveau | 3,0 m | `FLOOR_H` |
| Hauteur d'écoute au-dessus du plancher | 1,2 m | `EAR` |
| Rayon de recherche des bâtiments | 350 m | `BUILD_R` |
| Distance « bâtiment de l'adresse » | 5 m | `OWN_R` |
| Plafond d'atténuation du bâti | 20 dB | `BUILD_CAP` |
| Rayon terrestre effectif | k = 4/3 | `RE` |
| Rayon de recherche des émetteurs | 50 km | `chooseSites` |
| Fusion des supports voisins | 300 m | `chooseSites` |
| Seuils DAB+ | 16 / 28 / 38 | `LEVELS` |
| Décalage FM | +8 dB | `FM_SHIFT` |
