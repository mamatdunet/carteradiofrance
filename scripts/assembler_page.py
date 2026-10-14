"""Assemble index.html à partir du gabarit et de la liste des émetteurs.

Usage :
    python3 scripts/assembler_page.py            # src/page.html + data/emetteurs.js → index.html

Le gabarit contient un emplacement /*TX*/ dans une balise <script> ; il est remplacé
par le contenu de data/emetteurs.js (window.TX = [...]).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
tpl = (ROOT / "src" / "page.html").read_text(encoding="utf-8")
data = (ROOT / "data" / "emetteurs.js").read_text(encoding="utf-8")
if "/*TX*/" not in tpl:
    raise SystemExit("Emplacement /*TX*/ introuvable dans src/page.html")
(ROOT / "index.html").write_text(tpl.replace("/*TX*/", data, 1), encoding="utf-8")
print("index.html assemblé")
