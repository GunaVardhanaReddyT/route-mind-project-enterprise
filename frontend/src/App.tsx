import { useState, useEffect } from 'react'
import { AppProvider } from './context/AppContext'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Routes from './pages/Routes'
import Settings from './pages/Settings'
import Login from './pages/Login'
import { Menu, X } from 'lucide-react'

type Page = 'dashboard' | 'routes' | 'settings'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const savedToken = localStorage.getItem('routemind_token')
    if (savedToken) {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = (newToken: string) => {
    localStorage.setItem('routemind_token', newToken)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('routemind_token')
    setIsAuthenticated(false)
  }

  const handleNavigate = (page: Page) => {
    setCurrentPage(page)
    setSidebarOpen(false)
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'routes':
        return <Routes />
      case 'settings':
        return <Settings />
      default:
        return <Dashboard />
    }
  }

  return (
    <AppProvider>
      <div className={darkMode ? 'dark' : ''}>
        <div className="flex h-screen bg-slate-50 dark:bg-slate-950 overflow-hidden">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-slate-900 rounded-md shadow-lg text-slate-900 dark:text-slate-100"
          >
            {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>

          <div className={`fixed lg:static inset-0 z-40 lg:z-0 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-300 ease-in-out`}>
            {sidebarOpen && (
              <div className="lg:hidden fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
            )}
            <div className="relative">
              <Sidebar currentPage={currentPage} onNavigate={handleNavigate} />
            </div>
          </div>
          
          <div className="flex-1 flex flex-col overflow-hidden w-full">
            <Header 
              darkMode={darkMode} 
              onToggleDarkMode={() => setDarkMode(!darkMode)}
              onLogout={handleLogout}
            />
            
            <main className="flex-1 overflow-y-auto p-4 md:p-6">
              {renderPage()}
            </main>
          </div>
        </div>
      </div>
    </AppProvider>
  )
}

export default App
