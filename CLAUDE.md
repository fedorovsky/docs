# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source for Claude Code skills about documentation. Currently one skill, `feature-docs/`, which writes, updates and reviews feature docs as a PRD + Spec pair, each kept as mirrored English and Russian versions (`<feature>/en/*.md` ↔ `<feature>/ru/*.md`).

`~/.claude/skills/feature-docs` is a symlink to `feature-docs/` here, so any edit is live in every project immediately. There is no build step. Keep only skill content inside `feature-docs/`: anything placed there ships with the skill. Repo-level files (README, this file, `.gitignore`) belong at the root.

## Commands

The only tooling is the mirror checker (Python 3, stdlib only):

```bash
# Templates and example must always pass
python3 feature-docs/scripts/check_mirror.py feature-docs/templates feature-docs/examples

# Single pair (pass either side)
python3 feature-docs/scripts/check_mirror.py feature-docs/templates/en/spec.md
```

It exits with 1 on any mismatch or missing mirror. There are no unit tests. After changing the checker, also confirm that it still *fails* on deliberate drift: copy the example to the scratchpad, break one side (add a table row, change `status`, translate a backticked identifier, edit a Mermaid block, delete a mirror) and run it there.

## How the skill fits together

- `SKILL.md`: frontmatter `description` is the trigger. It deliberately lists English and Russian phrasings, so keep both when editing it. The body holds the workflow, the conventions and the review checklist. It refers to the other files by skill-relative paths.
- `templates/en|ru/{prd,spec}.md`: the canonical document structure. The Russian templates fix the Russian section headings used across all features.
- `examples/orders-csv-export/`: worked example showing the expected depth, tone and conventions (struck-through requirement, open question, Mermaid diagram, coverage table).
- `scripts/check_mirror.py`: structural parity check. Compares frontmatter, heading levels, per-section list, checkbox, table and fenced-block counts, plus requirement IDs (`R\d+`), inline code and links across the whole document.

These files are coupled, so a convention change usually touches all of them in one go:

- Changing a section or frontmatter field means editing both language templates, both language versions of the example, the checklist in `SKILL.md`, and possibly `README.md`.
- Frontmatter keys allowed to differ between languages are `title`, `lang` and `mirror` (`LANG_SPECIFIC_KEYS` in the checker). Every other key must be identical, so adding a language-specific key means updating the checker.
- Templates and the example are themselves EN/RU mirrors and must pass the checker. Anything in backticks counts as an untranslated identifier and must appear identically on both sides.

Diagrams in docs are Mermaid only. That rule lives in `SKILL.md` and in the template hints.
