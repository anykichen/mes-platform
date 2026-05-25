'use client'
import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { YieldTrendChart } from '@/components/charts/YieldTrendChart'
import { NgStackChart } from '@/components/charts/NgStackChart'
import { OutputTrendChart } from '@/components/charts/OutputTrendChart'

const KEY_STATIONS = ['OQC', 'Gap Check', 'CGM_VI', 'Housing_VI']

export default function TrendPage() {
  const [project, setProject] = useState('')
  const [days, setDays] = useState(7)
  
  // 获取专案列表
  const { data: projectsData } = useSWR('projects', api.projects.list)
  const projects = (projectsData as any[])?.map((p: any) => p.project_name) ?? []
  
  // 默认选择第一个专案
  useEffect(() => {
    if (projects.length > 0 && !project) {
      setProject(projects[0])
    }
  }, [projects, project])

  const trends = KEY_STATIONS.map(s => ({
    station: s,
    result: useSWR(['trend', project, s, days], () => project ? api.dashboard.yieldTrend(project, s, days) : null),
  }))

  const { data: outputRaw } = useSWR('output', () => projects.length >= 2 ? api.dashboard.outputTrend(projects.slice(0, 2).join(','), days) : null)

  const outputData: any[] = []
  if (outputRaw) {
    const allDates = new Set<string>()
    Object.values(outputRaw as any).forEach((arr: any) => arr.forEach((p: any) => allDates.add(p.date)))
    Array.from(allDates).sort().forEach(d => {
      const row: any = { date: d.slice(5) }
      Object.entries(outputRaw as any).forEach(([proj, arr]: any) => {
        const found = arr.find((p: any) => p.date === d)
        row[proj] = found?.output ?? 0
      })
      outputData.push(row)
    })
  }

  const ngStackData: any[] = []
  const dates = (trends[0]?.result.data as any[])?.map((p: any) => p.date.slice(5)) ?? []
  dates.forEach((d, i) => {
    const row: any = { date: d }
    trends.forEach(({ station, result }) => {
      row[station] = (result.data as any[])?.[i]?.ng_qty ?? 0
    })
    ngStackData.push(row)
  })

  return (
    <div>
      <Topbar
        title="趋势报表"
        projects={projects}
        activeProject={project}
        onProjectChange={setProject}
      />
      <div className="p-6">
        <div className="flex items-center gap-2 mb-5">
          {[7, 14, 30].map(d => (
            <button key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 rounded-lg text-xs border transition-colors ${
                days === d ? 'bg-blue-50 text-blue-700 border-blue-200' : 'text-gray-500 border-gray-200 hover:bg-gray-50'
              }`}
            >近 {d} 天</button>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {trends.slice(0, 2).map(({ station, result }) => (
            <div key={station} className="card">
              <div className="text-sm font-medium text-gray-700 mb-3">
                {station} 良率趋势
              </div>
              <YieldTrendChart data={(result.data as any) ?? []} stationName={station} />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          {trends.slice(2, 4).map(({ station, result }) => (
            <div key={station} className="card">
              <div className="text-sm font-medium text-gray-700 mb-3">
                {station} 良率趋势
              </div>
              <YieldTrendChart data={(result.data as any) ?? []} stationName={station} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">NG 数量趋势（叠加）</div>
            <NgStackChart data={ngStackData} stations={KEY_STATIONS} />
          </div>
          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">专案产出趋势</div>
            <OutputTrendChart data={outputData} projects={projects.slice(0, 2)} />
          </div>
        </div>
      </div>
    </div>
  )
}
