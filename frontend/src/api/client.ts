import type { ChartResponse, FilterOptions, Kpis } from './types'

// '' in dev → Vite proxies /api to the backend; set VITE_API_BASE for other hosts.
const BASE = import.meta.env.VITE_API_BASE ?? ''

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

export const api = {
  chart: (theme: string, slug: string, params?: Record<string, string>): Promise<ChartResponse> => {
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params)}` : ''
    return get<ChartResponse>(`/api/charts/${theme}/${slug}${qs}`)
  },
  kpis: (): Promise<Kpis> => get<Kpis>('/api/kpis'),
  filters: (): Promise<FilterOptions> => get<FilterOptions>('/api/filters'),
}
