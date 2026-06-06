import { useQuery } from '@tanstack/react-query'

import { api } from '../api/client'
import type { ChartResponse } from '../api/types'

export function useChart(theme: string, slug: string, params?: Record<string, string>) {
  return useQuery<ChartResponse>({
    queryKey: ['chart', theme, slug, params ?? {}],
    queryFn: () => api.chart(theme, slug, params),
  })
}
