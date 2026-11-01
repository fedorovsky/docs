# docs

Claude Code skills for documentation, packaged as a Claude Code plugin marketplace.

```
.claude-plugin/marketplace.json   # marketplace manifest: plugins and the skills they ship
skills/
  feature-docs/                   # one folder per skill, Agent Skills layout
```

## feature-docs

Skill for writing feature documentation as a linked pair:

- **PRD**: why and what. Problem, goals, numbered requirements (`R1…`), success metrics.
- **Spec**: how. Design grounded in the real code, requirements coverage, decisions, testing, rollout.

Every document is kept in English and Russian, in `en/` and `ru/` folders, and the two are exact mirrors through every create and edit.

By default docs go here in the target project (if the project already has its own location for feature docs, the skill uses it):

```
docs/features/<feature-slug>/
  en/prd.md  en/spec.md
  ru/prd.md  ru/spec.md
```

Skill layout:

```
skills/feature-docs/
  SKILL.md                          # workflow, conventions, review checklist
  assets/templates/en|ru/           # prd/spec templates
  references/examples/              # worked example, en/ + ru/
  scripts/check_mirror.py           # structural EN/RU mirror check
```

Check mirrors yourself (e.g. after editing a doc by hand, or in CI):

```bash
python3 /path/to/skills/feature-docs/scripts/check_mirror.py docs/features
```

### Install

Pick one. Using more than one at the same time loads the skill twice.

**As a plugin** (any machine, updates through the marketplace):

```
/plugin marketplace add fedorovsky/docs
/plugin install feature-docs@fedorovsky-docs
```

**As a symlink** (while developing this repo; edits apply immediately):

```bash
ln -s "$(pwd)/skills/feature-docs" ~/.claude/skills/feature-docs
```

**Into a single project** (the skill is versioned with that project):

```bash
cp -r skills/feature-docs /path/to/project/.claude/skills/
```

### Use

Just describe what you need. The skill triggers on requests like "write a PRD for …", "сделай спеку по этой фиче", "review the spec in docs/features/sso-login". You can also call it explicitly: `/feature-docs` when installed as a symlink or copy, `/feature-docs:feature-docs` when installed as a plugin.
