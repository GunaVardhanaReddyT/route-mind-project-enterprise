import { useState, useEffect } from 'react'
import { DollarSign, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface CostAnalysis {
  routes_computed: number
  cost_per_route_usd: {
    routemind_hybrid: number
    pure_llm_gpt4: number
    manual_planning: number
  }
  total_cost_usd: {
    routemind: number
    pure_llm: number
    manual: number
  }
  savings_usd: {
    vs_pure_llm: number
    vs_manual: number
  }
  why_efficient: string
}

export default function Metrics() {
  const [costData, setCostData] = useState<CostAnalysis | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCostAnalysis()
  }, [])

  const loadCostAnalysis = async () => {
    try {
      const res = await fetch('/api/v1/cost-analysis')
      const data = await res.json()
      setCostData(data)
    } catch (err) {
      console.error('Failed to load cost analysis:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading cost analysis...</div>
  }

  if (!costData) {
    return <div className="text-center py-12 text-red-600">Failed to load cost data</div>
  }

  const chartData = [
    {
      name: 'RouteMind',
      cost: costData.cost_per_route_usd.routemind_hybrid,
      fill: '#10b981'
    },
    {
      name: 'Pure LLM',
      cost: costData.cost_per_route_usd.pure_llm_gpt4,
      fill: '#ef4444'
    },
    {
      name: 'Manual',
      cost: costData.cost_per_route_usd.manual_planning,
      fill: '#f59e0b'
    }
  ]

  const savingsPercentLLM = ((costData.savings_usd.vs_pure_llm / costData.total_cost_usd.pure_llm) * 100).toFixed(1)
  const savingsPercentManual = ((costData.savings_usd.vs_manual / costData.total_cost_usd.manual) * 100).toFixed(1)

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Routes Computed</h3>
            <TrendingUp className="h-6 w-6 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{costData.routes_computed}</p>
          <p className="text-sm text-gray-600 mt-2">Total optimizations</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Cost Per Route</h3>
            <DollarSign className="h-6 w-6 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600">
            ${costData.cost_per_route_usd.routemind_hybrid.toFixed(4)}
          </p>
          <p className="text-sm text-gray-600 mt-2">RouteMind hybrid approach</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Total Savings</h3>
            <TrendingDown className="h-6 w-6 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-purple-600">
            ${costData.savings_usd.vs_pure_llm.toFixed(2)}
          </p>
          <p className="text-sm text-gray-600 mt-2">vs Pure LLM approach</p>
        </div>
      </div>

      {/* Cost Comparison Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Cost Per Route Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Cost (USD)', angle: -90, position: 'insideLeft' }} />
            <Tooltip formatter={(value: any) => value ? `$${Number(value).toFixed(4)}` : '$0'} />
            <Bar dataKey="cost" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Comparison */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Detailed Cost Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Approach
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Cost/Route
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Total Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Savings
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr className="bg-green-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-green-500 rounded-full mr-2" />
                    <span className="font-medium text-gray-900">RouteMind (Hybrid)</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.cost_per_route_usd.routemind_hybrid.toFixed(4)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.total_cost_usd.routemind.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                  Baseline
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-red-500 rounded-full mr-2" />
                    <span className="font-medium text-gray-900">Pure LLM (GPT-4)</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.cost_per_route_usd.pure_llm_gpt4.toFixed(4)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.total_cost_usd.pure_llm.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                  -${costData.savings_usd.vs_pure_llm.toFixed(2)} ({savingsPercentLLM}% more)
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-yellow-500 rounded-full mr-2" />
                    <span className="font-medium text-gray-900">Manual Planning</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.cost_per_route_usd.manual_planning.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${costData.total_cost_usd.manual.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                  -${costData.savings_usd.vs_manual.toFixed(2)} ({savingsPercentManual}% more)
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Why Efficient */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
        <div className="flex items-start">
          <AlertCircle className="h-6 w-6 text-blue-600 mt-0.5 mr-3" />
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-2">Why RouteMind is Cost-Efficient</h4>
            <p className="text-sm text-blue-800">{costData.why_efficient}</p>
          </div>
        </div>
      </div>

      {/* Projections */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Cost Projections (10,000 routes)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">RouteMind</p>
            <p className="text-2xl font-bold text-green-600">
              ${(costData.cost_per_route_usd.routemind_hybrid * 10000).toFixed(0)}/mo
            </p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Pure LLM</p>
            <p className="text-2xl font-bold text-red-600">
              ${(costData.cost_per_route_usd.pure_llm_gpt4 * 10000).toFixed(0)}/mo
            </p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Manual</p>
            <p className="text-2xl font-bold text-yellow-600">
              ${(costData.cost_per_route_usd.manual_planning * 10000).toFixed(0)}/mo
            </p>
          </div>
        </div>
        <p className="text-sm text-gray-600 text-center mt-4">
          RouteMind saves <span className="font-bold text-green-600">
            ${((costData.cost_per_route_usd.pure_llm_gpt4 - costData.cost_per_route_usd.routemind_hybrid) * 10000).toFixed(0)}
          </span> per month vs Pure LLM
        </p>
      </div>
    </div>
  )
}
