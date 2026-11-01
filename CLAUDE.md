# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Plugin marketplace of Claude Code skills, laid out like `anthropics/skills`: one folder per skill under `skills/`, listed in `.claude-plugin/marketplace.json`. Each skill is self-contained: everything it needs lives in its folder. Don't put skill knowledge here.

```bash
claude plugin validate .
python3 skills/feature-docs/scripts/check_mirror.py skills/feature-docs
```
