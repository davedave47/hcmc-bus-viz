import NetworkPulse from './charts/health/NetworkPulse'
import ChartCard from './components/ChartCard'
import { useChart } from './hooks/useChart'
import { useKpis } from './hooks/useKpis'
import { fmtInt, fmtPct } from './lib/format'

function KpiStrip() {
  const { data } = useKpis()
  if (!data) return null
  const items: [string, string][] = [
    ['Boardings', fmtInt(data.boardings)],
    ['Routes', fmtInt(data.routes_n)],
    ['Stops', fmtInt(data.stops_n)],
    ['Student share', fmtPct(data.student_share, 1)],
  ]
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {items.map(([label, value]) => (
        <div key={label} className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
          <div className="mt-1 text-xl font-semibold text-gray-900">{value}</div>
        </div>
      ))}
    </div>
  )
}

function PulsePanel() {
  const { data, isLoading, error } = useChart('health', '5.1')
  return (
    <ChartCard
      title={data?.title ?? ''}
      subtitle={data?.subtitle ?? ''}
      loading={isLoading}
      error={error?.message}
    >
      {data && <NetworkPulse resp={data} />}
    </ChartCard>
  )
}

export default function App() {
  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-900">HCMC Bus Analytics</h1>
      <KpiStrip />
      <PulsePanel />
    </div>
  )
}
