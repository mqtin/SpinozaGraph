#!/usr/bin/env python3
"""Génère explorer.html : graphe et textes de l'Éthique, dans un fichier HTML autonome.

Lit elements/*.md (front-matter et une section par langue), les métadonnées des langues
(sources/ethica/*/types.json), DEVELOPMENT.md et notes/*.md.

Usage :
    python outils/build_explorer.py           # génère explorer.html
    python outils/build_explorer.py --watch   # régénère à chaque modification
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ethica import LANGS, ROOT, Model, read_text  # noqa: E402

import yaml  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent / "explorer_template.html"
OUTPUT = ROOT / "explorer.html"
ELEMENTS = ROOT / "elements"
NOTES = ROOT / "notes"
DOC_FILES = ["DEVELOPMENT.md"]

FRONT_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def lang_sections(body: str) -> dict:
    out, cur, buf = {}, None, []
    for line in body.split("\n"):
        h = re.match(r"^##\s+(\S+)\s*$", line)
        if h:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = h.group(1), []
        else:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def load_elements(order: dict):
    elements, problems = [], []
    for path in sorted(ELEMENTS.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        m = FRONT_RE.match(path.read_text(encoding="utf-8").replace("\r\n", "\n"))
        if not m:
            problems.append(f"{rel} : pas de front-matter")
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        secs = lang_sections(COMMENT_RE.sub("", m.group(2)))
        eid = str(meta["id"])
        elements.append({
            "id": eid,
            "file": rel,
            "type": meta.get("type"),
            "type_la": meta.get("type_la"),
            "partie": meta.get("partie"),
            "numero": meta.get("numero"),
            "parent": meta.get("parent"),
            "repli": meta.get("repli"),
            "depends_on": [str(x) for x in meta.get("depends_on") or []],
            "voir": [str(x) for x in meta.get("voir") or []],
            "corrections": meta.get("corrections") or [],
            "text": {k: secs.get(k, "") for k in LANGS},
            "ordre": order.get(eid, 10**6),
        })
    elements.sort(key=lambda e: e["ordre"])
    return elements, problems


def load_documents():
    docs = [{"name": n, "body": (ROOT / n).read_text(encoding="utf-8")} for n in DOC_FILES if (ROOT / n).exists()]
    if NOTES.is_dir():
        for p in sorted(NOTES.rglob("*.md")):
            docs.append({"name": p.relative_to(ROOT).as_posix(), "body": p.read_text(encoding="utf-8")})
    return docs


# Titres des parties : latin tiré de meta.json ; français d'après Appuhn, anglais d'après Elwes ;
# allemand : titres usuels (les fichiers de Stern ne les contiennent pas).
PART_TITLES = {
    "fr": {1: "De Dieu", 2: "De la nature et de l'origine de l'âme", 3: "De l'origine et de la nature des affections",
           4: "De la servitude de l'homme ou des forces des affections",
           5: "De la puissance de l'entendement ou de la liberté de l'homme"},
    "de": {1: "Von Gott", 2: "Von der Natur und dem Ursprung des Geistes", 3: "Von dem Ursprung und der Natur der Affekte",
           4: "Von der menschlichen Knechtschaft oder von der Macht der Affekte",
           5: "Von der Macht des Verstandes oder von der menschlichen Freiheit"},
    "en": {1: "Concerning God", 2: "On the Nature and Origin of the Mind", 3: "On the Origin and Nature of the Emotions",
           4: "Of Human Bondage, or the Strength of the Emotions",
           5: "Of the Power of the Understanding, or of Human Freedom"},
}


def build() -> Path:
    model = Model()
    elements, problems = load_elements(model.pos)
    latin = {int(v["number"]): v.get("title", "") for v in model.meta.values() if v["type"] == "pars"}
    langs = {code: {"name": i.get("name"), "translator": i.get("translator"), "year": i.get("year"),
                    "types": i.get("types", {}), "parts": PART_TITLES.get(code, latin) if code != "la" else latin,
                    # Mentions de provenance et de droits de l'édition numérisée, reproduites telles quelles.
                    "provenance": read_text(i["folder"], "ethica")}
             for code, i in model.langs.items()}
    data = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "langs": langs,
        "elements": elements,
        "documents": load_documents(),
        "problems": problems + model.problems,
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", payload)
    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    return OUTPUT


def snapshot():
    files = [TEMPLATE, *(ROOT / n for n in DOC_FILES), *ELEMENTS.rglob("*.md")]
    if NOTES.is_dir():
        files += list(NOTES.rglob("*.md"))
    return {str(f): f.stat().st_mtime for f in files if f.exists()}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = build()
    print(f"Écrit : {out} ({out.stat().st_size // 1024} Ko)")
    if "--watch" in sys.argv:
        print("Surveillance des modifications (Ctrl+C pour arrêter)…")
        last = snapshot()
        try:
            while True:
                time.sleep(1)
                now = snapshot()
                if now != last:
                    last = now
                    build()
                    print(f"[{datetime.now():%H:%M:%S}] régénéré")
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
