import { useState, useEffect } from 'react'
import { TrendingUp, DollarSign, Zap, Clock } from 'lucide-react'
// Charts removed for simplicity

interface MetricsData {
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

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMetrics()
    const interval = setInterval(loadMetrics, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const loadMetrics = async () => {
    try {
      const res = await fetch('/api/v1/metrics')
      const data = await res.json()
      setMetrics(data)
    } catch (err) {
      console.error('Failed to load metrics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  if (!metrics) {
    return <div className="text-center py-12 text-red-600">Failed to load metrics</div>
  }

  const stats = [
    {
      name: 'Total Routes',
      value: metrics.performance.total_optimizations,
      icon: TrendingUp,
      color: 'text-blue-600',
      bg: 'bg-blue-100'
    },
    {
      name: 'Avg Solve Time',
      value: `${(metrics.performance.avg_solve_time_ms / 1000).toFixed(1)}s`,
      icon: Clock,
      color: 'text-green-600',
      bg: 'bg-green-100'
    },
    {
      name: 'Distance Saved',
      value: `${metrics.business_impact.vs_baseline.distance_saved_km.toFixed(1)} km`,
      icon: Zap,
      color: 'text-yellow-600',
      bg: 'bg-yellow-100'
    },
    {
      name: 'Fuel Savings',
      value: `₹${metrics.business_impact.vs_baseline.estimated_fuel_saved_inr.toFixed(0)}`,
      icon: DollarSign,
      color: 'text-green-600',
      bg: 'bg-green-100'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`${stat.bg} p-3 rounded-lg`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Efficiency Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficiency vs Baseline</h3>
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="text-4xl font-bold text-green-600">
              {metrics.business_impact.vs_baseline.efficiency_gain_percent}%
            </div>
            <p className="text-sm text-gray-600 mt-1">Better than naive greedy</p>
          </div>
          <div className="flex-1 text-right">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.performance.total_distance_optimized_km.toFixed(1)} km
            </div>
            <p className="text-sm text-gray-600 mt-1">Total optimized</p>
          </div>
        </div>
      </div>

      {/* Cost Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Per Route</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">AI Cost</span>
            <span className="font-semibold">${metrics.business_impact.total_ai_cost_usd.toFixed(4)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Cost Per Route</span>
            <span className="font-semibold">${metrics.business_impact.cost_per_route_usd.toFixed(4)}</span>
          </div>
          <div className="border-t pt-3">
            <p className="text-sm text-green-600 font-medium">
              100x cheaper than pure LLM approach ($0.10/route)
            </p>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">CPU Usage</p>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${metrics.system_health.cpu_percent}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">{metrics.system_health.cpu_percent.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Memory Usage</p>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: `${metrics.system_health.memory_percent}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">{metrics.system_health.memory_percent.toFixed(1)}%</p>
          </div>
        </div>
        <div className="mt-4 flex items-center space-x-2">
          <div className={`h-3 w-3 rounded-full ${metrics.system_health.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">Status: {metrics.system_health.status}</span>
        </div>
      </div>
    </div>
  )
}
