"""Liste les sites DAB+ qui diffusent les radios de Radio France, à partir des pages de dabplus.fr.

Usage :
    python3 scripts/extraire_multiplex.py sources/dabplus data/multiplex-radio-france.csv

dabplus.fr recopie, multiplex par multiplex, les radios autorisées par l'Arcom et les sites
d'émission publiés au Journal officiel (puissance apparente rayonnée, altitude, hauteur d'antenne,
lien vers la décision). Le script garde les multiplex qui portent au moins une radio de
Radio France :
- le multiplex métropolitain M2 (France Inter, franceinfo, France Culture, France Musique,
  FIP, Mouv') ;
- les multiplex locaux et étendus qui portent une station ICI (ex-France Bleu).

Chaque ligne du CSV produit décrit un site d'émission d'un multiplex. Un même site peut
apparaître sur plusieurs pages (allotissements à cheval sur plusieurs zones) : les doublons
(même multiplex, même canal, même site) sont retirés.
"""
import base64, csv, html, json, pathlib, re, sys

RF = re.compile(r"^(ici\b(?! ?&)|France (Inter|Info|Culture|Musique|Bleu)\b|FIP\b|Mouv)", re.I)
HEAD = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
TABLE = re.compile(r'data-ext="([A-Za-z0-9+/=]+)"')
SITE = re.compile(r"^(.*?)\s*\((\d[\dAB]|\d{3})\)")


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def radios(chunk):
    """Noms de radios listés entre le titre du multiplex et le bouton « Autorisation mux »."""
    end = chunk.find("Autorisation mux")
    part = chunk[:end if end > 0 else len(chunk)]
    names = [text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", part, re.S)]
    return [n for n in names if n and n != "Radio"]


def sites(chunk):
    for b in TABLE.findall(chunk):
        rows = json.loads(base64.b64decode(b))["rows"]
        for r in rows[1:]:
            if not r or not r.get("0", {}).get("value"):
                continue
            yield (text(r["0"]["value"]), r.get("1", {}).get("value", ""), r.get("2", {}).get("value", ""),
                   r.get("3", {}).get("value", ""), r.get("4", {}).get("link", {}).get("value", ""))


def main(src, out):
    seen, out_rows = set(), []
    for p in sorted(pathlib.Path(src).rglob("*.html")):
        doc = p.read_text(encoding="utf-8")
        heads = [(m.start(), text(m.group(1))) for m in HEAD.finditer(doc)]
        for i, (pos, title) in enumerate(heads):
            if not title.startswith("Multiplex") or "Canal" not in title:
                continue
            chunk = doc[pos:heads[i + 1][0] if i + 1 < len(heads) else len(doc)]
            rf = [re.sub(r"\s*\(.*", "", n) for n in radios(chunk) if RF.match(n)]
            rf = [n for n in rf if "arrêt" not in n.lower()]
            if not rf:
                continue
            mux = "M2" if "métropolitain M2" in title else re.sub(r",.*", "", title.replace("Multiplex ", "", 1))
            canal = re.search(r"Canal (\w+)", title).group(1)
            for site, par, alt, haut, jorf in sites(chunk):
                if "plus en service" in site:
                    continue
                m = SITE.match(site)
                if not m:
                    print("  site illisible :", site)
                    continue
                commune = m.group(1).split(",")[-1].strip()
                diffuseur = next((d for d in ("TDF", "towerCast", "GRAM", "Itas", "OneCast") if d.lower() in site.lower()), "")
                key = (mux, canal, site.split(" (Ph")[0])
                if key in seen:
                    continue
                seen.add(key)
                out_rows.append([mux, canal, ", ".join(dict.fromkeys(rf)), site, m.group(2), commune, diffuseur,
                                 par, alt, haut, jorf, p.stem])
    out_rows.sort(key=lambda r: (r[0] != "M2", r[0], r[4], r[5]))
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["multiplex", "canal", "radios_radio_france", "site", "departement", "commune", "diffuseur",
                    "par_kw", "altitude_m", "hauteur_antenne_m", "decision_jorf", "page_dabplus"])
        w.writerows(out_rows)
    m2 = sum(r[0] == "M2" for r in out_rows)
    print(f"{len(out_rows)} sites écrits dans {out} (M2 : {m2}, multiplex locaux avec ICI : {len(out_rows) - m2})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
