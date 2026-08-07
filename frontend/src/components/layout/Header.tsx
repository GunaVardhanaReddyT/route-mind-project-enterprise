import { Moon, Sun, ToggleLeft, ToggleRight, LogOut } from 'lucide-react'
import { useApp } from '../../context/AppContext'

interface HeaderProps {
  darkMode: boolean
  onToggleDarkMode: () => void
  onLogout?: () => void
}

export default function Header({ darkMode, onToggleDarkMode, onLogout }: HeaderProps) {
  const { hubId, setHubId, demoMode, setDemoMode } = useApp()

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <select
          value={hubId}
          onChange={(e) => setHubId(Number(e.target.value))}
          className="px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value={1}>Hub 1 - Delhi NCR</option>
          <option value={2}>Hub 2 - Mumbai</option>
          <option value={3}>Hub 3 - Bangalore</option>
        </select>
      </div>

      <div className="flex items-center space-x-4">
        <button
          onClick={() => setDemoMode(!demoMode)}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
        >
          {demoMode ? <ToggleRight className="h-5 w-5 text-success" /> : <ToggleLeft className="h-5 w-5" />}
          <span className="font-medium">Demo Mode</span>
        </button>

        <button
          onClick={onToggleDarkMode}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="h-5 w-5 text-slate-300" /> : <Moon className="h-5 w-5 text-slate-700" />}
        </button>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Admin</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">Supervisor</div>
          </div>
          <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
            A
          </div>
          {onLogout && (
            <button
              onClick={onLogout}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors text-slate-700 dark:text-slate-300"
              aria-label="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
