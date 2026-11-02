#!/usr/bin/env python3
"""Check feature docs: each file on its own, every EN/RU pair, and each feature across its documents.

Docs live in per-language folders, and a mirror has the same path under the
sibling language folder: `<feature>/en/prd.md` <-> `<feature>/ru/prd.md`.

Usage:
    check_mirror.py PATH [PATH ...]

PATH is a feature folder (or any folder above several), or one of its prd.md /
spec.md / tasks.md files. Other Markdown files, and files outside an `en/` or
`ru/` folder, are reported as ignored. Exit status: 0 all checks pass, 1 any
check fails or a mirror is missing, 2 nothing was checked.

Each file is checked on its own, mirror or not:
- frontmatter: present, every key of its template filled, `type` matches the
  file name, `lang` matches the folder, `status` one of draft / review /
  approved / shipped / deprecated, `created` and `updated` real dates with
  `updated` no earlier, `prd:` / `spec:` / `tasks:` naming files that exist,
  `mirror:` pointing at the twin;
- headings: H1 ends with the template's suffix; every H2 and every template H3
  is the template's, in the template's order, no required section missing;
  deeper subsections are free;
- IDs: every T / Q header (`**T1.**`) and every R row in the requirements table
  defined once; a bold ID without the period is reported;
- tasks: each has exactly one "Covers" (R IDs, or one label setup / verify /
  rollout, never both), "Depends on" names tasks above it, "Blocked by" names a
  question as "PRD Qn" / "Spec Qn" or is "—";
- no template scaffolding: <placeholders>, *(optional)* markers, YYYY-MM-DD,
  frontmatter comments.

An EN/RU pair is compared structurally, since prose differs by language:
frontmatter (except title / lang / mirror), heading levels with sections paired
by their position in the templates (Summary <-> Кратко), per section the list
items, checkbox states, table shapes and fenced blocks (byte-identical, except
Mermaid, where node IDs, participants and arrows are compared and labels are
ignored), and over the whole file the R/T/Q IDs, inline code and links.
Meaning still has to be checked by reading.

A feature folder is checked across its documents, per language: every
requirement (the PRD's table, or the Spec's *Context & current state* table
when there is no PRD) is in the Spec's coverage table, every requirement that
is neither struck through nor "Not covered:" is in some task's "Covers", and
every "PRD Qn" / "Spec Qn" reference names a question that document defines.
"""

import datetime
import hashlib
import os
import re
import sys
from collections import Counter
from pathlib import Path

LANGS = ("en", "ru")
DOC_NAMES = ("prd", "spec", "tasks")
STATUSES = ("draft", "review", "approved", "shipped", "deprecated")
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "assets" / "templates"
NONE_MARK = "—"
DATE_PLACEHOLDER = "YYYY-MM-DD"

# Frontmatter: keys every document has, sibling links per document, keys that differ between languages.
COMMON_KEYS = ("type", "title", "feature", "lang", "mirror", "status", "owner", "reviewers", "created", "updated", "links")
SIBLING_KEYS = {"prd": ("spec", "tasks"), "spec": ("prd", "tasks"), "tasks": ("prd", "spec")}
LANG_SPECIFIC_KEYS = {"title", "lang", "mirror"}

# Sections whose tables hold requirement rows (| R1 | …), in both languages.
REQUIREMENT_SECTIONS = {"Requirements", "Требования"}
COVERAGE_SECTIONS = {"Requirements coverage", "Покрытие требований"}
CONTEXT_SECTIONS = {"Context & current state", "Контекст и текущее состояние"}  # a Spec without a PRD defines its requirements here
DEFINITION_SECTIONS = {"prd": REQUIREMENT_SECTIONS, "spec": CONTEXT_SECTIONS, "tasks": set()}
COVERS_LABELS = {"setup", "verify", "rollout"}

FENCE_OPEN_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w-]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
CHECKBOX_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
# Requirement (R1), task (T1) and open question (Q1) IDs; "Q4 2026" is a quarter, not a question.
ID_RE = re.compile(r"\b([RTQ]\d+)\b(?!\s*\d{4}\b)")
CODE_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"\]\(([^)\s]+)")
# Where a task or question is defined: a bold header with a period (**T1.** / ~~**T1.**~~), as a list item or alone.
HEAD_PREFIX = r"^\s*(?:[-*+]\s+(?:\[[ xX]\]\s+)?)?~{0,2}\*\*"
HEAD_DEF_RE = re.compile(HEAD_PREFIX + r"([TQ]\d+)\.")
HEAD_NO_DOT_RE = re.compile(HEAD_PREFIX + r"([TQ]\d+)(?![\d.])")
TASK_DEF_RE = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s+(~{0,2})\*\*(T\d+)\.")
# A requirement row; the text may be struck through, the ID too.
ROW_RE = re.compile(r"^\s*\|\s*~{0,2}(R\d+)~{0,2}\s*\|(.*)$")
DEPENDS_RE = re.compile(r"^\s*[-*+]\s+(?:Depends on|Зависит от):\s*(.*)$")
BLOCKED_RE = re.compile(r"^\s*[-*+]\s+(?:Blocked by|Заблокировано):\s*(.*)$")
COVERS_RE = re.compile(r"^\s*[-*+]\s+(?:Covers|Покрывает):\s*(.*)$")
QUESTION_REF_RE = re.compile(r"\b(PRD|Spec) (Q\d+)\b")
NOT_COVERED_RE = re.compile(r"^\s*\*\*(?:Not covered|Не покрыто):\*\*")
# Template scaffolding that must not survive into a real document.
HTML_RE = re.compile(
    r"<!--.*?-->|</?(?:br|hr|b|i|u|em|strong|code|kbd|sub|sup|span|div|p|a|img|details|summary|table|thead|tbody|tr|td|th|ul|ol|li|small|mark|del|ins|s)(?:\s[^<>]*)?/?>",
    re.I,
)
PLACEHOLDER_RE = re.compile(r"<[A-Za-zА-Яа-яЁё…][^<>\n]{0,199}>")
OPTIONAL_MARK_RE = re.compile(r"\*\((?:optional|необязательно)\)\*")
OPTIONAL_SUFFIX_RE = re.compile(r"\s*\*\((?:optional|необязательно)\)\*\s*$")
# Mermaid: what carries a label (translated) as opposed to structure (identical).
MERMAID_LABEL_RE = re.compile(r'"[^"]*"|\[[^\]]*\]|\{[^}]*\}|\([^)]*\)|\|[^|]*\||:.*$|\bas\b.*$')
MERMAID_EDGE_TEXT_RE = re.compile(r"--\s+.*?\s+-->")


# --- paths -------------------------------------------------------------------

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


# --- parsing -----------------------------------------------------------------

def strip_comment(value: str) -> str:
    """Drop a trailing YAML comment: '#' after whitespace, outside a quoted value ("PR: #12 — …" is kept)."""
    v = value.strip()
    if v.startswith("#"):
        return ""
    if v and v[0] in "\"'":
        end = v.find(v[0], 1)
        if end != -1:
            rest = v[end + 1:]
            m = re.search(r"\s#", rest)
            return (v[: end + 1] + (rest[: m.start()] if m else rest)).rstrip()
    m = re.search(r"\s#", v)
    return v[: m.start()].rstrip() if m else v


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(lines):
    """Return (dict, index of first body line, found). Values are strings, comments stripped, quotes removed."""
    if not lines or lines[0].strip() != "---":
        return {}, 0, False
    data, key = {}, None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return data, i + 1, True
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            data[key] = unquote(strip_comment(m.group(2)))
            continue
        m = re.match(r"^\s*-\s+(.*)$", line)  # item of a multi-line list, indented or not
        if m and key is not None:
            item = unquote(strip_comment(m.group(1)))
            data[key] = (data[key] + "\n" if data[key] else "") + item
    return data, len(lines), True


def scan(lines, start):
    """Body records (line number, text, fence): fence is None for text, else ("open" | "in" | "close", info string).

    One fence-aware pass for every check, so a ``` block inside a ~~~ block is read the same way everywhere.
    """
    out, fence = [], None
    for n, line in enumerate(lines[start:], start=start + 1):
        if fence:
            char, length, lang = fence
            if re.match(rf"^\s*{re.escape(char)}{{{length},}}\s*$", line):
                out.append((n, line, ("close", lang)))
                fence = None
            else:
                out.append((n, line, ("in", lang)))
            continue
        m = FENCE_OPEN_RE.match(line)
        if m:
            fence = (m.group(1)[0], len(m.group(1)), m.group(2) or "")
            out.append((n, line, ("open", fence[2])))
            continue
        out.append((n, line, None))
    return out


def text_lines(doc):
    """(line number, text) outside fenced blocks."""
    return [(n, line) for n, line, fence in doc["records"] if fence is None]


def mermaid_skeleton(lines):
    """Mermaid lines with labels removed: node IDs, participants and arrows stay, translated words go."""
    out = []
    for line in lines:
        s = line.strip()
        if re.match(r"^(subgraph|title)\b", s):
            s = s.split()[0]
        s = MERMAID_EDGE_TEXT_RE.sub("-->", s)
        s = MERMAID_LABEL_RE.sub("", s)
        s = re.sub(r"\s+", "", s)
        if s:
            out.append(s)
    return out


def fence_key(lang, lines):
    """(lang, line count, digest): content for code, structure only for Mermaid."""
    body = mermaid_skeleton(lines) if lang == "mermaid" else lines
    digest = hashlib.sha1("\n".join(body).encode("utf-8")).hexdigest()[:8]
    return (lang, len(lines), digest)


def new_section(title, level):
    return {"title": title, "level": level, "lists": 0, "checkboxes": [], "tables": [], "fences": [], "rows": [], "defs": []}


_DOCS = {}


def parse(path: Path):
    """Everything the checks need from one document, parsed once."""
    path = path.resolve()
    if path in _DOCS:
        return _DOCS[path]
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    frontmatter, start, has_frontmatter = parse_frontmatter(lines)
    records = scan(lines, start)
    sections = [new_section("(before first heading)", 0)]
    headings = []  # (level, title, line number)
    ids, code, links = set(), Counter(), []
    fence_lines, fence_lang = None, ""
    table = None  # [rows, columns] while inside a table

    for n, line, fence in records:
        section = sections[-1]
        if fence:
            kind, lang = fence
            if kind == "open":
                fence_lines, fence_lang = [], lang
            elif kind == "in":
                fence_lines.append(line)
                ids.update(ID_RE.findall(line))
            else:
                section["fences"].append(fence_key(fence_lang, fence_lines))
                fence_lines = None
            continue

        if line.lstrip().startswith("|"):
            if not TABLE_SEP_RE.match(line):
                cols = len(line.strip().strip("|").split("|"))
                if table is None:
                    table = [0, cols]
                    section["tables"].append(table)
                table[0] += 1
                m = ROW_RE.match(line)
                if m:
                    cells = m.group(2).split("|")
                    section["rows"].append((m.group(1), "~~" in cells[0], cells[0].strip()))
        else:
            table = None

        m = HEADING_RE.match(line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            headings.append((level, title, n))
            sections.append(new_section(title, level))
            continue

        if LIST_RE.match(line):
            section["lists"] += 1
        m = CHECKBOX_RE.match(line)
        if m:
            section["checkboxes"].append(m.group(1).lower() == "x")
        m = HEAD_DEF_RE.match(line)
        if m:
            section["defs"].append((m.group(1), n))

        ids.update(ID_RE.findall(line))
        code.update(c[1].strip() for c in CODE_RE.findall(line))
        links.extend(LINK_RE.findall(line))

    if fence_lines is not None:  # unclosed fence runs to the end of the file
        sections[-1]["fences"].append(fence_key(fence_lang, fence_lines))

    _DOCS[path] = {
        "path": path,
        "lines": lines,
        "frontmatter": frontmatter,
        "has_frontmatter": has_frontmatter,
        "start": start,
        "records": records,
        "sections": sections,
        "headings": headings,
        "ids": ids,
        "code": code,
        "links": links,
    }
    return _DOCS[path]


_TEMPLATES = {}


def template_headings(lang, doc_name):
    """[(level, title, optional)] of the skill's template for this document, or None without one."""
    key = (lang, doc_name)
    if key not in _TEMPLATES:
        path = TEMPLATES_DIR / lang / f"{doc_name}.md"
        out = None
        if path.is_file():
            out = []
            for _, line in text_lines(parse(path)):
                m = HEADING_RE.match(line)
                if m:
                    title = m.group(2).strip()
                    out.append((len(m.group(1)), OPTIONAL_SUFFIX_RE.sub("", title), bool(OPTIONAL_SUFFIX_RE.search(title))))
        _TEMPLATES[key] = out
    return _TEMPLATES[key]


# --- per-file checks ---------------------------------------------------------

def lint(path: Path):
    """Checks that need no mirror."""
    doc = parse(path)
    issues = lint_frontmatter(path, doc)
    issues += lint_headings(path, doc)
    issues += lint_ids(path, doc)
    if path.stem == "tasks":
        issues += lint_tasks(doc)
    issues += lint_scaffolding(doc)
    return issues


def lint_frontmatter(path, doc):
    fm, stem = doc["frontmatter"], path.stem
    if not doc["has_frontmatter"]:
        return ["no frontmatter block (--- … ---) at the top of the file"]
    issues = []
    lang, index = lang_of(path)
    has_prd = (path.parent / "prd.md").is_file()
    required = list(COMMON_KEYS) + [k for k in SIBLING_KEYS[stem] if k != "prd" or has_prd]
    missing = [k for k in required if k not in fm]
    if missing:
        issues.append(f"frontmatter is missing {missing} (every key of the template is filled; unknowns are TBD or [])")
    if fm.get("type") and fm["type"] != stem:
        issues.append(f"frontmatter 'type: {fm['type']}' does not match the file name {path.name}")
    if fm.get("lang") and lang and fm["lang"] != lang:
        issues.append(f"frontmatter 'lang: {fm['lang']}' does not match the folder {lang}/")
    if fm.get("status") and fm["status"] not in STATUSES:
        issues.append(f"frontmatter 'status: {fm['status']}' is not one of {' / '.join(STATUSES)}")
    dates = {}
    for key in ("created", "updated"):
        v = fm.get(key, "")
        if not v or v == DATE_PLACEHOLDER:
            continue
        try:
            dates[key] = datetime.date.fromisoformat(v)
        except ValueError:
            issues.append(f"frontmatter '{key}: {v}' is not a real YYYY-MM-DD date")
    if len(dates) == 2 and dates["updated"] < dates["created"]:
        issues.append(f"frontmatter 'updated' ({fm['updated']}) is earlier than 'created' ({fm['created']})")
    for key in SIBLING_KEYS[stem]:
        v = fm.get(key)
        if v and not (path.parent / v).is_file():
            issues.append(f"frontmatter '{key}: {v}' names a file that does not exist")
    if lang and fm.get("mirror"):
        expected = relative_link(path, twin(path, lang, index))
        if fm["mirror"] != expected:
            issues.append(f"frontmatter 'mirror' should be '{expected}' (found {fm['mirror']!r})")
    return issues


def lint_headings(path, doc):
    """Headings against the template: H1 suffix, H1/H2 and template H3 titles, their order, required ones present."""
    lang, _ = lang_of(path)
    tpl = template_headings(lang, path.stem) if lang else None
    if not tpl:
        return []
    issues = []
    h1 = [t for l, t, _ in tpl if l == 1]
    if h1 and " — " in h1[0]:
        suffix = " — " + h1[0].rsplit(" — ", 1)[1]
        doc_h1 = [t for l, t, _ in doc["headings"] if l == 1]
        if len(doc_h1) != 1 or not doc_h1[0].endswith(suffix):
            issues.append(f"title heading must be one '# <name>{suffix}' (found {doc_h1})")
    order = {(l, t): i for i, (l, t, _) in enumerate(tpl) if l > 1}
    seen, last = set(), -1
    for l, t, n in doc["headings"]:
        t = OPTIONAL_SUFFIX_RE.sub("", t)  # the marker itself is reported by lint_scaffolding
        if l == 1:
            continue
        if (l, t) in order:
            if (l, t) in seen:
                issues.append(f"line {n}: heading '{t}' appears twice")
            elif order[(l, t)] < last:
                issues.append(f"line {n}: heading '{t}' is out of the template's order")
            seen.add((l, t))
            last = max(last, order[(l, t)])
        elif l <= 2 or t in {x[1] for x in tpl}:
            issues.append(f"line {n}: heading '{t}' is not in the {lang} {path.stem} template (H2 are the template's, verbatim; deeper subsections are free)")
    for l, t, optional in tpl:
        if l > 1 and not optional and (l, t) not in seen:
            issues.append(f"required section '{t}' is missing (a section with nothing to say keeps one line)")
    return issues


def lint_ids(path, doc):
    """Every T / Q header and every R row of the requirements table defined once; bold IDs without the period."""
    issues, seen = [], Counter()
    for section in doc["sections"]:
        for id_, _ in section["defs"]:
            seen[id_] += 1
        if section["title"] in DEFINITION_SECTIONS.get(path.stem, set()):
            for rid, _, _ in section["rows"]:
                seen[rid] += 1
    for id_, count in sorted(seen.items()):
        if count > 1:
            issues.append(f"ID {id_} is defined {count} times")
    for n, line in text_lines(doc):
        m = HEAD_NO_DOT_RE.match(line)
        if m:
            issues.append(f"line {n}: '**{m.group(1)}' needs the period right after the ID (**{m.group(1)}.**) to count as a task or question header")
    return issues


def lint_tasks(doc):
    """Tasks in execution order, each with one Covers line, blockers naming a question."""
    issues = []
    tasks, covers, dropped = [], Counter(), set()
    task = None
    for n, line in text_lines(doc):
        m = TASK_DEF_RE.match(line)
        if m:
            task = m.group(2)
            tasks.append(task)
            if m.group(1):
                dropped.add(task)  # ~~struck through~~: dropped, keeps no fields
            continue
        if task is None:
            continue
        above = set(tasks[:-1])
        m = DEPENDS_RE.match(line)
        if m:
            for dep in re.findall(r"\bT\d+\b", m.group(1)):
                if dep == task:
                    issues.append(f"line {n}: {task} depends on itself")
                elif dep not in above:
                    issues.append(f"line {n}: {task} depends on {dep}, which is not above it (tasks go in execution order)")
        m = BLOCKED_RE.match(line)
        if m and m.group(1).strip() not in ("", NONE_MARK) and not QUESTION_REF_RE.search(m.group(1)):
            issues.append(f"line {n}: {task} 'Blocked by' must name a question as 'PRD Qn' or 'Spec Qn' (found {m.group(1).strip()!r})")
        m = COVERS_RE.match(line)
        if m:
            covers[task] += 1
            labels = [c[1].strip() for c in CODE_RE.findall(m.group(1))]
            rids = re.findall(r"\bR\d+\b", CODE_RE.sub("", m.group(1)))
            bad = [l for l in labels if l not in COVERS_LABELS]
            if bad:
                issues.append(f"line {n}: {task} 'Covers' label must be setup, verify or rollout (found {bad})")
            if labels and rids:
                issues.append(f"line {n}: {task} 'Covers' mixes requirement IDs and a label; a task covers requirements or carries one label")
            elif len(labels) > 1:
                issues.append(f"line {n}: {task} 'Covers' has {len(labels)} labels; one label per task")
            elif not labels and not rids:
                issues.append(f"line {n}: {task} 'Covers' names neither requirement IDs nor a label")
    for t in tasks:
        if t not in dropped and covers[t] != 1:
            issues.append(f"{t} has {covers[t]} 'Covers' lines; every task has exactly one")
    return issues


def lint_scaffolding(doc):
    """Template leftovers: <placeholders>, *(optional)* markers, YYYY-MM-DD, frontmatter comments."""
    issues = []
    for n, line in enumerate(doc["lines"][: doc["start"]], start=1):
        m = re.match(r"^(?:[\w-]+:|\s*-)\s*(.*)$", line)
        if m and strip_comment(m.group(1)) != m.group(1).strip():
            issues.append(f"line {n}: frontmatter comment left from the template")
        if DATE_PLACEHOLDER in line:
            issues.append(f"line {n}: '{DATE_PLACEHOLDER}' left from the template")
    for n, line in text_lines(doc):
        prose = HTML_RE.sub("", CODE_RE.sub("", line))
        for m in PLACEHOLDER_RE.finditer(prose):
            issues.append(f"line {n}: placeholder {m.group(0)!r} left from the template")
        if OPTIONAL_MARK_RE.search(prose):
            issues.append(f"line {n}: '(optional)' marker left from the template")
        if DATE_PLACEHOLDER in line:
            issues.append(f"line {n}: '{DATE_PLACEHOLDER}' left from the template")
    return issues


# --- pair checks -------------------------------------------------------------

def compare(en: Path, ru: Path):
    """Structural differences between a document and its mirror (each file's own checks are reported separately)."""
    a, b = parse(en), parse(ru)
    issues = []

    fa, fb = a["frontmatter"], b["frontmatter"]
    if set(fa) != set(fb):
        issues.append(f"frontmatter keys differ: only EN {sorted(set(fa) - set(fb))}, only RU {sorted(set(fb) - set(fa))}")
    for key in sorted(set(fa) & set(fb) - LANG_SPECIFIC_KEYS):
        if fa[key] != fb[key]:
            issues.append(f"frontmatter '{key}' differs: EN {fa[key]!r} vs RU {fb[key]!r}")

    la, lb = [l for l, _, _ in a["headings"]], [l for l, _, _ in b["headings"]]
    if la != lb:
        issues.append(f"heading structure differs: EN {len(la)} headings {la} vs RU {len(lb)} {lb}")
    else:
        ta, tb = template_headings("en", en.stem), template_headings("ru", ru.stem)
        if ta and tb and len(ta) == len(tb):
            pos_a = {(l, t): i for i, (l, t, _) in enumerate(ta)}
            pos_b = {(l, t): i for i, (l, t, _) in enumerate(tb)}
            for (l, xa, _), (_, xb, _) in zip(a["headings"], b["headings"]):
                if l > 1 and pos_a.get((l, xa), -1) != pos_b.get((l, xb), -1):
                    want = [t for (ll, t), i in pos_b.items() if i == pos_a.get((l, xa), -2)]
                    issues.append(f"headings don't pair up: EN '{xa}' vs RU '{xb}'" + (f" (the RU template's heading here is '{want[0]}')" if want else ""))

    for sa, sb in zip(a["sections"], b["sections"]):
        where = f"section '{sa['title']}' / '{sb['title']}'"
        if sa["lists"] != sb["lists"]:
            issues.append(f"{where}: list items {sa['lists']} vs {sb['lists']}")
        if sa["checkboxes"] != sb["checkboxes"]:
            issues.append(f"{where}: checkboxes (checked=True) {sa['checkboxes']} vs {sb['checkboxes']}")
        ta, tb = [tuple(t) for t in sa["tables"]], [tuple(t) for t in sb["tables"]]
        if ta != tb:
            issues.append(f"{where}: tables (rows, columns) {ta} vs {tb}")
        if sa["fences"] != sb["fences"]:
            kinds = {k[0] for k in sa["fences"] + sb["fences"]}
            note = "Mermaid is compared by node IDs, participants and arrows, labels ignored" if kinds == {"mermaid"} else "code blocks are byte-identical in both languages"
            issues.append(f"{where}: fenced blocks (lang, lines, digest) {sa['fences']} vs {sb['fences']}; {note}")

    if a["ids"] != b["ids"]:
        issues.append(f"IDs (R/T/Q): only EN {sorted(a['ids'] - b['ids'])}, only RU {sorted(b['ids'] - a['ids'])}")
    if a["code"] != b["code"]:
        only_en = sorted((a["code"] - b["code"]).elements())
        only_ru = sorted((b["code"] - a["code"]).elements())
        issues.append(f"inline code differs (identifiers must not be translated): only EN {only_en}, only RU {only_ru}")
    if a["links"] != b["links"]:
        issues.append(f"links differ: EN {a['links']} vs RU {b['links']}")
    return issues


# --- cross-document checks ---------------------------------------------------

def rows_in(path: Path, section_titles):
    """{R ID: struck through} from the tables of the named sections."""
    rows = {}
    for section in parse(path)["sections"]:
        if section["title"] in section_titles:
            for rid, struck, _ in section["rows"]:
                rows[rid] = struck
    return rows


def not_covered_in(path: Path):
    """R IDs whose coverage cell starts with 'Not covered:'."""
    ids = set()
    for section in parse(path)["sections"]:
        if section["title"] in COVERAGE_SECTIONS:
            for rid, _, cell in section["rows"]:
                if NOT_COVERED_RE.match(cell):
                    ids.add(rid)
    return ids


def question_defs(path: Path):
    return {id_ for section in parse(path)["sections"] for id_, _ in section["defs"] if id_.startswith("Q")}


def question_refs(path: Path):
    refs = set()
    for _, line in text_lines(parse(path)):
        refs.update(QUESTION_REF_RE.findall(line))
    return refs


def covered_in_tasks(path: Path):
    ids = set()
    for _, line in text_lines(parse(path)):
        m = COVERS_RE.match(line)
        if m:
            ids.update(re.findall(r"\bR\d+\b", CODE_RE.sub("", m.group(1))))
    return ids


def by_number(ids):
    return sorted(ids, key=lambda s: int(s[1:]))


def check_feature(folder: Path):
    """Cross-document checks for one language folder of a feature."""
    issues = []
    prd, spec, tasks = folder / "prd.md", folder / "spec.md", folder / "tasks.md"
    if not prd.exists() and not spec.exists():
        return issues
    if prd.exists():
        reqs = rows_in(prd, REQUIREMENT_SECTIONS)
        source = "the PRD"
    else:
        reqs = rows_in(spec, CONTEXT_SECTIONS)
        source = "the Spec's Context & current state (there is no PRD)"
        if not reqs:
            issues.append(f"{spec.name}: no PRD beside it and no requirement rows (| R1 | …) in Context & current state")
    if spec.exists():
        covered = set(rows_in(spec, COVERAGE_SECTIONS))
        for r in by_number(set(reqs) - covered):
            issues.append(f"{spec.name}: {r} from {source} is missing in Requirements coverage")
        for r in by_number(covered - set(reqs)):
            issues.append(f"{spec.name}: {r} in Requirements coverage is not in {source}")
    if tasks.exists():
        covered = covered_in_tasks(tasks)
        live = {r for r, struck in reqs.items() if not struck}
        if spec.exists():
            live -= not_covered_in(spec)
        for r in by_number(live - covered):
            issues.append(f"{tasks.name}: {r} is in no task's Covers")
        for r in by_number(covered - set(reqs)):
            issues.append(f"{tasks.name}: Covers names {r}, which is not in {source}")
    defined = {"PRD": question_defs(prd) if prd.exists() else set(), "Spec": question_defs(spec) if spec.exists() else set()}
    for doc in (prd, spec, tasks):
        if not doc.exists():
            continue
        for where, q in sorted(question_refs(doc), key=lambda r: (r[0], int(r[1][1:]))):
            if q not in defined[where]:
                issues.append(f"{doc.name}: refers to {where} {q}, which {where.lower()}.md does not define")
    return issues


# --- driver ------------------------------------------------------------------

def collect(paths):
    """Feature documents under the given paths; what was skipped is reported, not silently dropped."""
    files, notes, missing = set(), [], []
    for raw in paths:
        p = Path(raw).resolve()
        if p.is_dir():
            candidates = sorted(f for name in DOC_NAMES for f in p.rglob(f"{name}.md"))
        elif p.is_file():
            candidates = [p]
        else:
            missing.append(f"not found: {raw}")
            continue
        for f in candidates:
            lang, _ = lang_of(f)
            if lang is None or f.stem not in DOC_NAMES:
                notes.append(f"ignored: {f} (not a prd.md / spec.md / tasks.md inside an en/ or ru/ folder)")
            else:
                files.add(f)
    return sorted(files), notes, missing


def guarded(fn, *args):
    try:
        return fn(*args)
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read: {exc}"]


def report(label, issues):
    if issues:
        print(f"FAIL {label}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"OK   {label}")
    return bool(issues)


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    files, notes, missing = collect(argv)
    for line in missing + notes:
        print(line)
    if not files:
        print("nothing to check")
        return 2
    failed = bool(missing)

    for f in files:
        failed |= report(str(f), guarded(lint, f))

    pairs, seen = [], set()
    for f in files:
        lang, index = lang_of(f)
        other = twin(f, lang, index)
        if not other.exists():
            print(f"MISSING {other} (mirror of {f})")
            failed = True
            continue
        pair = (f, other) if lang == "en" else (other, f)
        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    for en, ru in pairs:
        failed |= report(f"{en} <-> {ru}", guarded(compare, en, ru))

    features = {}
    for f in files:
        lang, index = lang_of(f)
        features.setdefault(Path(*f.parts[:index]), set()).add(Path(*f.parts[: index + 1]))
    for feature, folders in sorted(features.items()):
        per_lang = {folder: guarded(check_feature, folder) for folder in sorted(folders)}
        common = set.intersection(*(set(v) for v in per_lang.values())) if len(per_lang) > 1 else set()
        if common:
            failed |= report(f"{feature} (across documents)", [i for i in next(iter(per_lang.values())) if i in common])
        for folder, issues in per_lang.items():
            own = [i for i in issues if i not in common]
            if own or not common:
                failed |= report(f"{folder} (across documents)", own)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
