# BusLens report diagrams

Mermaid sources for the figures in Chapter~4. Render each `.mmd`
to PNG (or PDF) and commit the result alongside the source.

## Render

Install Mermaid CLI once:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Then from this directory:

```bash
# 1. Schema (Figure 4.1)
mmdc -i schema.mmd   -o schema.png   -w 1600 -H 1100 -b transparent

# 2. Pipeline (Figure 4.4)
mmdc -i pipeline.mmd -o pipeline.png -w 1500 -H 700  -b transparent

# 3. Layout (Figure 4.3)
mmdc -i layout.mmd   -o layout.png   -w 1400 -H 600  -b transparent
```

The `.tex` files reference these via
`\includegraphics{images/diagrams/<name>}` so LaTeX will pick up
either `.png` or `.pdf`.

## Editing

Open the `.mmd` files directly in any text editor or paste into the
Mermaid Live Editor (<https://mermaid.live>) for visual tweaks.
Adjust the `-w` / `-H` arguments above if labels start to overlap
in the rendered image.
