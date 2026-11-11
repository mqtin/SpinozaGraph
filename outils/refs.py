"""Repère les renvois dans le texte de chaque langue et en fait des liens [[id|texte]].

Principe : un analyseur par langue (latin, Appuhn, Elwes) repère les expressions de renvoi
(« per propositionem 36 partis I », « Prop. 36, p. I », « I. xxxvi. ») et propose des identifiants.
Un lien n'est créé que si l'identifiant fait partie des renvois connus de l'élément (meta.json,
après corrections) : on ne devine jamais une cible. Les langues sans analyseur restent sans liens.
"""
from __future__ import annotations

import re

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}


def roman(s: str) -> int | None:
    s = s.lower().strip(". ")
    if s.isdigit():
        return int(s)
    if not s or any(c not in ROMAN for c in s):
        return None
    total, prev = 0, 0
    for c in reversed(s):
        v = ROMAN[c]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total


class Item:
    """Un renvoi repéré : position dans le texte et identifiants candidats, par ordre de préférence."""

    def __init__(self, start: int, end: int, cands: list[str], kind: str = "", num: int | None = None):
        self.start, self.end, self.cands, self.kind, self.num = start, end, cands, kind, num


def ids_for(kind: str, part: int, num: int, sub: str = "", subn: int | None = None) -> list[str]:
    """Identifiants possibles (format lou/ethica) pour un renvoi."""
    if kind == "p":
        base = f"{part}p{num}"
    elif kind == "def":
        base = f"{part}def{num}"
    elif kind == "ax":
        return [f"{part}ax{num}", f"2p13ax{num}", f"2p13ax{num}a"]
    elif kind == "post":
        return [f"{part}post{num}", f"2p13post{num}"]
    elif kind == "l":
        base = f"2p13l{num}"
    elif kind == "ad":
        return [f"3ad{num}"]
    elif kind == "cap":
        return [f"4appc{num}"]
    else:
        return []
    if not sub:
        return [base]
    if sub == "c":
        return [f"{base}c{subn}" if subn else f"{base}c", f"{base}c1", f"{base}c"]
    if sub == "sc":
        return [f"{base}sc{subn}" if subn else f"{base}sc", f"{base}sc1", f"{base}csc"]
    return [base]


def list_items(m: re.Match, group: str, kind: str, part: int) -> list[Item]:
    """Une liste de numéros (« 6 et 7 ») : le premier lien couvre toute l'expression, les suivants leur numéro."""
    nums = list(re.finditer(r"\d+", m.group(group)))
    out = []
    for i, x in enumerate(nums):
        n = int(x.group())
        s, e = m.start(group) + x.start(), m.start(group) + x.end()
        if i == 0:
            s, e = m.start(), (e if len(nums) > 1 else m.end())
        out.append(Item(s, e, ids_for(kind, part, n), kind, n))
    return out


# --- latin -------------------------------------------------------------------
LA_KIND = {"propositi": "p", "definiti": "def", "axiom": "ax", "postulat": "post", "lemm": "l"}
LA_RE = re.compile(r"""
    (?P<agd>affectuum\s+generalem\s+definitionem|generalem\s+affectuum\s+definitionem)
  | (?P<af>(?P<afn>\d+(?:\s*(?:,|et)\s*\d+)*)\s+affectuum\s+definitio\w*|affectuum\s+definitio\w*\s+(?P<afn2>\d+(?:\s*(?:,|et)\s*\d+)*)|definitio\w*\s+(?P<afn3>\d+(?:\s*(?:,|et)\s*\d+)*)\s+affectuum)
  | (?:(?P<subn0>\d+|[IVX]+)\s+)?(?P<sub>corollari\w*|scholi\w*)(?:\s+(?P<subn>\d+|[IVX]+)\b)?\s+(?P<subof>propositionis|propositionum|lemmatis)\s+(?P<n1>\d+(?:\s*(?:,|et)\s*\d+)*)
  | (?P<axh>axioma)(?=\s+hujus)
  | (?P<ejus>(?:ejus|ejusdem)\s+(?P<ejsub>corollari\w*|scholi\w*))
  | (?P<prev>præcedent\w*|praecedent\w*)
  | (?P<kind>propositi\w*|definiti\w*|axiom\w*|postulat\w*|lemm\w*)\s+(?P<nums>\d+(?:\s*(?:,|et)\s*\d+)*)
""", re.X | re.I)
LA_PART = re.compile(r"\s+(?:hujus|partis\s+(?P<part>[IVX]+|\d+))", re.I)


def la_kind(word: str) -> str:
    w = word.lower()
    return next((v for k, v in LA_KIND.items() if w.startswith(k)), "")


def parse_la(text: str, part: int) -> list[Item]:
    items, last_p = [], None
    for m in LA_RE.finditer(text):
        tail = LA_PART.match(text, m.end())
        p = part
        end = m.end()
        if tail:
            if tail.group("part"):
                p = roman(tail.group("part")) or part
            end = tail.end()
        if m.group("agd"):
            items.append(Item(m.start(), m.end(), ["3agd"]))
        elif m.group("axh"):
            items.append(Item(m.start(), end, [f"{part}ax"]))
        elif m.group("af"):
            g = next(k for k in ("afn", "afn2", "afn3") if m.group(k))
            items += list_items(m, g, "ad", 3)
        elif m.group("sub"):
            sub = "c" if m.group("sub").lower().startswith("c") else "sc"
            sn = m.group("subn") or m.group("subn0")
            subn = roman(sn) if sn else None
            kind = "l" if m.group("subof").lower().startswith("lem") else "p"
            for n in map(int, re.findall(r"\d+", m.group("n1"))):
                items.append(Item(m.start(), end, ids_for(kind, p, n, sub, subn), kind, n))
                last_p = (kind, p, n)
        elif m.group("ejus"):
            if last_p:
                sub = "c" if m.group("ejsub").lower().startswith("c") else "sc"
                items.append(Item(m.start(), m.end(), ids_for(last_p[0], last_p[1], last_p[2], sub)))
        elif m.group("prev"):
            items.append(Item(m.start(), m.end(), [], "prev"))
        else:
            kind = la_kind(m.group("kind"))
            nums = [(int(x.group()), x.start(), x.end()) for x in re.finditer(r"\d+", m.group("nums"))]
            off = m.start("nums")
            for i, (n, s, e) in enumerate(nums):
                start = m.start() if i == 0 else off + s
                stop = off + e if i < len(nums) - 1 else end
                items.append(Item(start, stop, ids_for(kind, p, n), kind, n))
                last_p = (kind, p, n)
    return items


# --- français (Appuhn) ---------------------------------------------------------
FR_KIND = {"prop": "p", "déf": "def", "def": "def", "ax": "ax", "post": "post", "lem": "l"}
FR_RE = re.compile(r"""
    (?P<agd>Déf(?:\.|inition)\s+gén(?:\.|érale)\s+des\s+(?:Aff\.|Affections))
  | (?P<af>Déf(?:\.|initions?)\s*(?P<afn>\d+(?:\*?\s*(?:,|et)\s*\*?\d+)*)\s+des\s+(?:Aff\.|Affections))
  | (?P<sub>Coroll\.|Corollaire|Scolie|Schol\.)\s*(?P<subn>\d+)?\s*(?:de\s+la\s+|du\s+|de\s+)?(?P<subof>Prop\.|Propos\.|Proposition|Lemme)\s*(?:(?P<n1>\d+)|(?P<subprev>préc\w*\.?))
  | (?P<son>(?:son|le)\s+(?P<sonsub>Coroll\.|Corollaire|Scolie))
  | (?P<prev>Prop(?:\.|os\.|osition)\s+préc\w*\.?)
  | (?P<kind>Prop(?:\.|os\.|ositions?)|Déf(?:\.|initions?)|Ax(?:\.|iomes?)|Post(?:\.|ul\.|ulats?)|Lemmes?)\s*(?P<nums>\d+(?:\*?\s*(?:,|et)\s*\*?\d+)*)
""", re.X)
FR_PART = re.compile(r"\s*,?\s*(?:p\.|partie)\s*(?P<part>[IVX]+)\b\.?|\s+de\s+la\s+(?P<pw>première|deuxième|seconde|troisième|quatrième|cinquième)\s+partie", re.I)
FR_ORD = {"première": 1, "deuxième": 2, "seconde": 2, "troisième": 3, "quatrième": 4, "cinquième": 5}


def fr_kind(word: str) -> str:
    w = word.lower()
    return next((v for k, v in FR_KIND.items() if w.startswith(k)), "")


def parse_fr(text: str, part: int) -> list[Item]:
    items, last_p = [], None
    for m in FR_RE.finditer(text):
        tail = FR_PART.match(text, m.end())
        p, end = part, m.end()
        if tail:
            p = roman(tail.group("part")) if tail.group("part") else FR_ORD[tail.group("pw").lower()]
            end = tail.end()
        if m.group("agd"):
            items.append(Item(m.start(), m.end(), ["3agd"]))
        elif m.group("af"):
            items += list_items(m, "afn", "ad", 3)
        elif m.group("sub") and m.group("subprev"):
            sub = "c" if m.group("sub").lower().startswith("c") else "sc"
            items.append(Item(m.start(), m.end(), [], "prev" + sub))
        elif m.group("sub"):
            sub = "c" if m.group("sub").lower().startswith("c") else "sc"
            kind = "l" if m.group("subof").lower().startswith("lem") else "p"
            n = int(m.group("n1"))
            items.append(Item(m.start(), end, ids_for(kind, p, n, sub, int(m.group("subn")) if m.group("subn") else None), kind, n))
            last_p = (kind, p, n)
        elif m.group("son"):
            if last_p:
                sub = "c" if m.group("sonsub").lower().startswith("c") else "sc"
                items.append(Item(m.start("sonsub"), m.end(), ids_for(last_p[0], last_p[1], last_p[2], sub)))
        elif m.group("prev"):
            items.append(Item(m.start(), m.end(), [], "prev"))
        else:
            kind = fr_kind(m.group("kind"))
            nums = [(int(x.group()), x.start(), x.end()) for x in re.finditer(r"\d+", m.group("nums"))]
            off = m.start("nums")
            for i, (n, s, e) in enumerate(nums):
                start = m.start() if i == 0 else off + s
                stop = off + e if i < len(nums) - 1 else end
                items.append(Item(start, stop, ids_for(kind, p, n), kind, n))
                last_p = (kind, p, n)
    return items


# --- anglais (Elwes) -----------------------------------------------------------
EN_KIND = {"def": "def", "ax": "ax", "post": "post", "prop": "p", "lem": "l"}
EN_RE = re.compile(r"""
    (?P<af>Def(?:\.|inition)?\s+of\s+(?:the\s+)?Emotions?\s*,?\s*(?P<afn>[ivxl]+|\d+)\b\.?)
  | (?P<lastp>(?:the\s+)?(?:last|preceding|previous)\s+Prop(?:\.|osition))
  | (?:(?P<kp>\b[IV]{1,3})\.\s*)?(?P<kind>Deff\.|Def\.|Definitions?|Axiom\.|Axioms?|Ax\.|Post\.|Postulates?|Prop\.|Propositions?|Prop|Lemmas?|Lem\.)\s*(?P<kn>[ivxl]+|\d+)\b\.?(?P<kmore>(?:\s*,?\s*(?:and\s+)?(?:[ivxl]+|\d+)\b\.?(?!\s*[A-Z]))*)
  | (?P<pp>\b[IV]{1,3})\.\s*(?P<pn>[ivxl]+)\b\.?(?P<more>(?:\s*,?\s*(?:and\s+)?[ivxl]+\b\.?(?!\s*[A-Z]))*)
      (?P<sx>\s*[;,]?\s*(?P<and>and\s+)?(?P<sub>Coroll\.|Corollary|note|Note)(?:\s*(?P<subn>[ivx]+)\b\.?)?)?
""", re.X)


def parse_en(text: str, part: int) -> list[Item]:
    items = []
    for m in EN_RE.finditer(text):
        if m.group("af"):
            n = roman(m.group("afn"))
            items.append(Item(m.start(), m.end(), ids_for("ad", 3, n), "ad", n))
        elif m.group("lastp"):
            items.append(Item(m.start(), m.end(), [], "prev"))
        elif m.group("kind"):
            kind = next((v for k, v in EN_KIND.items() if m.group("kind").lower().startswith(k)), "")
            p = roman(m.group("kp")) if m.group("kp") else part
            n = roman(m.group("kn"))
            kn_end = m.end("kn") + (1 if text[m.end("kn"):m.end("kn") + 1] == "." else 0)
            if n:
                items.append(Item(m.start(), kn_end, ids_for(kind, p, n), kind, n))
            for x in re.finditer(r"[ivxl]+|\d+", m.group("kmore") or ""):
                n2 = roman(x.group())
                if n2:
                    items.append(Item(m.start("kmore") + x.start(), m.start("kmore") + x.end(), ids_for(kind, p, n2), kind, n2))
        else:
            p, n = roman(m.group("pp")), roman(m.group("pn"))
            if not p or not n or p > 5:
                continue
            sub = ""
            if m.group("sub"):
                sub = "c" if m.group("sub").lower().startswith("c") else "sc"
            subn = roman(m.group("subn")) if m.group("subn") else None
            more = [roman(x) for x in re.findall(r"[ivxl]+", m.group("more") or "")]
            if sub and m.group("and"):
                items.append(Item(m.start(), m.end("pn"), ids_for("p", p, n), "p", n))
                items.append(Item(m.start("sub"), m.end(), ids_for("p", p, n, sub, subn), "p", n))
            elif sub and not more:
                items.append(Item(m.start(), m.end(), ids_for("p", p, n, sub, subn), "p", n))
            else:
                items.append(Item(m.start(), m.end("pn") + (1 if text[m.end("pn"):m.end("pn") + 1] == "." else 0), ids_for("p", p, n), "p", n))
                for x in re.finditer(r"[ivxl]+\b\.?", m.group("more") or ""):
                    n2 = roman(x.group())
                    if n2:
                        s = m.start("more") + x.start()
                        items.append(Item(s, m.start("more") + x.end(), ids_for("p", p, n2), "p", n2))
                if sub:
                    items.append(Item(m.start("sub"), m.end(), ids_for("p", p, more[-1] if more else n, sub, subn), "p", n))
    return items


# --- allemand (Stern ; tolère aussi les abréviations d'Auerbach) ------------------
DE_NUM = r"(?:\d+|[IVXL]+\b)"
DE_LIST = rf"{DE_NUM}(?:\s*(?:,|und)\s*{DE_NUM})*"
DE_KIND = {"lehrs": "p", "def": "def", "ax": "ax", "post": "post", "hilfs": "l", "lehns": "l"}
DE_RE = re.compile(rf"""
    (?P<agd>allgemeinen\s+Definition\s+der\s+Affekte)
  | (?P<af>Definitionen?\s+der\s+Affekte\s*,?\s*Ziffer\s+(?P<afn>{DE_LIST})|Def(?:\.|initionen?)\s*(?P<afn2>{DE_LIST})\s+der\s+Affekte)
  | (?P<sub>Zusatz|Zusätze|Folgesatz|Anmerkung|Anm\.)\s*(?P<subn>{DE_NUM})?\s+zu(?:m)?\s+(?:(?P<subof>Lehrsatz|Hilfssatz)\s*(?P<n1>\d+)|(?P<subprev>(?:dem\s+)?(?:vorigen|vorhergehenden|obigen)\s+Lehrsatz))
  | (?P<son>(?:seiner|dessen|deren|der)\s+(?P<sonsub>Anmerkung|Anm\.|Zusatz|Folgesatz))
  | (?P<prev>(?:dem\s+)?(?:vorigen|vorhergehenden|obigen)\s+Lehrsatz)
  | (?P<kind>Lehrsätzen|Lehrsatz|Lehrs\.|Definitionen|Definition|Def\.|Axiomen|Axiom|Ax\.|Postulaten|Postulat|Post\.|Hilfssatz|Lehnsatz)\s*(?P<nums>{DE_LIST})
""", re.X)
DE_PART = re.compile(r"\s*(?:dieses\s+Teils|,\s*(?:Teil|T\.)\s*(?P<part>\d+|[IVX]+)\b)")


def parse_de(text: str, part: int) -> list[Item]:
    items, last_p = [], None
    for m in DE_RE.finditer(text):
        tail = DE_PART.match(text, m.end())
        p, end = part, m.end()
        if tail:
            if tail.group("part"):
                p = roman(tail.group("part")) or part
            end = tail.end()
        if m.group("agd"):
            items.append(Item(m.start(), m.end(), ["3agd"]))
        elif m.group("af"):
            g = "afn" if m.group("afn") else "afn2"
            nums = list(re.finditer(DE_NUM, m.group(g)))
            for i, x in enumerate(nums):
                n = roman(x.group())
                s, e = (m.start(), m.end()) if i == 0 else (m.start(g) + x.start(), m.start(g) + x.end())
                if n:
                    items.append(Item(s, e, ids_for("ad", 3, n), "ad", n))
        elif m.group("sub"):
            sub = "sc" if m.group("sub").lower().startswith("anm") else "c"
            subn = roman(m.group("subn")) if m.group("subn") else None
            if m.group("subprev"):
                items.append(Item(m.start(), m.end(), [], "prev" + sub))
                continue
            kind = "l" if m.group("subof").lower().startswith("hilf") else "p"
            n = int(m.group("n1"))
            items.append(Item(m.start(), end, ids_for(kind, p, n, sub, subn), kind, n))
            last_p = (kind, p, n)
        elif m.group("son"):
            if last_p:
                sub = "sc" if m.group("sonsub").lower().startswith("anm") else "c"
                items.append(Item(m.start("sonsub"), m.end(), ids_for(last_p[0], last_p[1], last_p[2], sub)))
        elif m.group("prev"):
            items.append(Item(m.start(), m.end(), [], "prev"))
        else:
            kind = next((v for k, v in DE_KIND.items() if m.group("kind").lower().startswith(k)), "")
            nums = list(re.finditer(DE_NUM, m.group("nums")))
            off = m.start("nums")
            for i, x in enumerate(nums):
                n = roman(x.group())
                if not n:
                    continue
                start = m.start() if i == 0 else off + x.start()
                stop = off + x.end() if i < len(nums) - 1 else end
                items.append(Item(start, stop, ids_for(kind, p, n), kind, n))
                last_p = (kind, p, n)
    return items


PARSERS = {"la": parse_la, "fr": parse_fr, "en": parse_en, "de": parse_de}


def link(text: str, lang: str, part: int, targets: list[str], prev_ids: list[str]) -> tuple[str, set[str]]:
    """Remplace les renvois reconnus par [[id|texte]] ; renvoie le texte et les ids liés.

    targets : renvois connus de l'élément (ids d'éléments) ; prev_ids : candidats pour « la précédente ».
    """
    parser = PARSERS.get(lang)
    if not parser or not targets:
        return text, set()
    allowed = set(targets)
    chosen: list[tuple[int, int, str]] = []
    for it in parser(text, part):
        if it.kind.startswith("prev"):
            suffix = it.kind[4:]
            cid = next((c + suffix for c in prev_ids if c + suffix in allowed), None)
            if not cid and suffix:
                cid = next((c + suffix + "1" for c in prev_ids if c + suffix + "1" in allowed), None)
        else:
            cid = next((c for c in it.cands if c in allowed), None)
            if not cid and it.kind and it.num:
                # numéro juste mais partie fausse (erreur fréquente chez Elwes) : seulement si sans ambiguïté
                same = [t for t in allowed if re.fullmatch(rf"\d(?:p13)?{_kind_tag(it.kind)}{it.num}", t)]
                cid = same[0] if len(same) == 1 else None
        if cid:
            chosen.append((it.start, it.end, cid))
    # pas de chevauchement : on garde le premier
    out, last, linked = [], 0, set()
    for s, e, cid in sorted(chosen):
        if s < last:
            continue
        label = re.sub(r"\s+", " ", text[s:e]).replace("|", "/").replace("]", ")").replace("[", "(")
        out.append(text[last:s])
        out.append(f"[[{cid}|{label}]]")
        last = e
        linked.add(cid)
    out.append(text[last:])
    return "".join(out), linked


def _kind_tag(kind: str) -> str:
    return {"p": "p", "def": "def", "ax": "ax", "post": "post", "l": "l", "ad": "ad", "cap": "appc"}.get(kind, kind)
