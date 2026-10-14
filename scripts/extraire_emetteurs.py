"""Extrait la liste nationale des sites d'émission FM et DAB+ depuis un export ANFR.

Usage :
    python3 scripts/extraire_emetteurs.py sources/anfr-AAAAMMJJ sources/communes.json data/emetteurs.js [data/multiplex-radio-france.csv]

Chaque ligne du fichier produit décrit un support (pylône, château d'eau…) :
    [lat, lon, code_insee, commune, lieu-dit, nb_emetteurs_FM, nb_emetteurs_DAB+, hauteur_antenne_max_m, exploitants,
     diffuse_M2, stations_ICI]

Règles :
- émetteurs retenus : EMR_LB_SYSTEME = « FM » ou « RDF T-DAB » ;
- hauteur d'antenne : la plus haute AER_NB_ALT_BAS (hauteur du bas d'antenne au-dessus du sol)
  parmi les antennes FM/DAB+ du support ; à défaut, la hauteur du support ;
- exploitants : identifiants ADM_ID de SUP_STATION traduits pour les plus courants
  (TDF, Towercast, « Site privé »…) ;
- diffuse_M2 (1/0) et stations_ICI : rapprochement avec la liste des sites DAB+ de Radio France
  (scripts/extraire_multiplex.py). L'ANFR ne dit pas quel multiplex passe par quel émetteur :
  chaque site de la liste est rattaché au support DAB+ de même département et de même commune,
  départagé par le diffuseur puis par les mots du lieu-dit. Les supports distants de moins de 1 km
  sont considérés comme un seul site. Les sites non rattachés sont affichés.
"""
import csv, json, math, re, sys, unicodedata
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


# Sites que le nom de commune ne suffit pas à retrouver : (département, commune de la liste) →
# (commune ANFR, mot du lieu-dit ANFR).
MANUEL = {
    # « Roc Redoun » : le lieu-dit IGN « Coumo del Roc Redoun » est à 1 km du support towerCast
    # « Les Coumos de la Quirro » de Baixas, seul site DAB+ du secteur.
    ("66", "Cases-de-Pène"): ("Baixas", "coumos"),
}
MOTS_VIDES = {"rue", "route", "lieudit", "chemin", "avenue", "les", "des", "del", "sur", "towercast", "tdf", "site"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\bsainte\b", "ste", re.sub(r"\bsaint\b", "st", s))
    s = re.sub(r"\bs\b", "sur", s)
    return re.sub(r"[^a-z0-9]", "", s)


def mots(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z0-9]{3,}", s)) - MOTS_VIDES


def km(a, b):
    return math.hypot((a[0] - b[0]) * 111, (a[1] - b[1]) * 111 * math.cos(math.radians(a[0])))


def rattacher(rows, csv_path, communes):
    """Ajoute à chaque support DAB+ les multiplex de Radio France qu'il diffuse."""
    dab = [r for r in rows if r[6] > 0]
    dep = lambda r: r[2][:3] if r[2].startswith("97") else r[2][:2]
    manque = 0
    for s in csv.DictReader(open(csv_path, encoding="utf-8")):
        d, com, site = s["departement"], s["commune"], s["site"]
        pool = [r for r in dab if dep(r) == d]
        if (d, com) in MANUEL:
            c_anfr, mot = MANUEL[(d, com)]
            c = [r for r in pool if r[3] == c_anfr and mot in r[4].lower()]
        else:
            c = [r for r in pool if norm(r[3]) == norm(com)]
            if not c and (d, norm(com)) not in communes:
                # commune nouvelle, ancienne commune ou lieu-dit pris pour la commune : on cherche
                # une commune ANFR citée dans le libellé (jamais pour une commune existante, sans quoi
                # « La Ferté-sous-Jouarre » serait rattachée à Jouarre)
                c = [r for r in pool if len(norm(r[3])) > 4 and norm(r[3]) in norm(site)]
                if c:  # « Château-Gontier-sur-Mayenne » plutôt que « Mayenne »
                    n = max(len(norm(r[3])) for r in c)
                    c = [r for r in c if len(norm(r[3])) == n]
            ville = {"Paris": "751", "Lyon": "6938", "Marseille": "132"}.get(re.sub(r" \d+e arr.*", "", com))
            if not c and ville:  # arrondissements : codes INSEE propres, nom de commune absent
                arr = re.search(r"(\d+)e arr", com)
                c = [r for r in pool if r[2].startswith(ville + ("%02d" % int(arr.group(1)) if arr else ""))]
        op = {"TDF": "TDF", "towerCast": "Towercast"}.get(s["diffuseur"])
        if len(c) > 1 and op:
            c = [r for r in c if op in r[8]] or c
        if len(c) > 1:
            sc = {id(r): len(mots(site) & mots(r[4])) for r in c}
            best = max(sc.values())
            if best:
                c = [r for r in c if sc[id(r)] == best]
        if not c or max(km(c[0], r) for r in c) > 1.0:
            manque += 1
            print(f"  non rattaché ({len(c)} candidats) : {s['multiplex']} · {site}")
            continue
        for r in c:
            if s["multiplex"] == "M2":
                r[9] = 1
            else:
                r[10] = ", ".join(sorted(set(filter(None, r[10].split(", ") + s["radios_radio_france"].split(", ")))))
    print(f"Radio France : {sum(r[9] for r in rows)} supports M2, {sum(bool(r[10]) for r in rows)} supports ICI, {manque} sites non rattachés")


def main(root, communes_path, out_path, multiplex_path=None):
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
                     s["fm"], s["dab"], round(h, 1), ", ".join(sorted(s["ops"])), 0, ""])
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    if multiplex_path:
        rattacher(rows, multiplex_path, {(c[:3] if c.startswith("97") else c[:2], norm(n)) for c, n in names.items()})
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.TX=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";")
    print(f"{len(rows)} sites FM/DAB+ écrits dans {out_path}")


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
