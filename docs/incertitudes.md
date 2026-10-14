# Incertitudes et limites connues

Cet outil est un **prototype**. Ce document liste, aussi honnêtement que possible, ce qui reste incertain. Pour chaque point, il indique l'effet probable sur le verdict et les pistes pour réduire l'incertitude.

Les points sont classés par impact décroissant sur la fiabilité du verdict.

---

## 1. Ce que les données ouvertes ne disent pas

### Puissance des émetteurs inconnue — impact : **fort**
L'ANFR ne publie ni la puissance apparente rayonnée (PAR) ni le diagramme d'antenne. Un relais FM de quelques watts et un grand site de plusieurs kilowatts sont donc traités presque pareil : seuls le nombre d'émetteurs et la hauteur d'antenne départagent les sites. Le verdict mesure un **masquage**, pas un niveau de champ réel.

*Effet* : un petit relais proche peut être jugé « favorable » alors qu'il est trop faible. À l'inverse, un site très puissant mais lointain peut être sous-estimé.

*Pistes* : récupérer les puissances autorisées. Elles figurent dans les décisions d'autorisation de l'Arcom, publiées en PDF. On pourrait aussi demander à l'Arcom ou à l'ANFR un export structuré, ou intégrer une estimation par catégorie de site.

### Radios portées par chaque émetteur : reconstituées pour le DAB+, inconnues en FM — impact : **moyen**
L'ANFR ne publie ni le nom du programme ni la fréquence exacte. Pour le DAB+, l'outil reconstitue l'information : il sait quels sites diffusent le multiplex national M2 (France Inter, franceinfo, France Culture, France Musique, FIP, Mouv') et les stations ICI, d'après les décisions de l'Arcom relevées par dabplus.fr (voir [donnees.md](donnees.md#sites-dab-de-radio-france--décisions-de-larcom-relevées-par-dabplusfr)). Le verdict DAB+ porte donc bien sur Radio France.

Restent incertains :
- **le rattachement** des sites de la liste aux supports ANFR, fait par commune. Il peut se tromper de support quand plusieurs sites DAB+ existent dans une même commune à plus de 1 km l'un de l'autre. 7 sites sur 515 ne sont pas rattachés, dont 2 sites M2 ;
- **la fraîcheur** de la liste : dabplus.fr est tenu à jour par un particulier, et le M2 s'étend plusieurs fois par an. Un site récent peut manquer. L'outil répondrait alors « probablement pas » à tort ;
- **la FM** : on ne sait toujours pas quelles radios passent par quel émetteur FM.

*Pistes* :
- obtenir de l'Arcom ou de Radio France un export structuré (site, multiplex, coordonnées), qui supprimerait le rattachement par commune ;
- pour la FM, demander à Radio France la liste de ses fréquences par site : son moteur de recherche n'est pas en open data ;
- la puissance apparente rayonnée figure dans la même liste : elle pourrait servir dans le calcul (voir le point précédent).

### Pas de zone de couverture officielle
Les cartes de couverture DAB+ de l'Arcom et des opérateurs, quand elles existent, ne sont pas disponibles en données ouvertes exploitables. Il est donc impossible de vérifier l'outil contre une référence.

---

## 2. Seuils non calibrés

### Les paliers du verdict sont fixés à la main — impact : **fort**
Les seuils DAB+ (16 / 28 / 38) et le décalage FM (+8 dB) ont été choisis pour donner des résultats vraisemblables sur trois adresses tests. Ils **n'ont pas été confrontés à des mesures ni à des retours d'utilisateurs**.

Lors de la mise au point, une première version jugeait « fragile » la FM au pied de la mairie de Nantes, ce qui n'est pas réaliste. C'est ce constat qui a conduit à plafonner le bâti à 20 dB et à décaler les seuils FM. D'autres ajustements seront nécessaires.

*Pistes* :
- **Campagne de terrain** : 30 à 50 adresses variées (centre dense, périurbain, vallée, montagne, littoral). Pour chacune, noter « DAB+ capté / instable / rien » avec un poste ordinaire, à l'étage indiqué.
- **Contribution** : un formulaire « dites-nous si ça marche chez vous », placé sous le verdict.
- **Ajustement** : recaler les seuils sur ces observations, puis documenter le taux d'accord.

### Pénalité de distance simpliste
Le terme `20·log10(d/5 km)` reprend la décroissance en espace libre. Il ne tient compte ni de la puissance (voir ci-dessus) ni des modèles de propagation de référence pour la radiodiffusion, comme UIT-R P.1546.

*Piste* : utiliser des courbes P.1546 (champ médian selon distance, hauteur d'antenne et fréquence) une fois les puissances connues.

---

## 3. Limites du modèle physique

### Un seul obstacle par trajet — impact : **moyen**
Le modèle en lame de couteau ne retient que l'obstacle le plus pénalisant du relief et celui du bâti, puis additionne les deux. Plusieurs crêtes successives (méthodes de Deygout ou d'Epstein-Peterson) ne sont pas cumulées.

*Effet* : en relief tourmenté, sous-estimation possible du masquage.

### Réflexions et diffraction latérale ignorées — impact : **moyen**
En ville, le signal arrive souvent par réflexion sur les façades ou en contournant les immeubles par les côtés, pas seulement en direct. Le modèle ne voit que le trajet direct dans le plan vertical.

Le **plafond de 20 dB** sur le bâti est une correction empirique de ce défaut. Sa valeur est discutable : la littérature sur les pertes en milieu urbain donne des ordres de grandeur de 10 à 25 dB selon la densité.

*Effet* : sans plafond, le modèle serait très pessimiste dans les rues étroites. Avec le plafond, il peut devenir optimiste dans les cours fermées.

### Murs du logement, fenêtres, intérieur — impact : **moyen à fort**
L'outil ignore :
- l'atténuation des murs de l'immeuble du logement, qui ajoute souvent 5 à 15 dB, davantage en béton armé ou derrière un vitrage à couche métallique ;
- le côté où donnent les fenêtres ;
- le type de poste et d'antenne.

Les bâtiments à moins de 5 m du point d'adresse sont simplement exclus du calcul.

*Pistes* :
- demander l'orientation des fenêtres (rue/cour ou points cardinaux) et ne retenir que les directions « vues » ;
- utiliser `materiaux_des_murs` de la BD TOPO (fichiers fonciers) pour une perte de pénétration indicative.

### Végétation et bâtiments au-delà de 350 m
Le relief utilisé est un modèle numérique de **terrain** (RGE ALTI) : sans arbres ni bâtiments. Les bâtiments ne sont pris en compte que dans un rayon de 350 m. Une forêt sur une crête, ou une barre d'immeubles située à 500 m, ne sont pas vues.

*Piste* : utiliser un modèle numérique de **surface** (LiDAR HD de l'IGN) le long du trajet, au prix de calculs plus lourds.

### Hauteurs approximatives
- **Étages** : 3,0 m par niveau et oreille à 1,2 m. C'est faux pour l'haussmannien (3,5 à 4 m) et pour certains immeubles récents.
- **Antennes** : on prend la hauteur d'antenne **la plus haute** du site, qui n'est pas forcément celle de l'émetteur DAB+.
- **Bâtiments** : les hauteurs de la BD TOPO ont une précision variable selon la méthode d'acquisition (LiDAR, photogrammétrie, valeurs déduites).

### Position du point d'adresse
Le géocodage place souvent le point sur la façade ou dans la rue, pas dans le logement. L'immeuble de l'adresse est alors identifié par proximité (moins de 5 m), ce qui peut l'exclure à tort ou garder à tort un immeuble d'en face.

### Courbure terrestre et atmosphère
Le rayon effectif k = 4/3 représente une atmosphère standard. Les conditions particulières (inversions, conduits) ne sont pas modélisées. L'effet est négligeable à moins de 30 km.

---

## 4. Sélection des émetteurs

- **Score heuristique** : nombre d'émetteurs × √hauteur / distance². Un site important à 40 km peut être écarté au profit d'un relais local.
- **Rayon limité** : 50 km. Au-delà, rien n'est considéré, ce qui peut écarter de grands émetteurs en montagne ou en mer.
- **Fusion des supports à moins de 300 m** : elle peut réunir des sites de nature différente.
- **Petits relais d'autoroute** : les relais de faible puissance (péages, aires) ne sont pas exclus explicitement. Leur score est généralement faible, mais ils peuvent apparaître.
- **Outre-mer** : la logique fonctionne si les données IGN et ANFR sont présentes, mais elle n'a pas été testée.

---

## 5. Comparaison des exports ANFR

Les chiffres de retraits (406 émetteurs FM entre le 30 juin et le 30 septembre 2026) viennent d'une comparaison sur l'identifiant d'émetteur (`EMR_ID`).

- **Faux retraits** : un émetteur modifié peut changer d'identifiant et apparaître comme retiré puis ajouté (40 ajouts FM sur la période).
- **Attribution impossible** : on ne peut pas attribuer chaque retrait à Radio France, Mouv' ou une radio privée.
- **Calendrier** : l'export de fin septembre peut ne pas refléter toutes les opérations du 21–22 juillet, ni l'arrêt de Mouv' au 31 août, selon le rythme de mise à jour de la base de l'ANFR.

---

## 6. Technique et exploitation

- **Dépendance aux services de l'IGN** : si la Géoplateforme est lente ou indisponible, l'analyse échoue. La page réessaie trois fois puis affiche un message. Une coupure du service WFS fait basculer sur un calcul « relief seul ».
- **Dépendance aux CDN** : MapLibre et Carte facile sont chargés depuis unpkg. Une indisponibilité d'unpkg casse la carte, mais pas le diagnostic. Héberger ces fichiers dans le dépôt supprimerait ce risque.
- **Ouverture par double-clic** (`file://`) : le navigateur bloque le moteur de carte. Le diagnostic fonctionne, la carte non. Il faut servir la page par HTTP.
- **Page publiée dans Claude (artefact)** : l'outil n'y fonctionne pas, car la politique de sécurité bloque tous les appels à l'IGN.
- **Limite du WFS** : 6 000 bâtiments maximum par requête. Ce plafond est suffisant pour 350 m, même dans Paris (environ 900 bâtiments observés).
- **Performances** : sur un téléphone ancien, la 3D peut être lente. Ce cas n'a pas été testé.
- **Accessibilité** : la navigation au clavier de la liste d'adresses et les contrastes ont été soignés. En revanche, **aucun audit RGAA** n'a été réalisé, et la carte 3D n'a pas d'équivalent textuel complet.
- **Fraîcheur des données** : `data/emetteurs.js` reflète l'export du 30 septembre 2026. Sans mise à jour régulière, les réattributions de fréquences à venir ne seront pas prises en compte (voir [mise-a-jour-des-donnees.md](mise-a-jour-des-donnees.md)).
- **Vie privée** : l'adresse saisie part vers l'IGN et figure dans l'URL de la page, pour permettre le partage. Il faut le signaler si l'outil est diffusé largement.

---

## 7. Questions de projet

- **Licence du code** : aucune licence n'est choisie à ce jour. Sans licence, la réutilisation n'est juridiquement pas autorisée. Une licence libre (MIT, EUPL, AGPL…) reste à décider.
- **Nom et ton** : le titre interpelle directement Radio France, alors que l'outil n'est ni validé ni soutenu par Radio France, l'Arcom, l'ANFR ou l'IGN. Une mention est présente dans la page, mais la question de l'usage du nom peut se poser en cas de diffusion large.
- **Contexte mouvant** : un recours des radios privées est pendant devant le Conseil d'État, et la réattribution des quelque 300 fréquences rendues est en préparation. Le texte de contexte devra évoluer.
- **Gouvernance** : à terme, l'outil pourrait être porté par un acteur public ou associatif, ou contribuer à un commun numérique géographique. Rien n'est décidé.

---

## Synthèse

| Incertitude | Impact | Réductible ? |
|---|---|---|
| Puissance des émetteurs | Fort | Oui, avec des données Arcom à structurer |
| Radios portées par chaque émetteur | Moyen (DAB+ reconstitué, FM inconnue) | Oui, avec un export Arcom ou Radio France |
| Seuils du verdict non calibrés | Fort | Oui, par des mesures de terrain |
| Murs et orientation du logement | Moyen à fort | En partie, en demandant l'orientation |
| Réflexions urbaines (plafond 20 dB) | Moyen | En partie, avec un modèle plus riche |
| Obstacle unique | Moyen | Oui (Deygout) |
| Végétation, bâti lointain | Faible à moyen | Oui (LiDAR HD) |
| Hauteurs d'étage et d'antenne | Faible à moyen | En partie, en saisissant la hauteur sous plafond |
