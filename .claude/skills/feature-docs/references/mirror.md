# Bilingual mirror

Rules for the `uk/` side of every document: what stays identical, what is translated, and how to repair a pair that drifted apart. Read before writing or editing any `uk/` file.

English is the main document (`en/`, `lang: en`). Ukrainian (`uk/`, `lang: uk`) is a mirror for convenient reading: it never adds, decides or drops anything, and when the two disagree in meaning, English is right unless the Ukrainian side holds a newer edit (see *Out-of-sync pair* below). A reader of either version learns exactly the same things:

- **Structure**: H1, H2 and the template's H3 are the template's, verbatim and in its order, in each language; subsections below that are free and pair up by position; same table rows, list items and checkbox states.
- **Facts**: every number, date, name, status, priority and decision on both sides. No clarification, example or caveat on one side only.
- **Untranslated**: IDs, priorities and task labels; anything in backticks; fenced code blocks except Mermaid, byte-identical with comments; people's names; UI text (screen names, labels, messages, empty states), quoted as the product shows or will show it. When the UI language isn't settled, UI text is English in both versions, including labels a source quotes in another language: «Зберегти» becomes "Save", and the final copy is a design question.
- **Diagrams**: identical node IDs, participants and arrows. The code inside a label (a call, identifier, field or value, such as `init(fields)` or `orders-<id>.csv`) stays byte-identical; the words around it are translated.
- **Links**: identical, relative to the language folder; an in-page anchor is the one exception, since it points at the translated heading.
- **Frontmatter**: identical except `title`, `lang`, `mirror`; `status` and `updated` change together.

Translate for meaning. The Ukrainian reads as written by a Ukrainian-speaking engineer; terms the team uses in English (rollout, endpoint) may stay English.

Out-of-sync pair: `git diff` / `git log` both files and port the change to the other side. Conflicting changes on both sides: show the user and ask which is right. Never regenerate one side from the other; that discards someone's edit.
