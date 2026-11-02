# Diagrams

When a diagram earns its place, which Mermaid type goes where, and how it mirrors. Read before adding or editing a diagram.

Mermaid only, in fenced `mermaid` blocks: it renders in Git hosts, Confluence and IDEs, and stays diffable. No ASCII art, images or external tools.

| Showing | Type | Where |
|---|---|---|
| User flow, decision logic | `flowchart` | PRD *Users & scenarios* |
| Components interacting over time | `sequenceDiagram` | Spec *Overview* |
| Component or service structure | `flowchart` with `subgraph` | Spec *Overview*, *Components & changes* |
| Tables and relations | `erDiagram` | Spec *Data model* |
| Entity lifecycle | `stateDiagram-v2` | Spec *Data model*, *Edge cases* |

Add one when prose can't explain it quickly: three or more parties, or non-trivial states. At most about 15 nodes; split by concern. Names match the code and the text. A PRD diagram shows what the user sees and does, never internals.
