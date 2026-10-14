"""Compare deux exports ANFR et liste les émetteurs FM/DAB+ apparus ou disparus.

Sert à observer les effets de la réorganisation de juillet 2026 (export du 30 juin
comparé à celui du 30 septembre 2026, par exemple).

Usage :
    python3 scripts/comparer_exports.py sources/anfr-20260630 sources/anfr-20260930 analyses/retraits.csv

Limite : la comparaison se fait sur l'identifiant d'émetteur (EMR_ID). Un émetteur
modifié peut changer d'identifiant et apparaître à la fois comme retiré et ajouté.
"""
import csv, sys
from collections import Counter

SYS = {"FM": "FM", "RDF T-DAB": "DAB+"}
ADM = {"39": "TDF", "170": "Towercast", "210": "Site privé", "214": "Radio étrangère", "12": "Arcom"}


def read(path):
    with open(path, encoding="latin-1", newline="") as f:
        yield from csv.DictReader(f, delimiter=";")


def dms(d, m, s, h):
    v = float(d) + float(m) / 60 + float(s.replace(",", ".")) / 3600
    return -v if h in ("S", "W") else v


def load(root):
    em = {r["EMR_ID"]: (SYS[r["EMR_LB_SYSTEME"]], r["STA_NM_ANFR"], r["AER_ID"])
          for r in read(f"{root}/SUP_EMETTEUR.txt") if r["EMR_LB_SYSTEME"] in SYS}
    aers = {e[2] for e in em.values()}
    aer = {r["AER_ID"]: r["SUP_ID"] for r in read(f"{root}/SUP_ANTENNE.txt") if r["AER_ID"] in aers}
    stas = {e[1] for e in em.values()}
    adm = {r["STA_NM_ANFR"]: r["ADM_ID"] for r in read(f"{root}/SUP_STATION.txt") if r["STA_NM_ANFR"] in stas}
    sups = set(aer.values())
    sup = {}
    for r in read(f"{root}/SUP_SUPPORT.txt"):
        if r["SUP_ID"] in sups:
            try:
                sup[r["SUP_ID"]] = (dms(r["COR_NB_DG_LAT"], r["COR_NB_MN_LAT"], r["COR_NB_SC_LAT"], r["COR_CD_NS_LAT"]),
                                    dms(r["COR_NB_DG_LON"], r["COR_NB_MN_LON"], r["COR_NB_SC_LON"], r["COR_CD_EW_LON"]),
                                    r["COM_CD_INSEE"], (r["ADR_LB_LIEU"] or r["ADR_LB_ADD1"]).strip())
            except ValueError:
                pass
    out = {}
    for eid, (k, sta, aid) in em.items():
        s = sup.get(aer.get(aid))
        if s:
            out[eid] = dict(systeme=k, exploitant=ADM.get(adm.get(sta, ""), adm.get(sta, "")),
                            lat=round(s[0], 5), lon=round(s[1], 5), insee=s[2], lieu=s[3])
    return out


def main(before_dir, after_dir, out_csv):
    a, b = load(before_dir), load(after_dir)
    removed = {e: v for e, v in a.items() if e not in b}
    added = {e: v for e, v in b.items() if e not in a}
    print("avant :", Counter(v["systeme"] for v in a.values()))
    print("après :", Counter(v["systeme"] for v in b.values()))
    print("retirés :", Counter(v["systeme"] for v in removed.values()), "par exploitant FM :",
          Counter(v["exploitant"] for v in removed.values() if v["systeme"] == "FM"))
    print("ajoutés :", Counter(v["systeme"] for v in added.values()))
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["evenement", "emr_id", "systeme", "exploitant", "insee", "lieu", "lat", "lon"])
        for ev, d in (("retire", removed), ("ajoute", added)):
            for e, v in sorted(d.items()):
                w.writerow([ev, e, v["systeme"], v["exploitant"], v["insee"], v["lieu"], v["lat"], v["lon"]])
    print("détail écrit dans", out_csv)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
