import { useState, useEffect } from 'react'
import { AppProvider } from './context/AppContext'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Routes from './pages/Routes'
import Settings from './pages/Settings'
import Login from './pages/Login'

type Page = 'dashboard' | 'routes' | 'settings'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Check for saved token
    const savedToken = localStorage.getItem('routemind_token')
    if (savedToken) {
      setToken(savedToken)
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = (newToken: string) => {
    localStorage.setItem('routemind_token', newToken)
    setToken(newToken)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('routemind_token')
    setToken(null)
    setIsAuthenticated(false)
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
        <div className="flex h-screen bg-slate-50 dark:bg-slate-950">
          <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
          
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header 
              darkMode={darkMode} 
              onToggleDarkMode={() => setDarkMode(!darkMode)}
              onLogout={handleLogout}
            />
            
            <main className="flex-1 overflow-y-auto p-6">
              {renderPage()}
            </main>
          </div>
        </div>
      </div>
    </AppProvider>
  )
}

export default App
