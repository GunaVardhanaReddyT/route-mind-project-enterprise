import { useState, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMapEvents } from 'react-leaflet'
import { Button } from '../components/ui/Button'
import api from '../lib/api'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const HUBS = [
  { id: 1, name: 'Delhi', lat: 28.6139, lon: 77.2090 },
  { id: 2, name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
  { id: 3, name: 'Bangalore', lat: 12.9716, lon: 77.5946 },
]

interface Stop {
  lat: number
  lon: number
  address: string
  priority: string
}

function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

export function LiveRouting() {
  const [hubId, setHubId] = useState(1)
  const [inputStops, setInputStops] = useState<Stop[]>([])
  const [vehicles, setVehicles] = useState(2)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [selectedAlt, setSelectedAlt] = useState(0)
  
  const selectedHub = HUBS.find(h => h.id === hubId) || HUBS[0]
  
  // Add stop by clicking on input map
  const handleInputMapClick = (lat: number, lng: number) => {
    setInputStops([
      ...inputStops,
      {
        lat,
        lon: lng,
        address: `Stop ${inputStops.length + 1}`,
        priority: 'medium'
      }
    ])
  }
  
  // Remove last stop
  const removeLastStop = () => {
    setInputStops(inputStops.slice(0, -1))
  }
  
  // Clear all
  const clearAll = () => {
    setInputStops([])
    setResult(null)
  }
  
  // Optimize
  const optimizeRoutes = async () => {
    if (inputStops.length < 2) {
      alert('Add at least 2 stops!')
      return
    }
    
    setLoading(true)
    try {
      const response = await api.post('/live/optimize', {
        hub_id: hubId,
        stops: inputStops.map(s => ({
          lat: s.lat,
          lon: s.lon,
          address: s.address,
          priority: s.priority,
          package_count: 1,
          weight_kg: 10.0,
          time_window_start: '09:00',
          time_window_end: '17:00'
        })),
        vehicles: Array.from({ length: vehicles }, (_, i) => ({
          id: i + 1,
          name: `Vehicle ${i + 1}`,
          capacity_kg: 500.0
        })),
        generate_alternatives: 3,
        use_ai_explanation: true
      })
      setResult(response.data)
      setSelectedAlt(0)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Optimization failed')
    } finally {
      setLoading(false)
    }
  }
  
  const currentAlt = result?.alternatives?.[selectedAlt]
  
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Live Routing</h1>
        <p className="text-gray-600 mt-2">
          Click on INPUT map to add stops → Get optimized routes on OUTPUT map with AI explanation
        </p>
      </div>
      
      {/* Controls */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Hub</label>
            <select
              value={hubId}
              onChange={(e) => setHubId(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              {HUBS.map(h => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Vehicles</label>
            <input
              type="number"
              value={vehicles}
              onChange={(e) => setVehicles(Number(e.target.value))}
              min="1"
              max="5"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Stops Added</label>
            <div className="text-2xl font-bold text-blue-600">{inputStops.length}</div>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button onClick={optimizeRoutes} disabled={loading || inputStops.length < 2}>
            {loading ? 'Optimizing...' : 'Optimize Routes'}
          </Button>
          <button
            onClick={removeLastStop}
            disabled={inputStops.length === 0}
            className="px-4 py-2 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            Remove Last
          </button>
          <button
            onClick={clearAll}
            className="px-4 py-2 border rounded hover:bg-gray-50"
          >
            Clear All
          </button>
        </div>
      </div>
      
      {/* Two Maps Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* INPUT MAP */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-2">INPUT: Click to Add Stops</h2>
          <div className="h-96 rounded-lg overflow-hidden border">
            <MapContainer
              center={[selectedHub.lat, selectedHub.lon]}
              zoom={11}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <MapClickHandler onMapClick={handleInputMapClick} />
              
              {/* Depot */}
              <Marker position={[selectedHub.lat, selectedHub.lon]}>
                <Popup>🏢 {selectedHub.name} Hub (Depot)</Popup>
              </Marker>
              
              {/* Input stops */}
              {inputStops.map((stop, idx) => (
                <Marker key={idx} position={[stop.lat, stop.lon]}>
                  <Popup>
                    📦 {stop.address}<br/>
                    Priority: {stop.priority}
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Click anywhere on map to add delivery stops
          </p>
        </div>
        
        {/* OUTPUT MAP */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold">OUTPUT: Optimized Routes</h2>
            {result && (
              <span className="text-sm text-green-600 font-medium">
                ✓ {result.performance.solve_time_ms}ms
              </span>
            )}
          </div>
          
          <div className="h-96 rounded-lg overflow-hidden border">
            {result ? (
              <MapContainer
                center={[selectedHub.lat, selectedHub.lon]}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                
                {/* Depot */}
                <Marker position={[selectedHub.lat, selectedHub.lon]}>
                  <Popup>🏢 {selectedHub.name} Hub</Popup>
                </Marker>
                
                {/* Routes */}
                {currentAlt?.routes.map((route: any, idx: number) => (
                  <div key={idx}>
                    {/* Road path */}
                    {route.road_path && route.road_path.length > 0 && (
                      <Polyline
                        positions={route.road_path.map((p: any) => [p[1], p[0]])}
                        color={route.color}
                        weight={4}
                        opacity={0.7}
                      />
                    )}
                    
                    {/* Stops */}
                    {route.stops.map((stop: any, stopIdx: number) => (
                      <Marker key={stopIdx} position={[stop.lat, stop.lon]}>
                        <Popup>
                          {route.vehicle_name}<br/>
                          {stop.address}<br/>
                          Priority: {stop.priority}
                        </Popup>
                      </Marker>
                    ))}
                  </div>
                ))}
              </MapContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Run optimization to see routes
              </div>
            )}
          </div>
          
          {result && (
            <div className="mt-2 text-sm text-gray-600">
              {currentAlt?.is_best && <span className="text-green-600 font-bold">★ BEST </span>}
              {currentAlt?.description} - {currentAlt?.total_distance_km} km
            </div>
          )}
        </div>
      </div>
      
      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Alternatives Tabs */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-bold mb-3">All Alternatives</h3>
            <div className="flex gap-2 flex-wrap">
              {result.alternatives.map((alt: any, idx: number) => (
                <button
                  key={idx}
                  onClick={() => setSelectedAlt(idx)}
                  className={`px-4 py-2 rounded border ${
                    selectedAlt === idx
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white hover:bg-gray-50'
                  }`}
                >
                  {alt.is_best && '⭐ '}
                  Option {alt.rank}: {alt.total_distance_km} km
                </button>
              ))}
            </div>
          </div>
          
          {/* AI Explanation */}
          {result.best_route?.ai_explanation && (
            <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg shadow">
              <h3 className="font-bold text-xl mb-3">🤖 AI Explanation</h3>
              
              <p className="text-gray-800 mb-4">{result.best_route.ai_explanation.summary}</p>
              
              <div className="space-y-2 mb-4">
                <h4 className="font-semibold">Why This Route is Optimal:</h4>
                {result.best_route.ai_explanation.why_optimal.map((reason: string, idx: number) => (
                  <div key={idx} className="text-sm text-gray-700">{reason}</div>
                ))}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                {result.best_route.ai_explanation.key_optimizations.map((opt: any, idx: number) => (
                  <div key={idx} className="bg-white p-3 rounded">
                    <div className="font-semibold text-sm">{opt.type}</div>
                    <div className="text-2xl font-bold text-blue-600">{opt.value}</div>
                    <div className="text-xs text-gray-600">{opt.benefit}</div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-semibold mb-2">Real-World Impact:</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Fuel Saved: </span>
                    <span className="font-bold">{result.best_route.ai_explanation.real_world_impact.fuel_saved_liters}L</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Time Saved: </span>
                    <span className="font-bold">{result.best_route.ai_explanation.real_world_impact.time_saved_minutes} min</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Cost Saved: </span>
                    <span className="font-bold">₹{result.best_route.ai_explanation.real_world_impact.cost_saved_inr}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
