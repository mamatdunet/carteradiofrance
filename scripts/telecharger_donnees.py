"""Télécharge les données sources nécessaires à la reconstruction de la page.

- l'export ANFR « Tables supports antennes émetteurs bandes » le plus récent
  (ou celui d'un mois donné) depuis data.gouv.fr ;
- la liste des communes (nom, code INSEE) depuis geo.api.gouv.fr.

Usage :
    python3 scripts/telecharger_donnees.py              # export le plus récent
    python3 scripts/telecharger_donnees.py --mois "juin 2026"

Les fichiers sont écrits dans sources/ (ignoré par git, voir .gitignore).
"""
import argparse, io, json, pathlib, time, urllib.request, zipfile

DATASET = "https://www.data.gouv.fr/api/1/datasets/551d4ff3c751df55da0cd89f/"
COMMUNES = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux&format=json"
ROOT = pathlib.Path(__file__).resolve().parent.parent / "sources"


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return r.read()
        except OSError as e:
            if i == tries - 1:
                raise
            print(f"  nouvel essai ({e})")
            time.sleep(3 * (i + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mois", help="libellé du mois de l'export, ex. « juin 2026 » (défaut : le plus récent)")
    args = ap.parse_args()
    ROOT.mkdir(exist_ok=True)

    meta = json.loads(get(DATASET))
    data = [r for r in meta["resources"] if r["title"].lower().startswith("tables supports antennes")]
    if args.mois:
        data = [r for r in data if args.mois.lower() in r["title"].lower()]
    if not data:
        raise SystemExit("Aucun export ANFR ne correspond.")
    res = max(data, key=lambda r: r.get("last_modified") or "")
    print("Export ANFR :", res["title"], "→", res["url"])
    dest = ROOT / ("anfr-" + res["url"].rsplit("/", 1)[-1].split("-export")[0])
    zipfile.ZipFile(io.BytesIO(get(res["url"]))).extractall(dest)
    print("  extrait dans", dest)

    (ROOT / "communes.json").write_bytes(get(COMMUNES))
    print("Communes : sources/communes.json")


if __name__ == "__main__":
    main()
