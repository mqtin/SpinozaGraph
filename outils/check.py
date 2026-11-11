#!/usr/bin/env python3
"""Contrôles de cohérence du graphe. Code de sortie 1 en cas d'erreur.

- comptages connus (propositions par partie) ;
- aucun renvoi vers un élément inexistant ;
- aucun cycle parmi les arêtes logiques et structurelles ;
- chaque langue couvre chaque élément ;
- corrections valides ;
- elements/ à jour par rapport aux sources (generate.py relancé).

Usage : python outils/check.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ethica import Model, read_text  # noqa: E402

# Nombre de propositions par partie (Gebhardt) : 36, 49, 59, 73, 42 = 259
PROPS_PAR_PARTIE = {1: 36, 2: 49, 3: 59, 4: 73, 5: 42}


def structural_edges(m: Model):
    """Arêtes implicites tirées de la structure : (appui, dépendant)."""
    for e in m.elements:
        p = m.element_parent(e)
        if not p:
            continue
        t = m.etype(e)
        if t in ("corollaire", "scolie"):
            yield p, e        # le corollaire découle de sa proposition ; la scolie la commente
        elif t == "aliter":
            yield e, p        # l'autre démonstration établit sa proposition


def find_cycles(nodes, edges):
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
    color, cycles = {}, []

    def dfs(v, path):
        color[v] = 1
        path.append(v)
        for w in adj[v]:
            if color.get(w) == 1:
                cycles.append(path[path.index(w):] + [w])
            elif not color.get(w):
                dfs(w, path)
        path.pop()
        color[v] = 2

    sys.setrecursionlimit(10000)
    for n in nodes:
        if not color.get(n):
            dfs(n, [])
    return cycles


def run(m: Model) -> tuple[list[str], list[str]]:
    errors, warnings = list(m.problems), []
    els = set(m.elements)

    props = Counter(m.part(e) for e in m.elements if m.etype(e) == "proposition")
    for part, n in PROPS_PAR_PARTIE.items():
        if props[part] != n:
            errors.append(f"partie {part} : {props[part]} propositions au lieu de {n}")

    for e in m.elements:
        for x in m.logique[e] + m.voir[e]:
            if x not in els:
                errors.append(f"{e} cite {x}, qui n'est pas un élément")

    edges = [(d, e) for e in m.elements for d in m.logique[e]] + list(structural_edges(m))
    for c in find_cycles(m.elements, edges):
        errors.append("cycle : " + " → ".join(c))

    # renvois logiques vers l'avant : suspects (permis seulement s'ils sont justifiés par une correction)
    for e in m.elements:
        for d in m.logique[e]:
            if m.pos[d] > m.pos[e]:
                warnings.append(f"renvoi logique vers l'avant : {e} → {d}")

    for code, info in m.langs.items():
        missing = [e for e in m.elements if not read_text(info["folder"], e)]
        if missing:
            warnings.append(f"{code} : {len(missing)} élément(s) sans texte : {', '.join(missing[:10])}")

    ids = [c.get("id") for c in m.corrections]
    for i, n in Counter(ids).items():
        if n > 1:
            errors.append(f"correction {i} : identifiant en double")
    for c in m.corrections:
        for f in ("id", "op", "de", "vers", "note", "source"):
            if not c.get(f):
                errors.append(f"correction {c.get('id', '?')} : champ « {f} » manquant")

    root = Path(__file__).resolve().parent.parent / "elements"
    on_disk = {p.stem for p in root.rglob("*.md")} if root.exists() else set()
    if on_disk != els:
        errors.append(f"elements/ n'est pas à jour ({len(on_disk ^ els)} écart(s)) : relancez outils/generate.py")
    return errors, warnings


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    m = Model()
    errors, warnings = run(m)
    types = Counter(m.etype(e) for e in m.elements)
    print(f"{len(m.elements)} éléments : " + ", ".join(f"{k} {v}" for k, v in sorted(types.items())))
    print(f"{sum(map(len, m.logique.values()))} renvois logiques, {sum(map(len, m.voir.values()))} renvois « voir », "
          f"{len(m.corrections)} correction(s)")
    for w in warnings:
        print("avertissement :", w)
    for e in errors:
        print("ERREUR :", e)
    print("OK" if not errors else f"{len(errors)} erreur(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
