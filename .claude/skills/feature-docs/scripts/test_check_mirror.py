"""Regression cases for check_mirror.py: each mutates a fresh copy of the example and checks the report.

For whoever changes the script, not for checking a feature:

    python3 scripts/test_check_mirror.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPT = SKILL / "scripts/check_mirror.py"
EXAMPLE = SKILL / "references/examples/orders-csv-export"
WORK = Path(tempfile.mkdtemp(prefix="check_mirror_tests_"))

HELP = "https://helpdesk.example.com/reports/orders-export-requests"


def run(*args, cwd=None):
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def edit(d, rel, old, new):
    p = d / rel
    s = p.read_text(encoding="utf-8")
    assert old in s, f"{rel}: {old!r} not found"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


CASES = []


def case(name, present=(), absent=(), code=None, args=None, cwd=None):
    def deco(fn):
        CASES.append((name, fn, present, absent, code, args, cwd))
        return fn
    return deco


@case("example passes", code=0)
def _(d): pass


@case("single-language folder is linted", present=["ID T1 is defined 2 times", "MISSING"], code=1)
def _(d):
    shutil.rmtree(d / "uk")
    edit(d, "en/tasks.md", "**T2.", "**T1.")


@case("bare file name from inside en/ is resolved and checked", present=["OK"], absent=["nothing to check"], code=0, args=["prd.md"], cwd="en")
def _(d): pass


@case("missing keys, bad status, impossible date", present=["is missing ['status'", "'status: aproved' is not one", "not a real YYYY-MM-DD"], code=1)
def _(d):
    edit(d, "en/prd.md", "status: approved\n", "status: aproved\n")
    edit(d, "uk/prd.md", "status: approved\n", "")
    edit(d, "en/spec.md", "created: 2026-03-10", "created: 2026-13-45")


@case("non-utf8 file does not crash", present=["cannot read"], absent=["Traceback"], code=1)
def _(d):
    (d / "en/prd.md").write_bytes((d / "en/prd.md").read_text().encode("cp1251", "replace")[:200] + b"\xff\xfe")


@case("html and comparisons are not scaffolding", absent=["left from the template"], code=0)
def _(d):
    for lang, head in (("en", "## Non-goals\n"), ("uk", "## Поза межами\n")):
        edit(d, f"{lang}/prd.md", head, head + "\n<!-- reviewer note -->\nTurnaround of <2 days, >1 hour.<br>Second line.\n")


@case("quoted scalars pass", absent=["does not exist", "does not match the folder"], code=0)
def _(d):
    for lang in ("en", "uk"):
        edit(d, f"{lang}/prd.md", f"lang: {lang}\n", f'lang: "{lang}"\n')
        edit(d, f"{lang}/prd.md", "spec: ./spec.md\n", 'spec: "./spec.md"\n')


@case("column-0 yaml list is read, differing links fail", present=["frontmatter 'links' differs"], code=1)
def _(d):
    for lang, u in (("en", "a"), ("uk", "b")):
        edit(d, f"{lang}/tasks.md", 'links: ["Jira: SHOP-412"]', f'links:\n- "Jira: SHOP-412 — https://{u}"')


@case("BOM is tolerated", absent=["frontmatter keys differ"], code=0)
def _(d):
    p = d / "en/prd.md"
    p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())


@case("second table with R rows outside Requirements is not a definition", absent=["defined 2 times"], code=0)
def _(d):
    for lang, head in (("en", "## Users & scenarios\n"), ("uk", "## Користувачі та сценарії\n")):
        edit(d, f"{lang}/prd.md", head, head + "\n| ID | Scenario |\n|----|----------|\n| R1 | monthly close |\n| R2 | audit |\n")


@case("R rows in the Spec testing plan are not coverage rows", absent=["Requirements coverage is not in"], code=0)
def _(d):
    for lang, head in (("en", "## Testing plan\n"), ("uk", "## План тестування\n")):
        edit(d, f"{lang}/spec.md", head, head + "\n| ID | Level |\n|----|-------|\n| R2 | integration |\n")


@case("struck-through ID cell still counts as the row", absent=["not in the PRD"], code=0)
def _(d):
    for lang in ("en", "uk"):
        edit(d, f"{lang}/prd.md", "| R5 | ~~", "| ~~R5~~ | ~~")


@case("backtick fence inside tilde fence is one block", absent=["missing in Requirements coverage"], code=0)
def _(d):
    block = "\n~~~\n```md\n| R9 | nope |\n```\n~~~\n"
    for lang, head in (("en", "## Non-goals\n"), ("uk", "## Поза межами\n")):
        edit(d, f"{lang}/prd.md", head, head + block)


@case("Q4 2026 is a quarter, not a question", absent=["only EN ['Q4']"], code=0)
def _(d):
    edit(d, "en/spec.md", "## Rollout & rollback\n", "## Rollout & rollback\n\nPlanned for Q4 2026.\n")
    edit(d, "uk/spec.md", "## Розгортання та відкат\n", "## Розгортання та відкат\n\nПлан — 4 кв. 2026.\n")


@case("covers mixing ids and a label fails", present=["mixes requirement IDs and a label"], code=1)
def _(d):
    edit(d, "en/tasks.md", "- Covers: `rollout`", "- Covers: R3, `rollout`")


@case("task without Covers fails, dropped task is exempt", present=["T1 has 0 'Covers' lines"], absent=["T8 has 0"], code=1)
def _(d):
    edit(d, "en/tasks.md", "  - Covers: `setup`\n", "")
    edit(d, "en/tasks.md", "- [ ] **T8. Release**", "- [ ] ~~**T8. Release**~~ Dropped")


@case("apostrophe in a value does not hide a comment", present=["frontmatter comment left"], code=1)
def _(d):
    edit(d, "en/prd.md", "owner: Jane Doe", "owner: Jane O'Doe   # from template")


@case("i18n folders are not feature docs", absent=["MISSING"], code=0, args=["."])
def _(d):
    (d / "i18n/en").mkdir(parents=True)
    (d / "i18n/en/strings.md").write_text("hello\n")


@case("bold id without period is reported", present=["needs the period"], code=1)
def _(d):
    edit(d, "en/tasks.md", "**T2. ", "**T2 — ")


@case("Blocked by: — is accepted", absent=["'Blocked by' must name"], code=0)
def _(d):
    for lang, key in (("en", "Depends on: T7"), ("uk", "Залежить від: T7")):
        edit(d, f"{lang}/tasks.md", key + "\n", key + ("\n  - Blocked by: —\n" if lang == "en" else "\n  - Заблоковано: —\n"))


@case("mermaid arrow change fails, label change passes", present=["Mermaid is compared"], code=1)
def _(d):
    edit(d, "uk/spec.md", "API-->>UI", "API->>Queue")


@case("mermaid label-only translation passes", absent=["fenced blocks"], code=0)
def _(d):
    edit(d, "uk/spec.md", "Worker->>Email: надсилає посилання, якщо задача тривала > 10 с", "Worker->>Email: шле лист")


@case("code block content must match", present=["code blocks are byte-identical"], code=1)
def _(d):
    for lang, head, body in (("en", "### Components & changes\n", "const a = 1;"), ("uk", "### Компоненти та зміни\n", "const a = 2;")):
        edit(d, f"{lang}/spec.md", head, head + "\n```ts\n" + body + "\n```\n")


@case("spec without prd: requirements in context", absent=["does not exist", "missing in Requirements coverage"], code=0)
def _(d):
    for lang in ("en", "uk"):
        (d / lang / "prd.md").unlink()
        for name in ("spec", "tasks"):
            edit(d, f"{lang}/{name}.md", "prd: ./prd.md\n", "")
        p = d / lang / "spec.md"
        p.write_text(p.read_text().replace("PRD Q2", "Spec Q1").replace("PRD Q3", "Spec Q1"))
    edit(d, "en/spec.md", "## Context & current state\n", "## Context & current state\n\n| ID | Requirement | Priority | Acceptance criteria |\n|----|---|---|---|\n| R1 | a | Must | b |\n| R2 | a | Must | b |\n| R3 | a | Must | b |\n| R4 | a | Must | b |\n| R5 | ~~a~~ | — | dropped |\n")
    edit(d, "uk/spec.md", "## Контекст і поточний стан\n", "## Контекст і поточний стан\n\n| ID | Вимога | Пріоритет | Критерії приймання |\n|----|---|---|---|\n| R1 | a | Must | b |\n| R2 | a | Must | b |\n| R3 | a | Must | b |\n| R4 | a | Must | b |\n| R5 | ~~a~~ | — | скасовано |\n")


@case("swapped sections are reported with the expected UK heading", present=["out of the template's order", "headings don't pair up"], code=1)
def _(d):
    p = d / "uk/prd.md"; s = p.read_text()
    a, b, c = s.index("## Цілі"), s.index("## Поза межами"), s.index("## Користувачі та сценарії")
    p.write_text(s[:a] + s[b:c] + s[a:b] + s[c:])


@case("free H3 under a section passes", absent=["not in the en spec template"], code=0)
def _(d):
    for lang, head in (("en", "### Components & changes\n"), ("uk", "### Компоненти та зміни\n")):
        edit(d, f"{lang}/spec.md", head, head + "\n#### Frontend\n\nx\n")


@case("a mirror without a frontmatter block is reported", present=["no frontmatter block"], code=1)
def _(d):
    p = d / "uk/tasks.md"
    p.write_text(p.read_text().split("---\n", 2)[2])


def main():
    failed = 0
    for name, fn, present, absent, code, args, cwd in CASES:
        d = WORK / name.replace(" ", "_").replace(",", "")
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(EXAMPLE, d)
        fn(d)
        rc, out = run(*(args or [d]), cwd=(d / cwd) if cwd else d)
        problems = [f"expected {s!r}" for s in present if s not in out] + [f"unexpected {s!r}" for s in absent if s in out]
        if code is not None and rc != code:
            problems.append(f"exit {rc}, expected {code}")
        status = "ok  " if not problems else "FAIL"
        failed += bool(problems)
        print(f"{status} {name}")
        for p in problems:
            print(f"      {p}")
        if problems:
            print("      --- output ---\n" + "\n".join("      " + l for l in out.splitlines()[:25]))
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
