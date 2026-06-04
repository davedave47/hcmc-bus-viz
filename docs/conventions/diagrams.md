# Diagram convention

**Author diagrams in draw.io (`.drawio`) — not Mermaid.** Mermaid is
legacy and being migrated out.

## Where files live

| Kind | Location |
| --- | --- |
| Editable **sources** (`.drawio`) | `docs/diagrams/report/` · `docs/diagrams/deck/` |
| Rendered **`.png`** consumed by the LaTeX report | `report/images/diagrams/` |
| Rendered **`.png`** consumed by the defence deck | `deck/assets/` |

- Diagram **sources are centralised** under `docs/diagrams/`, split by consumer.
- Each consumer keeps an **independent** set of rendered images — the report and the
  deck do **not** share `.png` files.
- A source and its render share a basename (`arch_medallion.drawio` → `arch_medallion.png`).

## Legacy to migrate (tracked in S3)

Still on Mermaid, to be redrawn in draw.io:

- report: `dataset_erd.mmd`, `interaction_sequence.mmd`, `foundations_layered.mmd`
- deck: `deck_erd_afc.mmd`, `deck_erd_gps.mmd`

The render/export step (draw.io CLI → `.png`) is defined in the S3 diagram sub-project.
