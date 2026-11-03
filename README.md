# docs

Claude Code skills for documentation.

- [`feature-docs`](.claude/skills/feature-docs/SKILL.md): feature docs as a PRD, a Spec and an implementation task list, mirrored in English and Ukrainian.

## Install

Copy the skill into your project:

```bash
cp -r .claude/skills/feature-docs /path/to/project/.claude/skills/
```

## Testing the skill

The check script has its own regression cases:

```bash
python3 .claude/skills/feature-docs/scripts/test_check_mirror.py
```

`.claude/skills/feature-docs/evals/` holds one folder per test case (prompt, input files, graders) in the layout `claude plugin eval` reads. Each is a real, billed model run with and without the skill:

```bash
claude plugin eval .claude/skills/feature-docs --allow-tools Write,Edit,Bash --scaffold
```

`playground/` is the manual test bed: a fixed brief and the app built from the docs the skill wrote for it.
