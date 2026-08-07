import { useState } from 'react'
import { Play, RefreshCw, MapPin, Truck } from 'lucide-react'

interface Route {
  vehicle_id: number
  stop_indices: number[]
  num_stops: number
  distance_km: number
}

interface OptimizationResult {
  routes: Route[]
  total_distance_km: number
  solve_time_ms: number
  status: string
  explanation?: string
  ai_cost_usd?: number
  cache_hit?: boolean
}

export default function RouteOptimizer() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [useAI, setUseAI] = useState(true)
  const [hubId, setHubId] = useState(1)

  const handleOptimize = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/v1/optimizer/optimize?hub_id=${hubId}&use_ai_explanation=${useAI}`, {
        method: 'POST'
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Optimization failed:', err)
      alert('Failed to optimize routes')
    } finally {
      setLoading(false)
    }
  }

  const handleReplan = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/v1/optimizer/replan?route_id=1&new_stop_id=5&reason=new_pickup&hub_id=${hubId}`, {
        method: 'POST'
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Replan failed:', err)
      alert('Failed to replan route')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Route Optimization</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hub ID
            </label>
            <input
              type="number"
              value={hubId}
              onChange={(e) => setHubId(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-end">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Use AI Explanation (+$0.001)
              </span>
            </label>
          </div>
        </div>

        <div className="flex space-x-4">
          <button
            onClick={handleOptimize}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            <Play className="h-5 w-5" />
            <span>{loading ? 'Optimizing...' : 'Optimize Routes'}</span>
          </button>

          <button
            onClick={handleReplan}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            <RefreshCw className="h-5 w-5" />
            <span>{loading ? 'Replanning...' : 'Replan (Demo)'}</span>
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Summary</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className={`text-lg font-semibold ${result.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                  {result.status.toUpperCase()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Routes</p>
                <p className="text-lg font-semibold text-gray-900">{result.routes.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Distance</p>
                <p className="text-lg font-semibold text-gray-900">{result.total_distance_km.toFixed(2)} km</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Solve Time</p>
                <p className="text-lg font-semibold text-gray-900">
                  {result.solve_time_ms < 1000 
                    ? `${result.solve_time_ms}ms` 
                    : `${(result.solve_time_ms / 1000).toFixed(1)}s`}
                </p>
              </div>
            </div>

            {result.cache_hit !== undefined && (
              <div className="mb-4 flex items-center space-x-2">
                {result.cache_hit ? (
                  <>
                    <div className="h-2 w-2 bg-green-500 rounded-full" />
                    <span className="text-sm text-green-600 font-medium">Cache Hit (50x faster!)</span>
                  </>
                ) : (
                  <>
                    <div className="h-2 w-2 bg-yellow-500 rounded-full" />
                    <span className="text-sm text-yellow-600 font-medium">Cache Miss (will be cached)</span>
                  </>
                )}
              </div>
            )}

            {result.explanation && (
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                <p className="text-sm font-medium text-blue-900 mb-1">AI Explanation</p>
                <p className="text-sm text-blue-800">{result.explanation}</p>
                {result.ai_cost_usd && (
                  <p className="text-xs text-blue-600 mt-2">Cost: ${result.ai_cost_usd.toFixed(4)}</p>
                )}
              </div>
            )}
          </div>

          {/* Routes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Route Details</h3>
            
            <div className="space-y-4">
              {result.routes.map((route, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Truck className="h-5 w-5 text-blue-600" />
                      <span className="font-semibold text-gray-900">
                        Vehicle {route.vehicle_id}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {route.distance_km.toFixed(2)} km
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <MapPin className="h-4 w-4" />
                    <span>{route.num_stops} stops</span>
                    <span className="text-gray-400">→</span>
                    <span>Indices: {route.stop_indices.join(' → ')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
