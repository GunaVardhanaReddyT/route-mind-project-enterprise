import { LayoutDashboard, MapPin, Settings, Trophy, Zap } from 'lucide-react'

interface SidebarProps {
  currentPage: string
  onNavigate: (page: 'dashboard' | 'routes' | 'settings' | 'live') => void
}

export default function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const navItems = [
    { id: 'live', icon: Zap, label: 'Live Routing' },
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'routes', icon: MapPin, label: 'Routes' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
      <div className="p-6 border-b border-slate-200 dark:border-slate-800">
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">RouteMind</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Route Optimization Platform</p>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPage === item.id
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onNavigate(item.id as any)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-white'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-200 dark:border-slate-800">
        <div className="text-xs text-slate-500 dark:text-slate-400">
          AI Build 2026
        </div>
      </div>
    </div>
  )
}
