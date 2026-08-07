import { createContext, useContext, useState, ReactNode } from 'react'

interface AppContextType {
  hubId: number
  setHubId: (id: number) => void
  demoMode: boolean
  setDemoMode: (mode: boolean) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [hubId, setHubId] = useState(1)
  const [demoMode, setDemoMode] = useState(false)

  return (
    <AppContext.Provider value={{ hubId, setHubId, demoMode, setDemoMode }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
