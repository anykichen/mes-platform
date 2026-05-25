'use client'
import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { format } from 'date-fns'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { ShiftTabs } from '@/components/common/ShiftTabs'
import { StatusBadge } from '@/components/common/StatusBadge'
import { fmtNumber, fmtPct, yieldStatus, cn } from '@/lib/utils'
import { YIELD_THRESHOLDS } from '@/lib/constants'

const TODAY = format(new Date(), 'yyyy-MM-dd')

export default function StationsPage() {
  const [project, setProject] = useState('')
  const [shift, setShift] = useState('summary')
  const [date, setDate] = useState(TODAY)
  
  // 获取专案列表
  const { data: projectsData } = useSWR('projects', api.projects.list)
  const projects = (projectsData as any[])?.map((p: any) => p.project_name) ?? []
  
  // 默认选择第一个专案
  useEffect(() => {
    if (projects.length > 0 && !project) {
      setProject(projects[0])
    }
  }, [projects, project])

  const { data, isLoading } = useSWR(
    ['stations', project, date, shift],
    () => project ? api.stations.list(project, date, shift) : null
  )

  const stations = (data as any[]) ?? []

  return (
    <div>
      <Topbar
        title="站点分析"
        meta={`${date} · ${project}`}
        projects={projects}
        activeProject={project}
        onProjectChange={setProject}
      />
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <ShiftTabs value={shift} onChange={setShift} />
          <input
            type="date" value={date}
            onChange={e => setDate(e.target.value)}
            className="input text-xs"
          />
          <span className="text-xs text-gray-400">{stations.length} 个工站</span>
        </div>

        <div className="card p-0 overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">工站</th>
                <th>投入</th><th>产出</th><th>NG</th>
                <th>良率</th><th>物料良率</th><th>工程良率</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={8} className="text-center py-10 text-sm text-gray-400">加载中...</td></tr>
              )}
              {!isLoading && stations.length === 0 && (
                <tr><td colSpan={8} className="text-center py-10 text-sm text-gray-400">暂无数据</td></tr>
              )}
              {stations.map((s: any) => {
                const status = yieldStatus(Number(s.yield_rate) * 100)
                const pct = Number(s.yield_rate) * 100
                const barColor = pct >= YIELD_THRESHOLDS.good ? 'bg-green-500'
                               : pct >= YIELD_THRESHOLDS.warn  ? 'bg-amber-400' : 'bg-red-500'
                return (
                  <tr key={`${s.station_name}-${s.shift}`}>
                    <td className="pl-4 font-medium">{s.station_name}</td>
                    <td>{fmtNumber(s.input_qty)}</td>
                    <td>{fmtNumber(s.output_qty)}</td>
                    <td className="text-red-500">{fmtNumber(s.ng_qty)}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <span className="text-xs w-11">{fmtPct(pct)}</span>
                        <div className="yield-bar w-20">
                          <div className={cn('h-full rounded-full', barColor)} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    </td>
                    <td>{fmtPct(Number(s.material_yield) * 100)}</td>
                    <td>{fmtPct(Number(s.process_yield) * 100)}</td>
                    <td><StatusBadge status={status} /></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
