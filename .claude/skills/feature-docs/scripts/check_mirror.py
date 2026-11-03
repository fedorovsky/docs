#!/usr/bin/env python3
"""Check feature docs: each file on its own, every EN/UK pair, and each feature across its documents.

Docs live in per-language folders, and a mirror has the same path under the
sibling language folder: `<feature>/en/prd.md` <-> `<feature>/uk/prd.md`.

Usage:
    check_mirror.py PATH [PATH ...]

PATH is a feature folder (or any folder above several), or one of its prd.md /
spec.md / tasks.md files. Other Markdown files, and files outside an `en/` or
`uk/` folder, are reported as ignored. Exit status: 0 all checks pass, 1 any
check fails or a mirror is missing, 2 nothing was checked.

Each file is checked on its own, mirror or not:
- frontmatter: present, every key of its template filled, `type` matches the
  file name, `lang` the folder and `feature` the feature folder, `status` one
  of draft / review / approved / shipped / deprecated, `created` and `updated`
  real dates with `updated` no earlier, `prd:` / `spec:` / `tasks:` naming
  files that exist (the template's `./spec.md` may still be unwritten),
  `mirror:` pointing at the twin, every `links:` entry of the form
  "Role: name — URL";
- headings: H1 is `<title> — <suffix>` with the frontmatter's title; every H2
  and every template H3 is the template's, in the template's order, no
  required section missing; deeper subsections are free;
- IDs: every T / Q header (`**T1.**`) and every R row in the requirements table
  defined once; a bold ID without the period is reported; a ticked question
  carries its answer ("Answered YYYY-MM-DD:");
- requirements (the PRD's table, or the Spec's Context table without a PRD):
  a live row has a Must / Should / Could priority and acceptance criteria, and
  a table of three or more is not all Must;
- coverage (Spec): a "Partial:" / "Not covered:" row names a question;
- tasks: each has one Covers (R IDs, or one label setup / verify / rollout,
  never both), Files, Change, Done when and Depends on; "Depends on" names
  tasks above it, and a ticked task depends on ticked tasks only; "Blocked by"
  names a question as "PRD Qn" / "Spec Qn" or is "—"; a dropped task keeps no
  fields;
- no bare URL in the body (a source is cited as [text](URL) and listed in
  links:), every Mermaid block starts with a diagram type, and no template
  scaffolding: <placeholders>, *(optional)* markers, YYYY-MM-DD, frontmatter
  comments.

An EN/UK pair is compared structurally, since prose differs by language:
frontmatter (except title / lang / mirror), heading levels with sections paired
by their position in the templates (Summary <-> Коротко), per section the list
items, checkbox states, table shapes and fenced blocks (byte-identical, except
Mermaid, where node IDs, participants and arrows are compared and labels are
ignored), and over the whole file the R/T/Q IDs, inline code and links
(in-page anchors by count only, since they point at translated headings).
Meaning still has to be checked by reading.

A feature folder is checked across its documents, per language: every
requirement (the PRD's table, or the Spec's *Context & current state* table
when there is no PRD) is in the Spec's coverage table, every requirement that
is neither struck through nor "Not covered:" is in some task's "Covers" and no
task covers one that is, every "PRD Qn" / "Spec Qn" reference names a question
that document defines, and no task is blocked by an answered question.
"""

import datetime
import hashlib
import os
import re
import sys
from collections import Counter
from pathlib import Path

LANGS = ("en", "uk")
DOC_NAMES = ("prd", "spec", "tasks")
STATUSES = ("draft", "review", "approved", "shipped", "deprecated")
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "assets" / "templates"
NONE_MARK = "—"
DATE_PLACEHOLDER = "YYYY-MM-DD"

# Frontmatter: keys every document has, sibling links per document, keys that differ between languages.
COMMON_KEYS = ("type", "title", "feature", "lang", "mirror", "status", "owner", "reviewers", "created", "updated", "links")
SIBLING_KEYS = {"prd": ("spec", "tasks"), "spec": ("prd", "tasks"), "tasks": ("prd", "spec")}
LANG_SPECIFIC_KEYS = {"title", "lang", "mirror"}
LIST_KEYS = {"reviewers", "links"}  # compared as lists, so a flow list and a block list with the same items are equal

# Sections whose tables hold requirement rows (| R1 | …), in both languages.
REQUIREMENT_SECTIONS = {"Requirements", "Вимоги"}
COVERAGE_SECTIONS = {"Requirements coverage", "Покриття вимог"}
CONTEXT_SECTIONS = {"Context & current state", "Контекст і поточний стан"}  # a Spec without a PRD defines its requirements here
DEFINITION_SECTIONS = {"prd": REQUIREMENT_SECTIONS, "spec": CONTEXT_SECTIONS, "tasks": set()}
COVERS_LABELS = {"setup", "verify", "rollout"}
PRIORITIES = ("Must", "Should", "Could")
MERMAID_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram-v2", "stateDiagram", "erDiagram", "journey",
    "gantt", "pie", "quadrantChart", "requirementDiagram", "gitGraph", "mindmap", "timeline", "C4Context", "C4Container",
    "C4Component", "C4Dynamic", "C4Deployment", "sankey-beta", "xychart-beta", "block-beta", "packet-beta", "kanban",
    "architecture-beta", "zenuml",
)

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
TASK_DEF_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]\s+(~{0,2})\*\*(T\d+)\.")
# A requirement row; the text may be struck through, the ID too.
ROW_RE = re.compile(r"^\s*\|\s*~{0,2}(R\d+)~{0,2}\s*\|(.*)$")
# The fields under a task, one line each in both languages; "Blocked by" only when a question blocks the task.
TASK_FIELD_RES = {
    "Covers": re.compile(r"^\s*[-*+]\s+(?:Covers|Покриває):\s*(.*)$"),
    "Files": re.compile(r"^\s*[-*+]\s+(?:Files|Файли):\s*(.*)$"),
    "Change": re.compile(r"^\s*[-*+]\s+(?:Change|Що зробити):\s*(.*)$"),
    "Done when": re.compile(r"^\s*[-*+]\s+(?:Done when|Готово, коли):\s*(.*)$"),
    "Depends on": re.compile(r"^\s*[-*+]\s+(?:Depends on|Залежить від):\s*(.*)$"),
    "Blocked by": re.compile(r"^\s*[-*+]\s+(?:Blocked by|Заблоковано):\s*(.*)$"),
}
REQUIRED_TASK_FIELDS = ("Covers", "Files", "Change", "Done when", "Depends on")
BLOCKED_RE = TASK_FIELD_RES["Blocked by"]
COVERS_RE = TASK_FIELD_RES["Covers"]
QUESTION_REF_RE = re.compile(r"\b(PRD|Spec) (Q\d+)\b")
NOT_COVERED_RE = re.compile(r"^\s*\*\*(?:Not covered|Не покрито):\*\*")
GAP_RE = re.compile(r"^\s*\*\*(?:Partial|Частково|Not covered|Не покрито):\*\*")
# An answered question carries its answer on its own line: "Answered 2026-03-09: …" / "Відповідь 2026-03-09: …".
ANSWERED_RE = re.compile(r"\b(?:Answered|Відповідь) \d{4}-\d{2}-\d{2}:")
# A source in links:, "Role: name — URL"; the URL may be left out for a key the team's tracker resolves ("Jira: SHOP-412").
LINK_ENTRY_RE = re.compile(r"^[A-Za-z][\w /&.-]*: [^—]+(?: — \S+)?$")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
URL_RE = re.compile(r"https?://\S+")
# Template scaffolding that must not survive into a real document.
HTML_RE = re.compile(
    r"<!--.*?-->|</?(?:br|hr|b|i|u|em|strong|code|kbd|sub|sup|span|div|p|a|img|details|summary|table|thead|tbody|tr|td|th|ul|ol|li|small|mark|del|ins|s)(?:\s[^<>]*)?/?>",
    re.I,
)
PLACEHOLDER_RE = re.compile(r"<[A-Za-zА-Яа-яІіЇїЄєҐґ…][^<>\n]{0,199}>")
OPTIONAL_MARK_RE = re.compile(r"\*\((?:optional|необов[’'ʼ]язково)\)\*")
OPTIONAL_SUFFIX_RE = re.compile(r"\s*\*\((?:optional|необов[’'ʼ]язково)\)\*\s*$")
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
    """Drop a trailing YAML comment: '#' after whitespace, outside a quoted scalar or quoted list item ("PR: #12 — …" is kept).

    A quote opens only where a value or a list item starts, so the apostrophe in `Jane O'Doe   # note` hides nothing.
    """
    v = value.strip()
    quote = None
    for i, ch in enumerate(v):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'" and (i == 0 or v[:i].rstrip().endswith(("[", ","))):
            quote = ch
        elif ch == "#" and (i == 0 or v[i - 1].isspace()):
            return v[:i].rstrip()
    return v


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def list_items(value: str):
    """Items of a YAML list the frontmatter parser kept as text: a flow list `[a, "b, c"]` or block items joined by newlines."""
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        items, buf, quote = [], "", None
        for ch in v[1:-1]:
            if quote:
                buf += ch
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote, buf = ch, buf + ch
            elif ch == ",":
                items.append(buf)
                buf = ""
            else:
                buf += ch
        items.append(buf)
        return [unquote(i.strip()) for i in items if i.strip()]
    return [i for i in v.split("\n") if i.strip()]


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


def mermaid_type(lines):
    """The diagram type a Mermaid block declares: its first word, after any %% directive or --- front matter."""
    in_front = False
    for line in lines:
        s = line.strip()
        if not s or s.startswith("%%"):
            continue
        if s == "---":
            in_front = not in_front
            continue
        if not in_front:
            return s.split()[0].rstrip(";:")
    return ""


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
    mermaid = []  # (line of the fence, diagram type) per Mermaid block
    fence_lines, fence_lang, fence_start = None, "", 0
    table = None  # [rows, columns] while inside a table

    for n, line, fence in records:
        section = sections[-1]
        if fence:
            kind, lang = fence
            if kind == "open":
                fence_lines, fence_lang, fence_start = [], lang, n
            elif kind == "in":
                fence_lines.append(line)
                ids.update(ID_RE.findall(line))
            else:
                section["fences"].append(fence_key(fence_lang, fence_lines))
                if fence_lang == "mermaid":
                    mermaid.append((fence_start, mermaid_type(fence_lines)))
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
                    cells = [c.strip() for c in m.group(2).strip().rstrip("|").split("|")]
                    section["rows"].append((m.group(1), "~~" in cells[0], cells, n))
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
            box = CHECKBOX_RE.match(line)
            section["defs"].append((m.group(1), n, bool(box and box.group(1).lower() == "x")))

        ids.update(ID_RE.findall(line))
        code.update(c[1].strip() for c in CODE_RE.findall(line))
        links.extend(LINK_RE.findall(line))

    if fence_lines is not None:  # unclosed fence runs to the end of the file
        sections[-1]["fences"].append(fence_key(fence_lang, fence_lines))
        if fence_lang == "mermaid":
            mermaid.append((fence_start, mermaid_type(fence_lines)))

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
        "mermaid": mermaid,
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
    issues += lint_questions(doc)
    issues += lint_requirements(path, doc)
    if path.stem == "spec":
        issues += lint_coverage(doc)
    if path.stem == "tasks":
        issues += lint_tasks(doc)
    issues += lint_sources(doc)
    issues += lint_diagrams(doc)
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
    if fm.get("feature") and index:
        folder = path.parts[index - 1]
        if fm["feature"] != folder:
            issues.append(f"frontmatter 'feature: {fm['feature']}' does not match the feature folder {folder}/")
    for entry in list_items(fm.get("links", "")):
        if not LINK_ENTRY_RE.match(entry):
            issues.append(f"frontmatter links entry {entry!r} is not of the form \"Role: name — URL\" (\"Jira: SHOP-412\", \"Figma: consent banner — https://…\")")
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
        if v and not (path.parent / v).is_file() and v != f"./{key}.md":
            issues.append(f"frontmatter '{key}: {v}' names a file that does not exist (a sibling not written yet is linked as ./{key}.md)")
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
        else:
            name, title = doc_h1[0][: -len(suffix)].strip(), doc["frontmatter"].get("title", "")
            if title and name != title:
                issues.append(f"title heading names {name!r} but the frontmatter says 'title: {title}'; the two are the same name")
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
        for id_, _, _ in section["defs"]:
            seen[id_] += 1
        if section["title"] in DEFINITION_SECTIONS.get(path.stem, set()):
            for rid, _, _, _ in section["rows"]:
                seen[rid] += 1
    for id_, count in sorted(seen.items()):
        if count > 1:
            issues.append(f"ID {id_} is defined {count} times")
    for n, line in text_lines(doc):
        m = HEAD_NO_DOT_RE.match(line)
        if m:
            issues.append(f"line {n}: '**{m.group(1)}' needs the period right after the ID (**{m.group(1)}.**) to count as a task or question header")
    return issues


def lint_questions(doc):
    """A ticked question carries its answer on its line: 'Answered YYYY-MM-DD: …' (Ukrainian 'Відповідь YYYY-MM-DD: …')."""
    issues = []
    for section in doc["sections"]:
        for id_, n, ticked in section["defs"]:
            if id_.startswith("Q") and ticked and not ANSWERED_RE.search(doc["lines"][n - 1]):
                issues.append(f"line {n}: {id_} is ticked but has no 'Answered YYYY-MM-DD: …' after the owner (Ukrainian: 'Відповідь YYYY-MM-DD: …'); an answered question keeps its line and gains the answer")
    return issues


def lint_requirements(path, doc):
    """Requirement rows: a live row has a Must / Should / Could priority and acceptance criteria; a table that is all Must isn't prioritised."""
    if path.stem == "spec" and (path.parent / "prd.md").is_file():
        return []  # the PRD defines the requirements; a table in the Spec's Context is then a reference, not the definition
    issues, live = [], []
    for section in doc["sections"]:
        if section["title"] not in DEFINITION_SECTIONS.get(path.stem, set()):
            continue
        for rid, struck, cells, n in section["rows"]:
            if struck:
                continue
            priority = cells[1].strip("* ") if len(cells) > 1 else ""
            criteria = cells[2] if len(cells) > 2 else ""
            live.append(priority)
            if priority not in PRIORITIES:
                issues.append(f"line {n}: {rid} priority {priority!r} is not Must / Should / Could")
            if not criteria:
                issues.append(f"line {n}: {rid} has no acceptance criteria (at least one check a tester can run)")
    if len(live) >= 3 and all(p == "Must" for p in live):
        issues.append(f"all {len(live)} requirements are Must; a table that is all Must hasn't been prioritised (a debug aid, a convenience or anything to be removed later is Should or Could)")
    return issues


def lint_coverage(doc):
    """A coverage row marked Partial: / Not covered: names the question that tracks the gap."""
    issues = []
    for section in doc["sections"]:
        if section["title"] in COVERAGE_SECTIONS:
            for rid, _, cells, n in section["rows"]:
                m = GAP_RE.match(cells[0])
                if m and not QUESTION_REF_RE.search(" ".join(cells)):
                    issues.append(f"line {n}: {rid} is {m.group(0).strip()} but names no question (PRD Qn / Spec Qn) that tracks what's missing")
    return issues


def lint_tasks(doc):
    """Tasks in execution order, each with its fields; ticks consistent with dependencies; a dropped task keeps no fields."""
    issues = []
    tasks, ticked, dropped, fields = [], set(), set(), {}
    task = None
    for n, line in text_lines(doc):
        m = TASK_DEF_RE.match(line)
        if m:
            task = m.group(3)
            tasks.append(task)
            fields[task] = Counter()
            if m.group(1).lower() == "x":
                ticked.add(task)
            if m.group(2):
                dropped.add(task)  # ~~struck through~~: dropped, keeps no fields
            continue
        if task is None:
            continue
        field = next((name for name, rx in TASK_FIELD_RES.items() if rx.match(line)), None)
        if field is None:
            continue
        fields[task][field] += 1
        if task in dropped:
            issues.append(f"line {n}: {task} is dropped but keeps a '{field}' line; a dropped task keeps only the reason")
            continue
        value = TASK_FIELD_RES[field].match(line).group(1).strip()
        above = set(tasks[:-1])
        if field == "Depends on":
            for dep in re.findall(r"\bT\d+\b", value):
                if dep == task:
                    issues.append(f"line {n}: {task} depends on itself")
                elif dep not in above:
                    issues.append(f"line {n}: {task} depends on {dep}, which is not above it (tasks go in execution order)")
                elif task in ticked and dep not in ticked and dep not in dropped:
                    issues.append(f"line {n}: {task} is ticked but depends on {dep}, which is not")
        elif field == "Blocked by":
            if value not in ("", NONE_MARK) and not QUESTION_REF_RE.search(value):
                issues.append(f"line {n}: {task} 'Blocked by' must name a question as 'PRD Qn' or 'Spec Qn' (found {value!r})")
        elif field == "Covers":
            labels = [c[1].strip() for c in CODE_RE.findall(value)]
            rids = re.findall(r"\bR\d+\b", CODE_RE.sub("", value))
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
        if t in dropped:
            continue
        for name in REQUIRED_TASK_FIELDS:
            count = fields[t][name]
            if count == 0:
                issues.append(f"{t} has no '{name}' line; every task has {', '.join(REQUIRED_TASK_FIELDS)} (and 'Blocked by' when a question blocks it)")
            elif count > 1:
                issues.append(f"{t} has {count} '{name}' lines; one of each")
    return issues


def lint_sources(doc):
    """No bare URL in the body: a source is cited as [text](URL) where it is used and listed in links: as "Role: name — URL"."""
    issues = []
    for n, line in text_lines(doc):
        prose = MD_LINK_RE.sub("", CODE_RE.sub("", line))
        for m in URL_RE.finditer(prose):
            issues.append(f"line {n}: bare URL {m.group(0).rstrip('>).,;')!r}; cite it as [text](URL) where it is used and list it in links: as \"Role: name — URL\"")
    return issues


def lint_diagrams(doc):
    """Every Mermaid block starts with a diagram type Mermaid knows."""
    return [
        f"line {n}: Mermaid block starts with {word!r}, not a diagram type ({', '.join(MERMAID_TYPES[:5])}, …)"
        for n, word in doc["mermaid"] if word not in MERMAID_TYPES
    ]


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

def compare(en: Path, uk: Path):
    """Structural differences between a document and its mirror (each file's own checks are reported separately)."""
    a, b = parse(en), parse(uk)
    issues = []

    fa, fb = a["frontmatter"], b["frontmatter"]
    if set(fa) != set(fb):
        issues.append(f"frontmatter keys differ: only EN {sorted(set(fa) - set(fb))}, only UK {sorted(set(fb) - set(fa))}")
    for key in sorted(set(fa) & set(fb) - LANG_SPECIFIC_KEYS):
        va, vb = (list_items(fa[key]), list_items(fb[key])) if key in LIST_KEYS else (fa[key], fb[key])
        if va != vb:
            issues.append(f"frontmatter '{key}' differs: EN {fa[key]!r} vs UK {fb[key]!r}")

    la, lb = [l for l, _, _ in a["headings"]], [l for l, _, _ in b["headings"]]
    if la != lb:
        issues.append(f"heading structure differs: EN {len(la)} headings {la} vs UK {len(lb)} {lb}")
    else:
        ta, tb = template_headings("en", en.stem), template_headings("uk", uk.stem)
        if ta and tb and len(ta) == len(tb):
            pos_a = {(l, t): i for i, (l, t, _) in enumerate(ta)}
            pos_b = {(l, t): i for i, (l, t, _) in enumerate(tb)}
            for (l, xa, _), (_, xb, _) in zip(a["headings"], b["headings"]):
                if l > 1 and pos_a.get((l, xa), -1) != pos_b.get((l, xb), -1):
                    want = [t for (ll, t), i in pos_b.items() if i == pos_a.get((l, xa), -2)]
                    issues.append(f"headings don't pair up: EN '{xa}' vs UK '{xb}'" + (f" (the UK template's heading here is '{want[0]}')" if want else ""))

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
        issues.append(f"IDs (R/T/Q): only EN {sorted(a['ids'] - b['ids'])}, only UK {sorted(b['ids'] - a['ids'])}")
    if a["code"] != b["code"]:
        only_en = sorted((a["code"] - b["code"]).elements())
        only_uk = sorted((b["code"] - a["code"]).elements())
        issues.append(f"inline code differs (identifiers must not be translated): only EN {only_en}, only UK {only_uk}")
    la, lb = [l for l in a["links"] if not l.startswith("#")], [l for l in b["links"] if not l.startswith("#")]
    if la != lb:
        issues.append(f"links differ: EN {la} vs UK {lb}")
    na, nb = sum(l.startswith("#") for l in a["links"]), sum(l.startswith("#") for l in b["links"])
    if na != nb:
        issues.append(f"in-page anchors differ in number: EN {na} vs UK {nb} (an anchor points at the translated heading, so only the count is compared)")
    return issues


# --- cross-document checks ---------------------------------------------------

def rows_in(path: Path, section_titles):
    """{R ID: struck through} from the tables of the named sections."""
    rows = {}
    for section in parse(path)["sections"]:
        if section["title"] in section_titles:
            for rid, struck, _, _ in section["rows"]:
                rows[rid] = struck
    return rows


def not_covered_in(path: Path):
    """R IDs whose coverage cell starts with 'Not covered:'."""
    ids = set()
    for section in parse(path)["sections"]:
        if section["title"] in COVERAGE_SECTIONS:
            for rid, _, cells, _ in section["rows"]:
                if NOT_COVERED_RE.match(cells[0]):
                    ids.add(rid)
    return ids


def question_defs(path: Path):
    """{Q ID: answered (ticked)} for the questions a document defines."""
    return {id_: ticked for section in parse(path)["sections"] for id_, _, ticked in section["defs"] if id_.startswith("Q")}


def blockers_in(path: Path):
    """(task, document, question, line) for every 'Blocked by' reference in a task list."""
    out, task = [], None
    for n, line in text_lines(parse(path)):
        m = TASK_DEF_RE.match(line)
        if m:
            task = m.group(3)
            continue
        m = BLOCKED_RE.match(line)
        if m and task:
            out.extend((task, where, q, n) for where, q in QUESTION_REF_RE.findall(m.group(1)))
    return out


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
        dropped = {r for r, struck in reqs.items() if struck}
        not_covered = not_covered_in(spec) if spec.exists() else set()
        for r in by_number(set(reqs) - dropped - not_covered - covered):
            issues.append(f"{tasks.name}: {r} is in no task's Covers")
        for r in by_number(covered - set(reqs)):
            issues.append(f"{tasks.name}: Covers names {r}, which is not in {source}")
        for r in by_number(covered & dropped):
            issues.append(f"{tasks.name}: Covers names {r}, which is dropped in {source}")
        for r in by_number(covered & not_covered):
            issues.append(f"{tasks.name}: Covers names {r}, which the Spec marks Not covered:")
    defined = {"PRD": question_defs(prd) if prd.exists() else {}, "Spec": question_defs(spec) if spec.exists() else {}}
    for doc in (prd, spec, tasks):
        if not doc.exists():
            continue
        for where, q in sorted(question_refs(doc), key=lambda r: (r[0], int(r[1][1:]))):
            if q not in defined[where]:
                issues.append(f"{doc.name}: refers to {where} {q}, which {where.lower()}.md does not define")
    if tasks.exists():
        for task, where, q, n in blockers_in(tasks):
            if defined[where].get(q):
                issues.append(f"{tasks.name}: line {n}: {task} is blocked by {where} {q}, which is answered (ticked); drop the line or block on an open question")
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
                notes.append(f"ignored: {f} (not a prd.md / spec.md / tasks.md inside an en/ or uk/ folder)")
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
    for en, uk in pairs:
        failed |= report(f"{en} <-> {uk}", guarded(compare, en, uk))

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
