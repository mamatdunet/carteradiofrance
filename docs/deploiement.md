# Déploiement

La page est **statique** : un seul fichier, `index.html`, qui interroge directement les services de l'IGN depuis le navigateur. Il n'y a ni serveur applicatif ni base de données à maintenir.

## GitHub Pages

1. Dans le dépôt, ouvrez **Settings → Pages**.
2. Dans *Build and deployment*, choisissez *Deploy from a branch*.
3. Sélectionnez la branche par défaut du dépôt et le dossier `/ (root)`, puis enregistrez.
4. Au bout d'une minute environ, la page est publiée sur `https://<compte>.github.io/carteradiofrance/`.

## Autres hébergements

Tout hébergement de fichiers statiques convient : Netlify, un serveur web classique, ou une page WordPress qui charge le fichier dans un `iframe` ou le sert tel quel. Seul `index.html` est nécessaire : les dossiers `src/`, `data/`, `scripts/` et `docs/` ne servent qu'à le reconstruire et le documenter.

## Tester en local

```bash
python3 -m http.server 8000
# puis http://localhost:8000/
```

Ouvrir `index.html` par double-clic (`file://`) fonctionne pour le diagnostic, mais **pas pour la carte 3D**. Le navigateur refuse en effet de lancer le moteur de MapLibre depuis un fichier local. La page affiche alors un message à la place de la carte.

## Ce qui ne fonctionne pas

- **Page publiée dans Claude (artefact)** : la politique de sécurité de ces pages bloque tout appel vers un autre domaine. L'autocomplétion d'adresse, le relief et les bâtiments ne répondent donc pas.
- **Hébergement avec une politique de sécurité stricte (CSP)** : il faut autoriser :
  - `data.geopf.fr` pour les appels réseau et les tuiles ;
  - `unpkg.com` pour les scripts et les styles ;
  - `fonts.googleapis.com` et `fonts.gstatic.com` pour les polices ;
  - `blob:` pour le moteur de carte (`worker-src`).

## Lien de partage

La page reprend l'adresse et l'étage dans l'URL, par exemple `?adresse=2 rue de l'Hôtel de Ville, Nantes&etage=3`. À l'ouverture d'un tel lien, l'analyse se lance automatiquement.
