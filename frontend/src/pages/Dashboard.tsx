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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="h-32"><div /></CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const stats = [
    {
      label: 'Routes Optimized',
      value: metrics.performance.total_optimizations,
      subtitle: 'Total routes computed',
      color: 'text-blue-600',
      bg: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      label: 'Distance Saved',
      value: formatDistance(metrics.business_impact.vs_baseline.distance_saved_km),
      subtitle: 'vs naive greedy baseline',
      color: 'text-green-600',
      bg: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      label: 'Avg Solve Time',
      value: formatTime(metrics.performance.avg_solve_time_ms),
      subtitle: 'Per optimization',
      color: 'text-purple-600',
      bg: 'bg-purple-100 dark:bg-purple-900/20',
    },
  ]

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat, i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
                <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-2">{stat.value}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{stat.subtitle}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Business Impact</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Efficiency Gain</span>
              <span className="text-xl font-bold text-success">
                {metrics.business_impact.vs_baseline.efficiency_gain_percent}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Fuel Savings</span>
              <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {formatCurrency(metrics.business_impact.vs_baseline.estimated_fuel_saved_inr)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">AI Cost Efficiency</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Cost per Route</span>
              <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {formatCurrency(metrics.business_impact.cost_per_route_usd, 'USD')}
              </span>
            </div>
            <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
              <p className="text-sm text-success font-medium">
                100x cheaper than pure LLM routing
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
