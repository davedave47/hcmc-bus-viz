import type { ChartResponse } from '../../api/types'
import Plot from '../Plot'
import { buildPulse } from './pulse'

export default function NetworkPulse({ resp }: { resp: ChartResponse }) {
  const { data, layout } = buildPulse(resp)
  return (
    <Plot
      data={data}
      layout={layout}
      useResizeHandler
      style={{ width: '100%', height: '100%' }}
      config={{ displayModeBar: false, responsive: true }}
    />
  )
}
