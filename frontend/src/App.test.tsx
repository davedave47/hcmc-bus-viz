import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { ChartResponse } from './api/types'
import { buildPulse } from './charts/health/pulse'
import ChartCard from './components/ChartCard'

describe('buildPulse', () => {
  it('builds traces + a Tết band from the contract', () => {
    const resp: ChartResponse = {
      theme: 'health',
      slug: '5.1',
      title: 'T',
      subtitle: 'S',
      series: [
        { day: '2026-02-13', boardings: 200000 },
        { day: '2026-02-16', boardings: 33000 },
      ],
      encoding: {},
      meta: {
        tet_start: '2026-02-14',
        tet_end: '2026-02-22',
        trough: '2026-02-16',
        baseline: 210000,
        min_drop_pct: 84,
      },
    }
    const { data, layout } = buildPulse(resp)
    expect(data.length).toBeGreaterThanOrEqual(2)
    expect(layout.shapes?.length).toBe(1)
  })
})

describe('ChartCard', () => {
  it('renders title + subtitle', () => {
    render(<ChartCard title="Hello" subtitle="World" />)
    expect(screen.getByRole('heading', { name: 'Hello' })).toBeInTheDocument()
    expect(screen.getByText('World')).toBeInTheDocument()
  })
})
