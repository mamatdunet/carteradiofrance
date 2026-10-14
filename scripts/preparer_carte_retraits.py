"""Prépare les données de la carte « Où la FM a reculé » (retraits.html).

Usage :
    python3 scripts/preparer_carte_retraits.py \\
        analyses/emetteurs-retires-ajoutes-2026-06-30_2026-09-30.csv \\
        data/frequences-remises-en-appel-2026-05-20.csv \\
        data/emetteurs.js sources/communes.json data/retraits.js

Entrées :
- la comparaison de deux exports ANFR (scripts/comparer_exports.py) ;
- les fréquences FM remises en appel par l'Arcom le 20 mai 2026 (30 fréquences de Mouv',
  une d'une radio privée), recopiées de l'annexe de la décision ;
- data/emetteurs.js (export ANFR le plus récent, avec les sites DAB+ de Radio France) ;
- la liste des communes, pour nommer les sites.

Sortie : window.RET = {sites, appel, m2}.
    sites : [lat, lon, insee, commune, lieu-dit, nb_FM_retirés, exploitants, nb_FM_restants,
             nb_FM_ajoutés_à_côté, distance_km_site_M2, distance_km_site_DAB+]
    appel : [fréquence, zone, département, commune d'implantation, lat, lon]
    m2    : [lat, lon, commune] des supports qui diffusent le multiplex national de Radio France

Les « restants » et « ajoutés à côté » comptent les émetteurs FM à moins de 300 m dans l'export
le plus récent. Un ajout à côté d'un retrait signale souvent un simple changement d'identifiant.
Les coordonnées des fréquences remises en appel sont celles du centre de la commune
d'implantation, relevées une fois avec le géocodeur de l'IGN et inscrites dans le CSV : l'Arcom ne publie
pas l'emplacement exact de l'émetteur.
"""
import csv, json, math, sys
from collections import defaultdict

ARR = {"751": "Paris", "693": "Lyon", "132": "Marseille"}


def fix(s):
    """La comparaison a été écrite à partir de libellés latin-1 mal décodés."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return s


def km(a, b):
    return math.hypot((a[0] - b[0]) * 111.2, (a[1] - b[1]) * 111.2 * math.cos(math.radians(a[0])))


def nearest(p, pts):
    return round(min((km(p, q) for q in pts), default=999), 1)


def main(comparaison, appel_path, emetteurs, communes_path, out):
    names = {c["code"]: c["nom"] for c in json.load(open(communes_path, encoding="utf-8"))}
    tx = json.loads(open(emetteurs, encoding="utf-8").read().removeprefix("window.TX=").removesuffix(";"))
    m2 = [(t[0], t[1]) for t in tx if t[9]]
    m2_out = [[t[0], t[1], t[3]] for t in tx if t[9]]
    dab = [(t[0], t[1]) for t in tx if t[6]]
    fm_now = [(t[0], t[1], t[5]) for t in tx if t[5]]

    rows = list(csv.DictReader(open(comparaison, encoding="utf-8")))
    ajouts = [(float(r["lat"]), float(r["lon"])) for r in rows if r["evenement"] == "ajoute" and r["systeme"] == "FM"]
    sites = defaultdict(lambda: dict(n=0, ops=set()))
    for r in rows:
        if r["evenement"] != "retire" or r["systeme"] != "FM":
            continue
        s = sites[(float(r["lat"]), float(r["lon"]), r["insee"], fix(r["lieu"]).strip())]
        s["n"] += 1
        s["ops"].add(r["exploitant"])

    out_sites = []
    for (lat, lon, insee, lieu), s in sites.items():
        com = names.get(insee) or ARR.get(insee[:3], "")
        p = (lat, lon)
        reste = sum(n for a, b, n in fm_now if km(p, (a, b)) < 0.3)
        ajout = sum(1 for q in ajouts if km(p, q) < 0.3)
        out_sites.append([lat, lon, insee, com, lieu[:50], s["n"], ", ".join(sorted(filter(None, s["ops"]))),
                          reste, ajout, nearest(p, m2), nearest(p, dab)])
    out_sites.sort(key=lambda r: (r[2], r[0]))

    appel = []
    for a in csv.DictReader(open(appel_path, encoding="utf-8")):
        appel.append([float(a["frequence_mhz"]), a["zone"], a["departement"], a["commune_implantation"],
                      float(a["lat_centre_commune"]), float(a["lon_centre_commune"])])

    with open(out, "w", encoding="utf-8") as f:
        f.write("window.RET=" + json.dumps({"sites": out_sites, "appel": appel, "m2": m2_out}, ensure_ascii=False, separators=(",", ":")) + ";")
    print(f"{len(out_sites)} sites ({sum(s[5] for s in out_sites)} émetteurs FM retirés), "
          f"{len(appel)} fréquences remises en appel, écrits dans {out}")
    print(f"  sans site M2 à moins de 30 km : {sum(s[9] > 30 for s in out_sites)} sites")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
