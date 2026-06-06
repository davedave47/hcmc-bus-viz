// Pure builder: ChartResponse (health/5.1) -> Plotly figure. Testable without React.
import type { Data, Layout } from 'plotly.js'

import type { ChartResponse } from '../../api/types'

const ACCENT = '#E45A2E'
const MUTED = '#6E7689'

interface PulseMeta {
  tet_start?: string
  tet_end?: string
  trough?: string
  baseline?: number
  min_drop_pct?: number
}

export function buildPulse(resp: ChartResponse): { data: Data[]; layout: Partial<Layout> } {
  const days = resp.series.map((r) => r.day as string)
  const vals = resp.series.map((r) => r.boardings as number)
  const meta = resp.meta as PulseMeta
  const byDay = new Map(days.map((d, i) => [d, vals[i]]))
  const inTet = (d: string) => !!meta.tet_start && !!meta.tet_end && d >= meta.tet_start && d <= meta.tet_end
  const tetDays = days.filter(inTet)

  const data: Data[] = [
    {
      x: days,
      y: vals,
      type: 'scatter',
      mode: 'lines',
      name: 'Daily boardings',
      line: { color: MUTED, width: 1.6 },
      hovertemplate: '%{x}<br>%{y:,} boardings<extra></extra>',
    },
    {
      x: tetDays,
      y: tetDays.map((d) => byDay.get(d) ?? 0),
      type: 'scatter',
      mode: 'lines',
      name: 'Tết window',
      line: { color: ACCENT, width: 3 },
      fill: 'tozeroy',
      fillcolor: 'rgba(228,90,46,0.12)',
      hovertemplate: '%{x}<br>%{y:,} · Tết<extra></extra>',
    },
  ]
  if (meta.baseline) {
    data.push({
      x: [days[0], days[days.length - 1]],
      y: [meta.baseline, meta.baseline],
      type: 'scatter',
      mode: 'lines',
      name: 'Jan baseline',
      line: { color: '#9AA0AB', width: 1.2, dash: 'dot' },
      hoverinfo: 'skip',
    })
  }

  const layout: Partial<Layout> = {
    margin: { l: 60, r: 20, t: 8, b: 36 },
    showlegend: true,
    legend: { orientation: 'h', y: 1.1, x: 0 },
    xaxis: { showgrid: false },
    yaxis: { rangemode: 'tozero', tickformat: '~s' },
    shapes:
      meta.tet_start && meta.tet_end
        ? [
            {
              type: 'rect',
              xref: 'x',
              yref: 'paper',
              x0: meta.tet_start,
              x1: meta.tet_end,
              y0: 0,
              y1: 1,
              fillcolor: ACCENT,
              opacity: 0.09,
              line: { width: 0 },
              layer: 'below',
            },
          ]
        : [],
    annotations: meta.trough
      ? [
          {
            x: meta.trough,
            y: byDay.get(meta.trough) ?? 0,
            text: `−${meta.min_drop_pct ?? 0}% · ${meta.trough}`,
            ax: 0,
            ay: -40,
            showarrow: true,
            arrowcolor: ACCENT,
            bgcolor: ACCENT,
            borderpad: 4,
            font: { color: '#ffffff', size: 10 },
          },
        ]
      : [],
  }
  return { data, layout }
}
