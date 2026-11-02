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

Each file is also checked on its own: every R/T/Q ID is defined once, a task's
"Depends on" names only tasks above it (tasks are in execution order), a
"Blocked by" names a question as "PRD Qn" / "Spec Qn", "Covers" holds R IDs or
one of the labels setup / verify / rollout, and no template scaffolding is left
(<placeholders>, *(optional)* markers, YYYY-MM-DD, frontmatter comments).

A feature folder (one holding en/ or ru/ with prd.md) is checked across its
documents too: every PRD requirement is in the Spec's coverage table, every
requirement that is neither struck through nor "Not covered:" in the Spec is in
some task's "Covers", and every "PRD Qn" / "Spec Qn" reference names a question
that document defines.
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
# Where an ID is defined: a task or question header (**T1.** / ~~**T1.**~~) or a requirement row (| R1 |).
DEF_ID_RE = re.compile(r"^\s*(?:[-*+]\s+(?:\[[ xX]\]\s+)?)?~{0,2}\*\*([RTQ]\d+)\.|^\s*\|\s*([RTQ]\d+)\s*\|")
TASK_DEF_RE = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s+~{0,2}\*\*(T\d+)\.")
DEPENDS_RE = re.compile(r"^\s*[-*+]\s+(?:Depends on|Зависит от):\s*(.*)$")
BLOCKED_RE = re.compile(r"^\s*[-*+]\s+(?:Blocked by|Заблокировано):\s*(.*)$")
QUESTION_REF_RE = re.compile(r"\b(PRD|Spec) (Q\d+)\b")
COVERS_RE = re.compile(r"^\s*[-*+]\s+(?:Covers|Покрывает):\s*(.*)$")
COVERS_LABELS = {"setup", "verify", "rollout"}
REQ_ROW_RE = re.compile(r"^\s*\|\s*(R\d+)\s*\|(.*)$")
NOT_COVERED_RE = re.compile(r"^\s*\*\*(?:Not covered|Не покрыто):\*\*")
# Template scaffolding that must not survive into a real document.
PLACEHOLDER_RE = re.compile(r"<\S[^<>\n]{0,199}>")  # anything in angle brackets, except "a < b > c" prose
OPTIONAL_MARK_RE = re.compile(r"\*\((?:optional|необязательно)\)\*")
DATE_PLACEHOLDER = "YYYY-MM-DD"


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


def strip_comment(value: str) -> str:
    """Drop a trailing YAML comment: '#' preceded by whitespace outside quotes ("PR: #12 — …" is kept)."""
    quote = None
    for i, ch in enumerate(value):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and i > 0 and value[i - 1].isspace():
            return value[:i].rstrip()
    return value.strip()


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
            value = strip_comment(m.group(2))
            key = m.group(1)
            data[key] = value
            continue
        m = re.match(r"^\s+-\s+(.*)$", line)  # item of a multi-line list
        if m and data:
            item = strip_comment(m.group(1))
            data[key] = (data[key] + "\n" if data[key] else "") + item
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


def lint(path: Path):
    """Per-file checks that need no mirror: unique IDs, task order, blockers."""
    issues = []
    lines = path.read_text(encoding="utf-8").splitlines()
    _, start = parse_frontmatter(lines)
    seen = Counter()
    tasks_above = set()
    task = None  # the task whose fields we are reading
    in_fence = False
    for n, line in enumerate(lines[start:], start=start + 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = DEF_ID_RE.match(line)
        if m:
            seen[m.group(1) or m.group(2)] += 1
        m = TASK_DEF_RE.match(line)
        if m:
            if task:
                tasks_above.add(task)
            task = m.group(1)
            continue
        if task is None:
            continue
        m = DEPENDS_RE.match(line)
        if m:
            for dep in re.findall(r"\bT\d+\b", m.group(1)):
                if dep == task:
                    issues.append(f"line {n}: {task} depends on itself")
                elif dep not in tasks_above:
                    issues.append(f"line {n}: {task} depends on {dep}, which is not above it (tasks go in execution order)")
        m = BLOCKED_RE.match(line)
        if m and not QUESTION_REF_RE.search(m.group(1)):
            issues.append(f"line {n}: {task} 'Blocked by' must name a question as 'PRD Qn' or 'Spec Qn' (found {m.group(1).strip()!r})")
        m = COVERS_RE.match(line)
        if m:
            labels = [c[1].strip() for c in CODE_RE.findall(m.group(1))]
            bad = [l for l in labels if l not in COVERS_LABELS]
            if bad:
                issues.append(f"line {n}: {task} 'Covers' label must be setup, verify or rollout (found {bad})")
            rest = CODE_RE.sub("", m.group(1))
            if not labels and not re.search(r"\bR\d+\b", rest):
                issues.append(f"line {n}: {task} 'Covers' names neither requirement IDs nor a label")
    for id_, count in sorted(seen.items()):
        if count > 1:
            issues.append(f"ID {id_} is defined {count} times")
    issues.extend(lint_scaffolding(lines, start))
    return issues


def lint_scaffolding(lines, start):
    """Template leftovers: <placeholders>, *(optional)* markers, YYYY-MM-DD, frontmatter comments."""
    issues = []
    for n, line in enumerate(lines[:start], start=1):
        m = re.match(r"^(?:[\w-]+:|\s+-)\s*(.*)$", line)
        if m and strip_comment(m.group(1)) != m.group(1).strip():
            issues.append(f"line {n}: frontmatter comment left from the template")
    in_fence = False
    for n, line in enumerate(lines[start:], start=start + 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = CODE_RE.sub("", line)
        for m in PLACEHOLDER_RE.finditer(prose):
            issues.append(f"line {n}: placeholder {m.group(0)!r} left from the template")
        if OPTIONAL_MARK_RE.search(prose):
            issues.append(f"line {n}: '(optional)' marker left from the template")
        if DATE_PLACEHOLDER in line:
            issues.append(f"line {n}: '{DATE_PLACEHOLDER}' left from the template")
    for n, line in enumerate(lines[:start], start=1):
        if DATE_PLACEHOLDER in line:
            issues.append(f"line {n}: '{DATE_PLACEHOLDER}' left from the template")
    return issues


def body_lines(path: Path):
    """Lines outside fenced blocks."""
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


def requirement_rows(path: Path):
    """R IDs from a document's tables: {id: struck_through}."""
    rows = {}
    for line in body_lines(path):
        m = REQ_ROW_RE.match(line)
        if m:
            rows[m.group(1)] = "~~" in m.group(2)
    return rows


def not_covered_rows(path: Path):
    """R IDs whose coverage cell starts with 'Not covered:'."""
    ids = set()
    for line in body_lines(path):
        m = REQ_ROW_RE.match(line)
        if m and NOT_COVERED_RE.match(m.group(2).split("|")[0].strip()):
            ids.add(m.group(1))
    return ids


def question_defs(path: Path):
    """Q IDs the document defines."""
    ids = set()
    for line in body_lines(path):
        m = DEF_ID_RE.match(line)
        if m and (m.group(1) or m.group(2)).startswith("Q"):
            ids.add(m.group(1) or m.group(2))
    return ids


def question_refs(path: Path):
    """{(document, Q ID)} the document refers to as 'PRD Qn' / 'Spec Qn'."""
    refs = set()
    for line in body_lines(path):
        refs.update(QUESTION_REF_RE.findall(line))
    return refs


def covered_in_tasks(path: Path):
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = COVERS_RE.match(line)
        if m:
            ids.update(re.findall(r"\bR\d+\b", CODE_RE.sub("", m.group(1))))
    return ids


def check_feature(folder: Path):
    """Cross-document checks for one language folder of a feature."""
    issues = []
    prd, spec, tasks = folder / "prd.md", folder / "spec.md", folder / "tasks.md"
    if not prd.exists():
        return issues
    reqs = requirement_rows(prd)
    if spec.exists():
        covered = set(requirement_rows(spec))
        for r in sorted(set(reqs) - covered, key=lambda s: int(s[1:])):
            issues.append(f"{spec.name}: {r} from the PRD is missing in Requirements coverage")
        for r in sorted(covered - set(reqs), key=lambda s: int(s[1:])):
            issues.append(f"{spec.name}: {r} in Requirements coverage is not in the PRD")
    if tasks.exists():
        covered = covered_in_tasks(tasks)
        live = {r for r, struck in reqs.items() if not struck}
        if spec.exists():
            live -= not_covered_rows(spec)
        for r in sorted(live - covered, key=lambda s: int(s[1:])):
            issues.append(f"{tasks.name}: {r} is in no task's Covers")
        for r in sorted(covered - set(reqs), key=lambda s: int(s[1:])):
            issues.append(f"{tasks.name}: Covers names {r}, which is not in the PRD")
    defined = {"PRD": question_defs(prd), "Spec": question_defs(spec) if spec.exists() else set()}
    for doc in (prd, spec, tasks):
        if not doc.exists():
            continue
        for where, q in sorted(question_refs(doc), key=lambda r: (r[0], int(r[1][1:]))):
            if q not in defined[where]:
                issues.append(f"{doc.name}: refers to {where} {q}, which {where.lower()}.md does not define")
    return issues


def collect_features(paths):
    folders = set()
    for raw in paths:
        p = Path(raw)
        candidates = [p] if p.is_file() else list(p.rglob("prd.md")) if p.is_dir() else []
        for f in candidates:
            lang, index = lang_of(f)
            if lang is not None:
                folders.add(Path(*f.parts[: index + 1]))
    return sorted(folders)


def compare(en: Path, ru: Path):
    a, b = parse(en), parse(ru)
    issues = []
    for name, path in (("EN", en), ("RU", ru)):
        issues.extend(f"{name}: {issue}" for issue in lint(path))

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
    for folder in collect_features(argv):
        issues = check_feature(folder)
        if issues:
            failed = True
            print(f"FAIL {folder} (across documents)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK   {folder} (across documents)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
