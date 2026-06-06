// plotly.js-dist-min ships no types; reuse @types/plotly.js. The react-plotly.js
// /factory subpath builds a Plot component from a Plotly bundle.
declare module 'plotly.js-dist-min' {
  const Plotly: typeof import('plotly.js')
  export default Plotly
}

declare module 'react-plotly.js/factory' {
  import type { ComponentType } from 'react'
  import type { PlotParams } from 'react-plotly.js'

  export default function createPlotlyComponent(plotly: object): ComponentType<PlotParams>
}
