"""Assemble les pages publiées à partir des gabarits et des données.

Usage :
    python3 scripts/assembler_page.py

- src/page.html + data/emetteurs.js → index.html (emplacement /*TX*/) ;
- src/retraits.html + data/retraits.js → retraits.html (emplacement /*RET*/).

Chaque emplacement se trouve dans une balise <script> ; il est remplacé par le contenu
du fichier de données (window.TX = [...] ou window.RET = {...}).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [("page.html", "index.html", "/*TX*/", "emetteurs.js"),
         ("retraits.html", "retraits.html", "/*RET*/", "retraits.js")]

for src, out, slot, data in PAGES:
    tpl = (ROOT / "src" / src).read_text(encoding="utf-8")
    if slot not in tpl:
        raise SystemExit(f"Emplacement {slot} introuvable dans src/{src}")
    (ROOT / out).write_text(tpl.replace(slot, (ROOT / "data" / data).read_text(encoding="utf-8"), 1), encoding="utf-8")
    print(f"{out} assemblé")
