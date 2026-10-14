# Puis-je capter la nouvelle version numérique de Radio France 🥹 ?

Une page web qui répond, pour une adresse et un étage donnés, à une question simple : **est-ce que le DAB+ (la radio numérique terrestre) a des chances de passer chez moi ?** Elle donne aussi une indication pour la FM.

Depuis la nuit du 21 au 22 juillet 2026, Radio France a réorganisé son réseau FM : franceinfo a gagné des fréquences, France Musique en a perdu dans une partie du pays, et Mouv' a quitté la FM le 31 août 2026. Ces radios restent diffusées en DAB+, à condition qu'un émetteur DAB+ atteigne votre logement. Cela dépend du relief, des immeubles qui vous entourent et de votre étage. C'est ce que l'outil estime. Le détail est dans [docs/contexte.md](docs/contexte.md).

> **Statut : prototype.** L'outil produit une **estimation de masquage** à partir de données ouvertes, pas une mesure de réception. Ses seuils n'ont pas encore été confrontés au terrain. Lisez [docs/incertitudes.md](docs/incertitudes.md) avant de diffuser ou de citer un résultat.

## Ce que fait la page

1. Vous saisissez une adresse (autocomplétion IGN) et un étage.
2. La page choisit une dizaine de sites d'émission FM/DAB+ proches parmi les 4 666 déclarés à l'ANFR, dont ceux qui diffusent Radio France en DAB+.
3. Pour chaque site, elle récupère en direct :
   - le profil du relief entre votre adresse et l'antenne (RGE ALTI, IGN) ;
   - les bâtiments dans un rayon de 350 m (BD TOPO, IGN), avec leur hauteur.
4. Elle calcule ce que le relief et les toits voisins retirent au signal, en appliquant le modèle de diffraction en lame de couteau de la recommandation UIT-R P.526.
5. Elle traduit le résultat en un verdict lisible, calculé sur l'émetteur de Radio France le plus favorable :
   - « Oui, très probablement » ;
   - « Oui, probablement » ;
   - « C'est incertain » ;
   - « Difficilement ».

   Le verdict est accompagné de conseils pratiques : orientation de la fenêtre, effet de l'étage, antenne extérieure.
6. Une carte 3D (Carte facile + MapLibre, fond IGN) montre les immeubles du quartier et un trait vers chaque émetteur, coloré selon la gêne.
7. Un volet « détail technique » donne les chiffres et les coupes du terrain.

Tout le calcul se fait dans le navigateur. Il n'y a pas de serveur applicatif.

## Démarrage rapide

```bash
# Servir la page localement (la carte 3D ne fonctionne pas en ouvrant le fichier par double-clic)
python3 -m http.server 8000
# puis ouvrir http://localhost:8000/
```

Le résultat est partageable par l'URL : `…/index.html?adresse=2 rue de l'Hôtel de Ville, Nantes&etage=3`.

Pour la mise en ligne (GitHub Pages ou tout hébergement statique), voir [docs/deploiement.md](docs/deploiement.md).

## Organisation du dépôt

| Chemin | Rôle |
|---|---|
| `index.html` | La page complète, prête à servir. Elle est **générée** : ne pas l'éditer à la main. |
| `retraits.html` | La carte « Où la FM a reculé » : émetteurs FM retirés, fréquences de Mouv' remises en appel, distance au DAB+ de Radio France. **Générée** elle aussi. |
| `src/page.html` | Le gabarit de la page (HTML, CSS, JavaScript). C'est ici qu'on modifie l'interface et le calcul. |
| `src/retraits.html` | Le gabarit de la carte des retraits. |
| `data/emetteurs.js` | La liste des sites FM/DAB+ extraite de l'ANFR, injectée dans la page. |
| `data/retraits.js` | Les données de la carte des retraits, injectées dans `retraits.html`. |
| `data/frequences-remises-en-appel-2026-05-20.csv` | Les 31 fréquences FM remises en appel par l'Arcom le 20 mai 2026 (30 de Mouv'), recopiées de l'annexe de la décision. |
| `data/multiplex-radio-france.csv` | Les sites DAB+ qui diffusent Radio France (multiplex national M2, stations ICI), avec la décision du Journal officiel correspondante. |
| `scripts/telecharger_donnees.py` | Télécharge l'export ANFR, la liste des communes et les pages de dabplus.fr. |
| `scripts/extraire_multiplex.py` | Produit `data/multiplex-radio-france.csv` à partir des pages de dabplus.fr. |
| `scripts/extraire_emetteurs.py` | Produit `data/emetteurs.js` à partir de l'export ANFR et y rattache les multiplex de Radio France. |
| `scripts/preparer_carte_retraits.py` | Produit `data/retraits.js` à partir de la comparaison des exports, des fréquences remises en appel et de `data/emetteurs.js`. |
| `scripts/assembler_page.py` | Assemble `index.html` et `retraits.html` à partir des gabarits de `src/` et des données. |
| `scripts/comparer_exports.py` | Compare deux exports ANFR (émetteurs retirés ou ajoutés). |
| `analyses/` | Résultats de comparaisons, dont l'effet de la réorganisation entre fin juin et fin septembre 2026. |
| `docs/` | Documentation détaillée. |

## Documentation

- [Contexte : la réorganisation des fréquences de Radio France](docs/contexte.md)
- [Méthode de calcul](docs/methodologie.md)
- [Données utilisées et licences](docs/donnees.md)
- [Incertitudes et limites connues](docs/incertitudes.md)
- [Déploiement](docs/deploiement.md)
- [Mettre à jour les données](docs/mise-a-jour-des-donnees.md)

## Chiffres clés de la réorganisation, vus depuis les données ANFR

En comparant l'export ANFR du 30 juin 2026 (avant la bascule) à celui du 30 septembre 2026 :

- **FM** : le parc passe de 11 237 à 10 871 émetteurs. On compte 406 retraits sur 391 sites, et 40 ajouts. Parmi les retraits, 307 émetteurs étaient exploités par TDF, 83 par Towercast et 16 sur des sites privés.
- **DAB+** : le parc passe de 1 084 à 1 106 émetteurs, soit 22 ajouts.
- **Répartition** : les retraits FM se concentrent dans les départements ruraux et montagneux. L'Aveyron arrive en tête, suivi des Hautes-Alpes, de la Côte-d'Or, du Lot, de la Savoie, de la Corse-du-Sud et du Gard.

La carte [`retraits.html`](retraits.html) montre ces retraits site par site, avec la distance au plus proche émetteur DAB+ de Radio France : 128 des 391 sites n'en ont aucun à moins de 30 km. Le détail par émetteur se trouve dans `analyses/`. Les limites de cette comparaison sont expliquées dans [docs/incertitudes.md](docs/incertitudes.md#5-comparaison-des-exports-anfr).

## Ce que l'outil ne dit pas

- **Quelles radios passent par un émetteur FM.** L'ANFR ne publie ni le programme ni la fréquence exacte. En DAB+, l'outil reconstitue cette information à partir des décisions de l'Arcom : il sait quels sites diffusent le multiplex national de Radio France (France Inter, franceinfo, France Culture, France Musique, FIP, Mouv') et les stations ICI. En FM, il ne le sait pas : consultez le moteur de recherche de Radio France. Ce rattachement a lui aussi ses limites, décrites dans [docs/incertitudes.md](docs/incertitudes.md).
- **La puissance des émetteurs.** Elle n'est pas publiée non plus. Le verdict repose sur le masquage et la distance, pas sur un niveau de champ réel.
- **L'intérieur de votre logement.** L'outil ignore les murs, l'orientation des fenêtres et le modèle de poste.

## Crédits

- Données : [IGN – Géoplateforme](https://geoservices.ign.fr/) (géocodage, RGE ALTI, BD TOPO, Plan IGN), [ANFR via data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1), [geo.api.gouv.fr](https://geo.api.gouv.fr/), décisions de l'Arcom au Journal officiel relevées par [dabplus.fr](https://www.dabplus.fr/).
- Cartographie : [Carte facile](https://fab-geocommuns.github.io/carte-facile-site/) (Fabrique des géocommuns, IGN) et [MapLibre GL JS](https://maplibre.org/).
- Projet initié par Matthieu Chatry.

Ce n'est pas un outil officiel de Radio France, de l'Arcom, de l'ANFR ou de l'IGN.
