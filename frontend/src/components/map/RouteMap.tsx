import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface RouteMapProps {
  depot?: { lat: number; lon: number; label: string }
  routes?: Array<{
    route_id: number
    vehicle_plate: string
    stops: Array<{ lat: number; lon: number; address: string }>
    distance_km: number
    color: string
  }>
  selectedRouteId?: number
}

export default function RouteMap({ depot, routes, selectedRouteId }: RouteMapProps) {
  const map = useMap()

  useEffect(() => {
    if (depot && map) {
      // Center map on the depot location
      map.setView([depot.lat, depot.lon], 12)
    }
  }, [depot, map])

  useEffect(() => {
    if (depot && routes && routes.length > 0 && map) {
      const bounds = L.latLngBounds([])
      bounds.extend([depot.lat, depot.lon])
      
      routes.forEach(route => {
        route.stops.forEach((stop: any) => {
          bounds.extend([stop.lat, stop.lon])
        })
      })
      
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] })
      }
    }
  }, [depot, routes, map])

  return null
}

export default function RouteMap({ depot, routes, selectedRouteId }: RouteMapProps) {
  const defaultCenter: [number, number] = depot ? [depot.lat, depot.lon] : [20.5937, 78.9629]
  const defaultZoom = depot ? 12 : 5

  const depotIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  })

  const stopIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  })

  return (
    <MapContainer
      center={defaultCenter}
      zoom={defaultZoom}
      className="h-full w-full rounded-md"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
      />

      {depot && (
        <Marker position={[depot.lat, depot.lon]} icon={depotIcon}>
          <Popup>
            <div className="text-sm">
              <div className="font-semibold">Depot</div>
              <div className="text-slate-600">{depot.label}</div>
            </div>
          </Popup>
        </Marker>
      )}

      {routes && routes.map((route) => {
        const isSelected = selectedRouteId === route.route_id
        const opacity = selectedRouteId === undefined || isSelected ? 1 : 0.3
        
        return (
          <div key={route.route_id}>
            {route.stops.map((stop, idx) => (
              <Marker key={`${route.route_id}-${idx}`} position={[stop.lat, stop.lon]} icon={stopIcon} opacity={opacity}>
                <Popup>
                  <div className="text-sm">
                    <div className="font-semibold">Stop {idx + 1}</div>
                    <div className="text-slate-600">{stop.address}</div>
                    <div className="text-xs text-slate-500 mt-1">Route {route.route_id}</div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {depot && route.stops.length > 0 && (
              <Polyline
                positions={[
                  [depot.lat, depot.lon],
                  ...route.stops.map(s => [s.lat, s.lon] as [number, number]),
                  [depot.lat, depot.lon]
                ]}
                color={route.color}
                weight={isSelected ? 4 : 3}
                opacity={opacity}
              />
            )}
          </div>
        )
      })}

      <FitBounds depot={depot} routes={routes} />
    </MapContainer>
  )
}

function FitBounds({ depot, routes }: { depot?: any; routes?: any[] }) {
  const map = useMap()

  useEffect(() => {
    if (depot && map) {
      map.setView([depot.lat, depot.lon], 12)
    }
  }, [depot, map])

  useEffect(() => {
    if (depot && routes && routes.length > 0 && map) {
      const bounds = L.latLngBounds([])
      bounds.extend([depot.lat, depot.lon])
      
      routes.forEach(route => {
        route.stops.forEach((stop: any) => {
          bounds.extend([stop.lat, stop.lon])
        })
      })
      
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] })
      }
    }
  }, [depot, routes, map])

  return null
}
