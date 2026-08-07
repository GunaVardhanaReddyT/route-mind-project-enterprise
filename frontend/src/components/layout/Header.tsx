import { Moon, Sun, ToggleLeft, ToggleRight, LogOut } from 'lucide-react'
import { useApp } from '../../context/AppContext'
import { useEffect } from 'react'
import { getHubs } from '../../lib/api'

interface HeaderProps {
  darkMode: boolean
  onToggleDarkMode: () => void
  onLogout?: () => void
}

export default function Header({ darkMode, onToggleDarkMode, onLogout }: HeaderProps) {
  const { hubId, setHubId, demoMode, setDemoMode, hubs, setHubs } = useApp()

  useEffect(() => {
    loadHubs()
  }, [])

  const loadHubs = async () => {
    try {
      const data = await getHubs()
      setHubs(data)
    } catch (err) {
      // Use fallback hubs
      setHubs([
        { id: 1, name: 'Delhi NCR', city: 'Delhi' },
        { id: 2, name: 'Mumbai', city: 'Mumbai' },
        { id: 3, name: 'Bangalore', city: 'Bangalore' },
      ])
    }
  }

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 md:px-6">
      <div className="flex items-center space-x-2 md:space-x-4">
        <select
          value={hubId}
          onChange={(e) => setHubId(Number(e.target.value))}
          className="px-2 md:px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {hubs.length > 0 ? (
            hubs.map((hub) => (
              <option key={hub.id} value={hub.id}>
                {hub.city}
              </option>
            ))
          ) : (
            <>
              <option value={1}>Delhi NCR</option>
              <option value={2}>Mumbai</option>
              <option value={3}>Bangalore</option>
            </>
          )}
        </select>
      </div>

      <div className="flex items-center space-x-1 md:space-x-4">
        <button
          onClick={() => setDemoMode(!demoMode)}
          className="flex items-center space-x-1 md:space-x-2 px-2 md:px-3 py-2 text-xs md:text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
        >
          {demoMode ? <ToggleRight className="h-4 w-4 md:h-5 md:w-5 text-success" /> : <ToggleLeft className="h-4 w-4 md:h-5 md:w-5" />}
          <span className="hidden sm:inline font-medium">Demo</span>
        </button>

        <button
          onClick={onToggleDarkMode}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="h-4 w-4 md:h-5 md:w-5 text-slate-300" /> : <Moon className="h-4 w-4 md:h-5 md:w-5 text-slate-700" />}
        </button>

        <div className="flex items-center space-x-2 md:space-x-3">
          <div className="hidden md:block text-right">
            <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Admin</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">Supervisor</div>
          </div>
          <div className="h-8 w-8 md:h-10 md:w-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold text-sm md:text-base">
            A
          </div>
          {onLogout && (
            <button
              onClick={onLogout}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors text-slate-700 dark:text-slate-300"
              aria-label="Logout"
            >
              <LogOut className="h-4 w-4 md:h-5 md:w-5" />
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
