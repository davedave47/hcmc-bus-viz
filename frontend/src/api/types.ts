// Mirrors the backend contract (busanalytics_api/schemas). Hand-kept now; a
// future step generates these from the FastAPI OpenAPI schema.

export interface ChartResponse {
  theme: string
  slug: string
  title: string
  subtitle: string
  series: Record<string, unknown>[]
  encoding: Record<string, unknown>
  meta: Record<string, unknown>
}

export interface Kpis {
  boardings: number
  revenue: number
  student_share: number
  routes_n: number
  stops_n: number
  metro_feeders: number
}

export interface FilterOptions {
  routes: string[]
  day_types: string[]
  segments: string[]
  date_range: { min: string | null; max: string | null }
}
