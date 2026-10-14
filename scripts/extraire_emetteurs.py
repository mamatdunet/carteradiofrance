"""Extrait la liste nationale des sites d'émission FM et DAB+ depuis un export ANFR.

Usage :
    python3 scripts/extraire_emetteurs.py sources/anfr-AAAAMMJJ sources/communes.json data/emetteurs.js

Chaque ligne du fichier produit décrit un support (pylône, château d'eau…) :
    [lat, lon, code_insee, commune, lieu-dit, nb_emetteurs_FM, nb_emetteurs_DAB+, hauteur_antenne_max_m, exploitants]

Règles :
- émetteurs retenus : EMR_LB_SYSTEME = « FM » ou « RDF T-DAB » ;
- hauteur d'antenne : la plus haute AER_NB_ALT_BAS (hauteur du bas d'antenne au-dessus du sol)
  parmi les antennes FM/DAB+ du support ; à défaut, la hauteur du support ;
- exploitants : identifiants ADM_ID de SUP_STATION traduits pour les plus courants
  (TDF, Towercast, « Site privé »…).
"""
import csv, json, sys
from collections import defaultdict

SYS = {"FM": "fm", "RDF T-DAB": "dab"}
ADM = {"39": "TDF", "170": "Towercast", "210": "Site privé", "214": "Radio étrangère", "12": "Arcom"}


def read(path):
    with open(path, encoding="latin-1", newline="") as f:
        yield from csv.DictReader(f, delimiter=";")


def fix(s):
    """Certains libellés sont en UTF-8 dans un fichier déclaré latin-1."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return s


def dms(d, m, s, h):
    v = float(d) + float(m) / 60 + float(s.replace(",", ".")) / 3600
    return -v if h in ("S", "W") else v


def main(root, communes_path, out_path):
    em = {}
    for r in read(f"{root}/SUP_EMETTEUR.txt"):
        k = SYS.get(r["EMR_LB_SYSTEME"])
        if k:
            em[r["EMR_ID"]] = (k, r["STA_NM_ANFR"], r["AER_ID"])
    aers = {e[2] for e in em.values()}
    aer = {r["AER_ID"]: (r["SUP_ID"], r["AER_NB_ALT_BAS"]) for r in read(f"{root}/SUP_ANTENNE.txt") if r["AER_ID"] in aers}
    stas = {e[1] for e in em.values()}
    adm = {r["STA_NM_ANFR"]: r["ADM_ID"] for r in read(f"{root}/SUP_STATION.txt") if r["STA_NM_ANFR"] in stas}
    sups = {a[0] for a in aer.values()}
    sup = {}
    for r in read(f"{root}/SUP_SUPPORT.txt"):
        if r["SUP_ID"] not in sups:
            continue
        try:
            lat = dms(r["COR_NB_DG_LAT"], r["COR_NB_MN_LAT"], r["COR_NB_SC_LAT"], r["COR_CD_NS_LAT"])
            lon = dms(r["COR_NB_DG_LON"], r["COR_NB_MN_LON"], r["COR_NB_SC_LON"], r["COR_CD_EW_LON"])
        except ValueError:
            continue
        lieu = fix((r["ADR_LB_LIEU"] or r["ADR_LB_ADD1"]).strip())
        sup[r["SUP_ID"]] = (lat, lon, r["COM_CD_INSEE"], lieu, r["SUP_NM_HAUT"])

    site = defaultdict(lambda: dict(fm=0, dab=0, h=[], ops=set()))
    for k, sta, aid in em.values():
        a = aer.get(aid)
        if not a or a[0] not in sup:
            continue
        s = site[a[0]]
        s[k] += 1
        if a[1]:
            s["h"].append(float(a[1].replace(",", ".")))
        o = ADM.get(adm.get(sta, ""))
        if o:
            s["ops"].add(o)

    names = {c["code"]: c["nom"] for c in json.load(open(communes_path, encoding="utf-8"))}
    rows = []
    for sid, s in site.items():
        lat, lon, insee, lieu, hsup = sup[sid]
        h = max(s["h"]) if s["h"] else (float(hsup.replace(",", ".")) if hsup else 30.0)
        rows.append([round(lat, 5), round(lon, 5), insee, names.get(insee, ""), lieu[:50],
                     s["fm"], s["dab"], round(h, 1), ", ".join(sorted(s["ops"]))])
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.TX=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";")
    print(f"{len(rows)} sites FM/DAB+ écrits dans {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
