import { useState } from 'react'
import api from '../lib/api'
import { Button } from '../components/ui/Button'

interface ComparisonResult {
  route_id: string
  dataset: string
  num_stops: number
  solve_time_ms: number
  comparison: {
    baseline_naive: {
      distance_km: number
      score: number
      method: string
    }
    constrained: {
      distance_km: number
      improvement_percent: number
      method: string
    }
    ai_enhanced: {
      distance_km: number
      improvement_percent: number
      method: string
    }
  }
  verdict: {
    ai_wins: boolean
    message: string
    hackathon_ready: boolean
  }
  data_source: string
}

export function AmazonChallenge() {
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [result, setResult] = useState<ComparisonResult | null>(null)
  const [routes, setRoutes] = useState<string[]>([])
  const [selectedRoute, setSelectedRoute] = useState<string>('')
  const [error, setError] = useState<string>('')

  const downloadDataset = async () => {
    setDownloading(true)
    setError('')
    try {
      const response = await api.post('/amazon/download')
      alert(`Downloaded ${response.data.routes_downloaded} real Amazon routes!`)
      loadRoutes()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Download failed')
    } finally {
      setDownloading(false)
    }
  }

  const loadRoutes = async () => {
    try {
      const response = await api.get('/amazon/routes?limit=50')
      setRoutes(response.data.routes)
      if (response.data.routes.length > 0) {
        setSelectedRoute(response.data.routes[0])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load routes')
    }
  }

  const runChallenge = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    
    try {
      const response = await api.post('/amazon/optimize', {
        route_id: selectedRoute || null,
        use_ai: true,
        use_osm: true
      })
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Optimization failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Amazon Challenge Mode</h1>
        <p className="text-gray-600 mt-2">
          Real Amazon dataset (9,184 routes, 1M+ stops) - Prove AI beats OR-Tools baseline
        </p>
      </div>

      {/* Download Dataset */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Step 1: Download Dataset</h2>
        <p className="text-sm text-gray-600 mb-4">
          Downloads real Amazon delivery routes from AWS Open Data Registry (public, no auth needed)
        </p>
        <Button onClick={downloadDataset} disabled={downloading}>
          {downloading ? 'Downloading...' : 'Download Amazon Dataset'}
        </Button>
        {routes.length > 0 && (
          <p className="text-sm text-green-600 mt-2">
            ✅ {routes.length} routes loaded
          </p>
        )}
      </div>

      {/* Run Challenge */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Step 2: Run Optimization Challenge</h2>
        
        {routes.length > 0 && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Route
            </label>
            <select
              value={selectedRoute}
              onChange={(e) => setSelectedRoute(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 w-full"
            >
              {routes.map((route) => (
                <option key={route} value={route}>
                  {route}
                </option>
              ))}
            </select>
          </div>
        )}
        
        <Button onClick={runChallenge} disabled={loading || routes.length === 0}>
          {loading ? 'Optimizing...' : 'Run Challenge'}
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Results</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Route: {result.route_id} | {result.num_stops} stops | Solved in {result.solve_time_ms}ms
                </p>
              </div>
              {result.verdict.hackathon_ready && (
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  🏆 Hackathon Ready
                </span>
              )}
            </div>
          </div>

          {/* Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Baseline */}
            <div className="bg-gray-50 p-6 rounded-lg border-2 border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">Baseline (Naive)</h3>
              <p className="text-xs text-gray-600 mb-4">{result.comparison.baseline_naive.method}</p>
              <div className="text-3xl font-bold text-gray-700">
                {result.comparison.baseline_naive.distance_km} km
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Amazon score: {result.comparison.baseline_naive.score.toFixed(3)}
              </p>
            </div>

            {/* Constrained */}
            <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-300">
              <h3 className="font-semibold text-blue-900 mb-2">OR-Tools + Constraints</h3>
              <p className="text-xs text-blue-700 mb-4">{result.comparison.constrained.method}</p>
              <div className="text-3xl font-bold text-blue-700">
                {result.comparison.constrained.distance_km} km
              </div>
              <p className="text-sm text-blue-600 mt-2 font-medium">
                {result.comparison.constrained.improvement_percent > 0 ? '↓' : '↑'} 
                {Math.abs(result.comparison.constrained.improvement_percent)}% improvement
              </p>
            </div>

            {/* AI Enhanced */}
            <div className={`p-6 rounded-lg border-2 ${
              result.verdict.ai_wins 
                ? 'bg-green-50 border-green-400' 
                : 'bg-yellow-50 border-yellow-400'
            }`}>
              <h3 className={`font-semibold mb-2 ${result.verdict.ai_wins ? 'text-green-900' : 'text-yellow-900'}`}>
                AI Enhanced (RouteMind)
              </h3>
              <p className={`text-xs mb-4 ${result.verdict.ai_wins ? 'text-green-700' : 'text-yellow-700'}`}>
                {result.comparison.ai_enhanced.method}
              </p>
              <div className={`text-3xl font-bold ${result.verdict.ai_wins ? 'text-green-700' : 'text-yellow-700'}`}>
                {result.comparison.ai_enhanced.distance_km} km
              </div>
              <p className={`text-sm mt-2 font-medium ${result.verdict.ai_wins ? 'text-green-600' : 'text-yellow-600'}`}>
                {result.comparison.ai_enhanced.improvement_percent > 0 ? '↓' : '↑'}
                {Math.abs(result.comparison.ai_enhanced.improvement_percent)}% improvement
              </p>
            </div>
          </div>

          {/* Verdict */}
          <div className={`p-6 rounded-lg ${
            result.verdict.ai_wins ? 'bg-green-100' : 'bg-yellow-100'
          }`}>
            <h3 className="font-bold text-lg mb-2">
              {result.verdict.ai_wins ? '🎉 AI Wins!' : '⚠️  AI Needs Tuning'}
            </h3>
            <p className="text-gray-800">{result.verdict.message}</p>
          </div>

          {/* Citation */}
          <div className="bg-gray-50 p-4 rounded text-xs text-gray-600">
            <p className="font-medium mb-1">Data Source:</p>
            <p>
              Amazon Last Mile Routing Research Challenge 2021 (Merchán et al., Transportation Science)
            </p>
            <a 
              href={result.data_source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {result.data_source}
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
