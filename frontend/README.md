# frontend — web app

The single-page app. It fetches **domain data** from the backend and builds every chart and map in
the browser; the backend never sends figures. Built for a dynamic dataset, so titles and captions
are abstract and the visuals carry the specifics.

**Status: foundation + first chart.** The typed client, the server-state hooks, the chart-builder
pattern, and the shell are in place; the network-pulse chart (5.1) and the KPI strip render live
through the Vite `/api` proxy. The remaining charts, the hub, the theme cards, the entity panel, the
filter bar, the maps, and the stories are still to build.

## Stack and tooling

- **React** + **Vite** + **TypeScript** · **Tailwind** for styling.
- **TanStack Query** for server state · **react-plotly.js** (slim Plotly bundle) for charts ·
  **react-router** for navigation. Maps (MapLibre via react-map-gl) and stories (Scrollama) are planned.
- **pnpm** for dependencies · **eslint** · **vitest** (unit) · Playwright (e2e, planned).

## Design principles

Feature-based with unidirectional layering — UI state stays local, server state stays in hooks, and
figure construction is pure functions, so each piece is testable on its own.

- **`api/`** — the single source of truth for types (generated from the backend's OpenAPI) plus the
  fetch client. Types are never hand-duplicated.
- **`hooks/`** — all server state lives here (TanStack Query: `useChart`, `useKpis`, `useFilters`).
  **Components never fetch directly.**
- **`charts/`** — presentational chart components; the figure itself is built by **pure functions in
  `lib/`** (testable without React). A registry maps `chartId → component` (open/closed).
- **`components/`** — reusable presentational UI (the shell, `ChartCard`, the entity panel, the
  filter bar, theme cards). **`features/`** compose them into pages (hub, theme, story).
- **`maps/`** — MapLibre map components. **`stories/`** — Scrollama scrollytelling.

## Directory

```
frontend/src/
├── api/           # typed client + contract types (client.ts, types.ts)
├── hooks/         # TanStack Query hooks (useChart, useKpis)
├── charts/        # chart components + pure builders (e.g. health/NetworkPulse + pulse.ts)
├── components/    # shell, ChartCard, EntityPanel, FilterBar, ThemeCard
├── features/      # hub · theme · story  (planned)
├── maps/          # MapLibre  (planned)
├── stories/       # Scrollama  (planned)
├── lib/           # pure helpers (formatting, figure builders)
└── types/         # ambient types
```

## Run, test, lint

```bash
pnpm install
pnpm dev            # http://localhost:5173 (proxies /api -> :8000)
pnpm test           # vitest
pnpm lint
pnpm build          # tsc -b && vite build
```

The backend must be running (or reachable via `VITE_API_BASE`) for live charts.
