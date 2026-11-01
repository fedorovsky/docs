# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source for Claude Code skills about documentation, laid out like `anthropics/skills`. Each skill is a folder under `skills/` following the Agent Skills spec (agentskills.io): `SKILL.md` plus optional `scripts/`, `references/` and `assets/`. `.claude-plugin/marketplace.json` makes the repo a plugin marketplace (`fedorovsky-docs`). Each plugin entry there lists its skills, with `"strict": false` and no `plugin.json`.

Currently there is one skill, `skills/feature-docs/`. It writes, updates and reviews feature docs as a PRD + Spec pair, each kept as mirrored English and Russian versions (`<feature>/en/*.md` ↔ `<feature>/ru/*.md`).

`~/.claude/skills/feature-docs` is a symlink to `skills/feature-docs/` here, so any edit is live in every project immediately. There is no build step. Keep only skill content inside a skill folder: anything placed there ships with the skill. Repo-level files (README, this file, `.gitignore`, `.claude-plugin/`) belong at the root.

Adding a skill means three things: create `skills/<name>/SKILL.md` with `name` equal to the folder name, add the folder to a plugin's `skills` array in `marketplace.json`, and add it to the README.

## Commands

```bash
# Validate the marketplace manifest
claude plugin validate .

# feature-docs: templates and example must always pass the mirror check (Python 3, stdlib only)
python3 skills/feature-docs/scripts/check_mirror.py skills/feature-docs/assets/templates skills/feature-docs/references/examples

# Single pair (pass either side)
python3 skills/feature-docs/scripts/check_mirror.py skills/feature-docs/assets/templates/en/spec.md
```

SKILL.md frontmatter rules (Agent Skills spec): `name` must match the folder, use lowercase letters, digits and hyphens, and be at most 64 characters. `description` can be at most 1024 characters.

It exits with 1 on any mismatch or missing mirror. There are no unit tests. After changing the checker, also confirm that it still *fails* on deliberate drift: copy the example to the scratchpad, break one side (add a table row, change `status`, translate a backticked identifier, edit a Mermaid block, delete a mirror) and run it there.

## How feature-docs fits together

All paths are relative to `skills/feature-docs/`.

- `SKILL.md`: frontmatter `description` is the trigger. It deliberately lists English and Russian phrasings, so keep both when editing it. The body holds the workflow, the conventions and the review checklist. It refers to the other files by skill-relative paths.
- `assets/templates/en|ru/{prd,spec}.md`: the canonical document structure. The Russian templates fix the Russian section headings used across all features.
- `references/examples/orders-csv-export/`: worked example showing the expected depth, tone and conventions (struck-through requirement, open question, Mermaid diagram, coverage table).
- `scripts/check_mirror.py`: structural parity check. Compares frontmatter, heading levels, per-section list, checkbox, table and fenced-block counts, plus requirement IDs (`R\d+`), inline code and links across the whole document.

These files are coupled, so a convention change usually touches all of them in one go:

- Changing a section or frontmatter field means editing both language templates, both language versions of the example, the checklist in `SKILL.md`, and possibly `README.md`.
- Frontmatter keys allowed to differ between languages are `title`, `lang` and `mirror` (`LANG_SPECIFIC_KEYS` in the checker). Every other key must be identical, so adding a language-specific key means updating the checker.
- Templates and the example are themselves EN/RU mirrors and must pass the checker. Anything in backticks counts as an untranslated identifier and must appear identically on both sides.

Diagrams in docs are Mermaid only. That rule lives in `SKILL.md` and in the template hints.
