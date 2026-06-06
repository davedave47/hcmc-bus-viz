import { useQuery } from '@tanstack/react-query'

import { api } from '../api/client'
import type { Kpis } from '../api/types'

export function useKpis() {
  return useQuery<Kpis>({ queryKey: ['kpis'], queryFn: api.kpis })
}
