#!/usr/bin/env python3
"""Check that English feature docs and their Russian mirrors match.

Docs live in per-language folders, and a mirror has the same path under the
sibling language folder: `<feature>/en/prd.md` <-> `<feature>/ru/prd.md`.

Usage:
    check_mirror.py PATH [PATH ...]

PATH is a folder (every EN/RU pair under it is checked, recursively) or a single
.md file inside an `en/` or `ru/` folder. Markdown files outside language
folders are ignored. Exits with 1 if any mirror is missing or any pair differs.

Only structure is compared — headings, tables, lists, checkboxes, R/T/Q
IDs, inline code, links, fenced blocks and frontmatter — since prose is
expected to differ by language. Meaning still has to be checked by reading.
"""

import os
import re
import sys
from collections import Counter
from pathlib import Path

LANGS = ("en", "ru")

# Frontmatter keys whose values legitimately differ between languages.
LANG_SPECIFIC_KEYS = {"title", "lang", "mirror"}

FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([\w-]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
CHECKBOX_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
# Requirement (R1), task (T1) and open question (Q1) IDs.
REQ_ID_RE = re.compile(r"\b[RTQ]\d+\b")
CODE_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"\]\(([^)\s]+)")


def lang_of(path: Path):
    """Return (lang, index of the language folder in path.parts), or (None, None)."""
    for i in range(len(path.parts) - 2, -1, -1):
        if path.parts[i] in LANGS:
            return path.parts[i], i
    return None, None


def twin(path: Path, lang: str, index: int) -> Path:
    other = LANGS[1 - LANGS.index(lang)]
    parts = list(path.parts)
    parts[index] = other
    return Path(*parts)


def relative_link(src: Path, dst: Path) -> str:
    return os.path.relpath(dst, src.parent)


def parse_frontmatter(lines):
    """Return (dict, index of first body line). Values are raw strings, comments stripped."""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    data = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return data, i + 1
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            value = re.sub(r"\s+#.*$", "", m.group(2)).strip()
            data[m.group(1)] = value
    return data, len(lines)


def new_section(title):
    return {"title": title, "lists": 0, "checkboxes": [], "tables": [], "fences": []}


def parse(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    frontmatter, start = parse_frontmatter(lines)

    sections = [new_section("(before first heading)")]
    headings = []
    req_ids, code, links = set(), Counter(), []
    fence = None  # [marker, lang, line_count] while inside a fenced block
    table = None  # [rows, columns] while inside a table

    for line in lines[start:]:
        section = sections[-1]

        if fence:
            if line.strip().startswith(fence[0]):
                section["fences"].append((fence[1], fence[2]))
                fence = None
            else:
                fence[2] += 1
                req_ids.update(REQ_ID_RE.findall(line))
            continue
        m = FENCE_RE.match(line)
        if m:
            fence = [m.group(1), m.group(2) or "", 0]
            continue

        if line.lstrip().startswith("|"):
            if not TABLE_SEP_RE.match(line):
                cols = len(line.strip().strip("|").split("|"))
                if table is None:
                    table = [0, cols]
                    section["tables"].append(table)
                table[0] += 1
        else:
            table = None

        m = HEADING_RE.match(line)
        if m:
            headings.append(len(m.group(1)))
            sections.append(new_section(m.group(2).strip()))
            continue

        if LIST_RE.match(line):
            section["lists"] += 1
        m = CHECKBOX_RE.match(line)
        if m:
            section["checkboxes"].append(m.group(1).lower() == "x")

        req_ids.update(REQ_ID_RE.findall(line))
        code.update(c[1].strip() for c in CODE_RE.findall(line))
        links.extend(LINK_RE.findall(line))

    if fence:
        sections[-1]["fences"].append((fence[1], fence[2]))

    return {
        "frontmatter": frontmatter,
        "headings": headings,
        "sections": sections,
        "req_ids": req_ids,
        "code": code,
        "links": links,
    }


def compare(en: Path, ru: Path):
    a, b = parse(en), parse(ru)
    issues = []

    # Frontmatter
    fa, fb = a["frontmatter"], b["frontmatter"]
    if set(fa) != set(fb):
        issues.append(f"frontmatter keys differ: only EN {sorted(set(fa) - set(fb))}, only RU {sorted(set(fb) - set(fa))}")
    for key in sorted(set(fa) & set(fb) - LANG_SPECIFIC_KEYS):
        if fa[key] != fb[key]:
            issues.append(f"frontmatter '{key}' differs: EN {fa[key]!r} vs RU {fb[key]!r}")
    if fa.get("lang") != "en":
        issues.append(f"EN file must have 'lang: en' (found {fa.get('lang')!r})")
    if fb.get("lang") != "ru":
        issues.append(f"RU file must have 'lang: ru' (found {fb.get('lang')!r})")
    for src, dst, fm, name in ((en, ru, fa, "EN"), (ru, en, fb, "RU")):
        expected = relative_link(src, dst)
        if fm.get("mirror") != expected:
            issues.append(f"{name} 'mirror' should be '{expected}' (found {fm.get('mirror')!r})")

    # Headings
    if a["headings"] != b["headings"]:
        issues.append(f"heading structure differs: EN {len(a['headings'])} headings {a['headings']} vs RU {len(b['headings'])} {b['headings']}")

    # Per-section content (only meaningful when sections line up)
    for i, (sa, sb) in enumerate(zip(a["sections"], b["sections"])):
        where = f"section '{sa['title']}' / '{sb['title']}'"
        if sa["lists"] != sb["lists"]:
            issues.append(f"{where}: list items {sa['lists']} vs {sb['lists']}")
        if sa["checkboxes"] != sb["checkboxes"]:
            issues.append(f"{where}: checkboxes (checked=True) {sa['checkboxes']} vs {sb['checkboxes']}")
        ta = [tuple(t) for t in sa["tables"]]
        tb = [tuple(t) for t in sb["tables"]]
        if ta != tb:
            issues.append(f"{where}: tables (rows, columns) {ta} vs {tb}")
        if sa["fences"] != sb["fences"]:
            issues.append(f"{where}: fenced blocks (lang, lines) {sa['fences']} vs {sb['fences']}")

    # Whole-document invariants
    if a["req_ids"] != b["req_ids"]:
        issues.append(f"IDs (R/T/Q): only EN {sorted(a['req_ids'] - b['req_ids'])}, only RU {sorted(b['req_ids'] - a['req_ids'])}")
    if a["code"] != b["code"]:
        only_en = sorted((a["code"] - b["code"]).elements())
        only_ru = sorted((b["code"] - a["code"]).elements())
        issues.append(f"inline code differs (identifiers must not be translated): only EN {only_en}, only RU {only_ru}")
    if a["links"] != b["links"]:
        issues.append(f"links differ: EN {a['links']} vs RU {b['links']}")

    return issues


def collect_pairs(paths):
    pairs, errors = set(), []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files = sorted(p.rglob("*.md"))
        elif p.is_file():
            files = [p]
        else:
            errors.append(f"not found: {p}")
            continue
        for f in files:
            lang, index = lang_of(f)
            if lang is None:
                continue
            other = twin(f, lang, index)
            if not other.exists():
                errors.append(f"MISSING {other} (mirror of {f})")
                continue
            pairs.add((f, other) if lang == "en" else (other, f))
    return sorted(pairs), sorted(set(errors))


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    pairs, errors = collect_pairs(argv)
    failed = bool(errors)
    for e in errors:
        print(e)
    for en, ru in pairs:
        try:
            issues = compare(en, ru)
        except (OSError, UnicodeDecodeError) as exc:
            issues = [f"cannot read pair: {exc}"]
        if issues:
            failed = True
            print(f"FAIL {en} <-> {ru}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK   {en} <-> {ru}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
