import type { ReactNode } from 'react'

interface Props {
  title: string
  subtitle: string
  loading?: boolean
  error?: string
  children?: ReactNode
}

export default function ChartCard({ title, subtitle, loading, error, children }: Props) {
  return (
    <section className="rounded-lg border border-gray-200 bg-white p-5">
      <h2 className="text-lg font-semibold text-gray-900">{title || ' '}</h2>
      <p className="mt-0.5 text-sm text-gray-500">{subtitle}</p>
      <div className="mt-3 h-[460px]">
        {loading ? (
          <div className="grid h-full place-items-center text-gray-400">Loading…</div>
        ) : error ? (
          <div className="grid h-full place-items-center text-red-500">Error: {error}</div>
        ) : (
          children
        )}
      </div>
    </section>
  )
}
