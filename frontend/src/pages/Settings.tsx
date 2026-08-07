import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Info } from 'lucide-react'

export default function Settings() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Version</p>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">1.0.0</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Environment</p>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">Production</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Solver</p>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">OR-Tools 9.9</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">AI Model</p>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">Kimi K2.5</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About RouteMind</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-primary mt-0.5" />
            <div className="text-sm text-slate-600 dark:text-slate-400">
              <p>RouteMind is an AI-powered route optimization platform for Indian logistics.</p>
              <p className="mt-2">Built for AI Build 2026 hackathon by Team route-club (T080).</p>
              <p className="mt-4 text-xs text-slate-500">
                Powered by Google OR-Tools and AWS Bedrock
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
