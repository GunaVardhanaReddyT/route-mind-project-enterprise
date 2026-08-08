import axios from 'axios'

const api = axios.create({
  baseURL: `http://${window.location.hostname}:8002/api/v1`,
  timeout: 30000,
})

export interface Route {
  vehicle_id: number
  stop_indices: number[]
  num_stops: number
  distance_km: number
}

export interface OptimizationResult {
  routes: Route[]
  total_distance_km: number
  solve_time_ms: number
  status: string
  explanation?: string
  ai_cost_usd?: number
  cache_hit?: boolean
  visualization?: {
    depot: { lat: number; lon: number; label: string }
    routes: Array<{
      route_id: number
      vehicle_plate: string
      stops: Array<{ lat: number; lon: number; address: string }>
      distance_km: number
      color: string
    }>
  }
}

export interface MetricsData {
  performance: {
    total_optimizations: number
    total_replans: number
    avg_solve_time_ms: number
    total_distance_optimized_km: number
  }
  business_impact: {
    total_ai_cost_usd: number
    cost_per_route_usd: number
    vs_baseline: {
      distance_saved_km: number
      estimated_fuel_saved_inr: number
      efficiency_gain_percent: number
    }
  }
  system_health: {
    cpu_percent: number
    memory_percent: number
    status: string
  }
}

export const optimizeRoutes = async (hubId: number): Promise<OptimizationResult> => {
  const response = await api.post(`/optimizer/optimize?hub_id=${hubId}`)
  return response.data
}

export const replanRoute = async (
  routeId: number,
  hubId: number,
  newStopId?: number,
  failedStopId?: number,
  reason: string = 'traffic'
): Promise<OptimizationResult> => {
  const params = new URLSearchParams({
    route_id: routeId.toString(),
    hub_id: hubId.toString(),
    reason,
  })
  
  if (newStopId) params.append('new_stop_id', newStopId.toString())
  if (failedStopId) params.append('failed_stop_id', failedStopId.toString())
  
  const response = await api.post(`/optimizer/replan?${params}`)
  return response.data
}

export const getMetrics = async (): Promise<MetricsData> => {
  const response = await api.get('/metrics')
  return response.data
}

export const getCostAnalysis = async () => {
  const response = await api.get('/cost-analysis')
  return response.data
}

export const getHubs = async () => {
  const response = await api.get('/hubs')
  return response.data
}

export default api
