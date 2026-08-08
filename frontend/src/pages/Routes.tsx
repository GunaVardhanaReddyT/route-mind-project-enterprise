import { useState } from 'react'
import { Play, AlertTriangle, Sparkles, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import RouteMap from '../components/map/RouteMap'
import { useApp } from '../context/AppContext'
import { optimizeRoutes, replanRoute, OptimizationResult } from '../lib/api'
import { formatDistance, formatTime } from '../lib/utils'

const ROUTE_COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#10b981', '#ef4444']

const MOCK_DATA: OptimizationResult = {
  routes: [
    { vehicle_id: 1, stop_indices: [0, 1, 2], num_stops: 3, distance_km: 45.2 },
    { vehicle_id: 2, stop_indices: [3, 4], num_stops: 2, distance_km: 32.8 },
  ],
  total_distance_km: 78.0,
  solve_time_ms: 150,
  status: 'optimal',
  explanation: 'Demo mode: Routes optimized using mock data. Switch off Demo Mode in header to use real backend.',
  visualization: {
    depot: { lat: 28.6139, lon: 77.2090, label: 'Delhi Hub' },
    routes: [
      {
        route_id: 1,
        vehicle_plate: 'DL01AB1234',
        stops: [
          { lat: 28.6289, lon: 77.2194, address: 'Connaught Place' },
          { lat: 28.6562, lon: 77.2410, address: 'Kashmere Gate' },
          { lat: 28.5935, lon: 77.2270, address: 'Lajpat Nagar' },
        ],
        distance_km: 45.2,
        color: ROUTE_COLORS[0],
      },
      {
        route_id: 2,
        vehicle_plate: 'DL01CD5678',
        stops: [
          { lat: 28.5494, lon: 77.2501, address: 'Nehru Place' },
          { lat: 28.5245, lon: 77.2066, address: 'Saket' },
        ],
        distance_km: 32.8,
        color: ROUTE_COLORS[1],
      },
    ],
  },
}

export default function Routes() {
  const { hubId, demoMode } = useApp()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [selectedRouteId, setSelectedRouteId] = useState<number | undefined>()
  const [replanningRouteId, setReplanningRouteId] = useState<number | null>(null)
  const [showDetails, setShowDetails] = useState(true)

  const handleOptimize = async () => {
    if (demoMode) {
      setLoading(true)
      setTimeout(() => {
        setResult(MOCK_DATA)
        setLoading(false)
      }, 1000)
      return
    }

    // Check if non-Delhi hub selected
    if (hubId !== 1) {
      alert('The Routes page only has pre-seeded delivery stops for Delhi Hub.\n\nFor Mumbai and Bangalore, please use the "Live Routing" page where you can add stops manually.')
      return
    }

    setLoading(true)
    try {
      const data = await optimizeRoutes(hubId)
      setResult(data)
    } catch (err) {
      console.error('Optimization failed:', err)
      alert('Optimization failed. Check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  const handleReplan = async (routeId: number) => {
    if (demoMode) {
      alert('Replan simulation not available in demo mode')
      return
    }

    setReplanningRouteId(routeId)
    try {
      const data = await replanRoute(routeId, hubId, undefined, undefined, 'traffic_jam')
      setResult(data)
      alert('Route replanned successfully')
    } catch (err) {
      console.error('Replan failed:', err)
      alert('Replan failed')
    } finally {
      setReplanningRouteId(null)
    }
  }

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4 lg:gap-6">
      <div className="w-full lg:flex-1 flex flex-col order-2 lg:order-1">
        <Card className="flex-1 flex flex-col h-96 lg:h-full">
          <CardHeader className="flex-shrink-0">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <CardTitle className="text-base sm:text-lg">Route Visualization</CardTitle>
              <Button onClick={handleOptimize} disabled={loading} size="sm" className="w-full sm:w-auto">
                {loading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Optimize Routes
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-0">
            <RouteMap
              depot={result?.visualization?.depot}
              routes={result?.visualization?.routes}
              selectedRouteId={selectedRouteId}
            />
          </CardContent>
        </Card>
      </div>

      <div className="w-full lg:w-96 order-1 lg:order-2">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="lg:hidden w-full flex items-center justify-between p-3 bg-white dark:bg-slate-900 rounded-lg mb-4 border border-slate-200 dark:border-slate-800"
        >
          <span className="font-semibold text-sm">Route Details</span>
          {showDetails ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </button>

        <div className={`${showDetails ? 'flex' : 'hidden'} lg:flex flex-col space-y-4 lg:space-y-6 overflow-y-auto max-h-96 lg:max-h-full`}>
        {result && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Total Distance</span>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">
                    {formatDistance(result.total_distance_km)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Solve Time</span>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">
                    {formatTime(result.solve_time_ms)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Routes</span>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">
                    {result.routes.length}
                  </span>
                </div>
                {result.cache_hit !== undefined && (
                  <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
                    <Badge variant={result.cache_hit ? 'success' : 'default'}>
                      {result.cache_hit ? 'Cache Hit' : 'Fresh Compute'}
                    </Badge>
                  </div>
                )}
                {result.ai_cost_usd !== undefined && (
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 dark:text-slate-400">AI Cost</span>
                    <span className="text-slate-700 dark:text-slate-300">
                      ${result.ai_cost_usd.toFixed(4)}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Routes</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-slate-200 dark:divide-slate-800">
                  {result.visualization?.routes.map((route) => (
                    <div
                      key={route.route_id}
                      className={`p-4 cursor-pointer transition-colors ${
                        selectedRouteId === route.route_id
                          ? 'bg-slate-100 dark:bg-slate-800'
                          : 'hover:bg-slate-50 dark:hover:bg-slate-900'
                      }`}
                      onClick={() => setSelectedRouteId(
                        selectedRouteId === route.route_id ? undefined : route.route_id
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: route.color }}
                          />
                          <span className="font-semibold text-slate-900 dark:text-slate-100">
                            Route {route.route_id}
                          </span>
                        </div>
                        <Badge variant="default">{route.vehicle_plate}</Badge>
                      </div>
                      
                      <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400 mb-3">
                        <span>{route.stops.length} stops</span>
                        <span>{formatDistance(route.distance_km)}</span>
                      </div>

                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleReplan(route.route_id)
                        }}
                        disabled={replanningRouteId === route.route_id}
                        className="w-full"
                      >
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        {replanningRouteId === route.route_id ? 'Replanning...' : 'Simulate Traffic'}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {result.explanation && (
              <Card>
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <CardTitle>AI Explanation</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    {result.explanation}
                  </p>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {!result && !loading && (
          <Card>
            <CardContent className="py-12 text-center">
              <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-4" />
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Click "Optimize Routes" to start
              </p>
            </CardContent>
          </Card>
        )}
        </div>
      </div>
    </div>
  )
}
