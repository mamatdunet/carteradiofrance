"""Télécharge les données sources nécessaires à la reconstruction de la page.

- l'export ANFR « Tables supports antennes émetteurs bandes » le plus récent
  (ou celui d'un mois donné) depuis data.gouv.fr ;
- la liste des communes (nom, code INSEE) depuis geo.api.gouv.fr ;
- les pages zone par zone de dabplus.fr (multiplex DAB+, radios et sites d'émission), dont
  scripts/extraire_multiplex.py tire les sites qui diffusent Radio France.

Usage :
    python3 scripts/telecharger_donnees.py              # export le plus récent
    python3 scripts/telecharger_donnees.py --mois "juin 2026"

Les fichiers sont écrits dans sources/ (ignoré par git, voir .gitignore).
"""
import argparse, io, json, pathlib, re, time, urllib.request, zipfile

DATASET = "https://www.data.gouv.fr/api/1/datasets/551d4ff3c751df55da0cd89f/"
COMMUNES = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux&format=json"
DABPLUS = "https://www.dabplus.fr"
# Pages du plan du site qui ne décrivent pas une zone.
DABPLUS_HORS_ZONE = {"recepteurs", "en-voiture", "promotion", "contact", "faq", "actualite", "actualites"}
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

    plan = get(DABPLUS + "/sitemap.xml").decode("utf-8")
    pages = [u for u in re.findall(r"<loc>([^<]+)</loc>", plan)
             if re.fullmatch(re.escape(DABPLUS) + r"/(metropolitain/)?[a-z0-9-]+/?", u)
             and u.rstrip("/").rsplit("/", 1)[-1] not in DABPLUS_HORS_ZONE]
    for u in pages:
        dest = ROOT / "dabplus" / (u.rstrip("/")[len(DABPLUS) + 1:] + ".html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(get(u))
        time.sleep(0.5)  # le site est tenu par un particulier : on ne le sollicite pas trop vite
    print(f"dabplus.fr : {len(pages)} pages dans sources/dabplus/")


if __name__ == "__main__":
    main()
