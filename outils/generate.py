#!/usr/bin/env python3
"""Génère elements/<partie>/<id>.md à partir de sources/ethica et de corrections.yaml.

Les fichiers générés sont écrasés à chaque exécution : n'y faites aucune modification à la main
(voir DEVELOPMENT.md). Les fichiers qui ne correspondent plus à aucun élément sont supprimés.

Usage : python outils/generate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ethica import LANGS, ROOT, Model, norm_type, read_text  # noqa: E402
from refs import link  # noqa: E402

import yaml  # noqa: E402

OUT = ROOT / "elements"
HEADER = "<!-- Fichier généré par outils/generate.py : ne pas modifier. Corrections : corrections.yaml ; notes : notes/. -->"


STATS: dict[str, list[int]] = {}  # langue -> [renvois attendus, renvois liés]


def previous_prop(m: Model, eid: str) -> list[str]:
    """Candidats pour « la précédente » : dans un corollaire ou une scolie, d'abord sa propre
    proposition ; puis la proposition (ou le lemme) qui précède."""
    base = m.fold_target(eid)
    out = [base] if base != eid else []
    num = m.meta[base].get("number")
    if isinstance(num, int) and num > 1:
        out.append(f"{base[: len(base) - len(str(num))]}{num - 1}")
    return out


def yaml_list(xs):
    return "[" + ", ".join(xs) + "]"


def render(m: Model, eid: str) -> str:
    v = m.meta[eid]
    parent = m.element_parent(eid)
    fm = {
        "id": eid,
        "type": m.etype(eid),
        "type_la": norm_type(v["type"]),
        "partie": m.part(eid),
        "numero": v.get("number"),
        "parent": parent,
        "repli": m.fold_target(eid) if m.fold_target(eid) != eid else None,
    }
    lines = ["---"]
    for k, val in fm.items():
        lines.append(f"{k}: {yaml.safe_dump(val, allow_unicode=True, default_flow_style=True).strip().removesuffix('...').strip()}")
    lines.append(f"depends_on: {yaml_list(m.logique[eid])}")
    lines.append(f"voir: {yaml_list(m.voir[eid])}")
    lines.append(f"corrections: {yaml_list(m.applied[eid])}")
    lines += ["---", "", HEADER, ""]
    merged = m.merged_children(eid)
    targets = m.logique[eid] + m.voir[eid]
    prev = previous_prop(m, eid)
    for code, info in m.langs.items():
        folder = info["folder"]
        lines.append(f"## {code}")
        lines.append("")
        own = read_text(folder, eid)
        if own:
            own, got = link(own, code, m.part(eid), targets, prev)
            STATS[code][1] += len(got)
            lines += [own, ""]
        for c in merged:
            t = read_text(folder, c)
            if not t:
                continue
            t, got = link(t, code, m.part(eid), targets, prev)
            STATS[code][1] += len(got)
            name = info["types"].get(norm_type(m.meta[c]["type"]), m.meta[c]["type"])
            num = m.meta[c].get("number")
            lines += [f"### {name}{' ' + str(num) if num is not None else ''}", "", t, ""]
    links = []
    if parent:
        links.append(f"Rattaché à : [[{parent}]]")
    if m.logique[eid]:
        links.append("Appuis : " + " · ".join(f"[[{x}]]" for x in m.logique[eid]))
    if m.voir[eid]:
        links.append("Voir : " + " · ".join(f"[[{x}]]" for x in m.voir[eid]))
    if links:
        lines += ["## Liens", ""] + [l + "  " for l in links] + [""]
    return "\n".join(lines).rstrip() + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    m = Model()
    for code in m.langs:
        STATS[code] = [0, 0]
    written = set()
    for eid in m.elements:
        path = OUT / str(m.part(eid)) / f"{eid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = render(m, eid)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8", newline="\n")
        written.add(path.resolve())
    removed = 0
    for p in OUT.rglob("*.md"):
        if p.resolve() not in written:
            p.unlink()
            removed += 1
    print(f"{len(written)} éléments écrits dans {OUT.relative_to(ROOT)}/ ({removed} obsolètes supprimés)")
    print(f"langues : {', '.join(f'{k} ({v})' for k, v in LANGS.items())}")
    expected = sum(len(m.logique[e]) + len(m.voir[e]) for e in m.elements)
    print("renvois rendus cliquables (cibles distinctes par élément) : " + ", ".join(
        f"{k} {v[1]}/{expected} ({100 * v[1] / expected:.0f} %)" for k, v in STATS.items()))
    if m.problems:
        print(f"{len(m.problems)} problème(s) :")
        for p in m.problems:
            print("  -", p)


if __name__ == "__main__":
    main()
