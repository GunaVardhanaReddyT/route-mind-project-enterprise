import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Clock, Zap, DollarSign } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { getMetrics, MetricsData } from '../lib/api'
import { formatDistance, formatTime, formatCurrency } from '../lib/utils'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMetrics()
    const interval = setInterval(loadMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadMetrics = async () => {
    try {
      const data = await getMetrics()
      setMetrics(data)
    } catch (err) {
      console.error('Failed to load metrics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="h-32"><div /></CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const stats = [
    {
      label: 'Total Routes',
      value: metrics.performance.total_optimizations,
      icon: TrendingUp,
      color: 'text-blue-600',
      bg: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      label: 'Avg Solve Time',
      value: formatTime(metrics.performance.avg_solve_time_ms),
      icon: Clock,
      color: 'text-green-600',
      bg: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      label: 'Distance Saved',
      value: formatDistance(metrics.business_impact.vs_baseline.distance_saved_km),
      icon: Zap,
      color: 'text-yellow-600',
      bg: 'bg-yellow-100 dark:bg-yellow-900/20',
    },
    {
      label: 'Fuel Savings',
      value: formatCurrency(metrics.business_impact.vs_baseline.estimated_fuel_saved_inr),
      icon: DollarSign,
      color: 'text-green-600',
      bg: 'bg-green-100 dark:bg-green-900/20',
    },
  ]

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <Card key={i}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.bg} p-3 rounded-md`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Efficiency vs Baseline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-4xl font-bold text-success">
                  {metrics.business_impact.vs_baseline.efficiency_gain_percent}%
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Better than naive greedy</p>
              </div>
              <TrendingDown className="h-12 w-12 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost Per Route</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600 dark:text-slate-400">AI Cost</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">
                  {formatCurrency(metrics.business_impact.total_ai_cost_usd, 'USD')}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600 dark:text-slate-400">Per Route</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">
                  {formatCurrency(metrics.business_impact.cost_per_route_usd, 'USD')}
                </span>
              </div>
              <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
                <p className="text-sm text-success font-medium">
                  100x cheaper than pure LLM
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Total Optimizations</span>
              <span className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {metrics.performance.total_optimizations}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Total Re-plans</span>
              <span className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {metrics.performance.total_replans}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Distance Optimized</span>
              <span className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {formatDistance(metrics.performance.total_distance_optimized_km)}
              </span>
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${metrics.system_health.status === 'healthy' ? 'bg-success' : 'bg-danger'}`} />
              <span className="text-sm text-slate-600 dark:text-slate-400">
                System: {metrics.system_health.status}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
