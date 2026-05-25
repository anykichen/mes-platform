'use client'
import { useState, useEffect } from 'react'
import useSWR, { mutate } from 'swr'
import { format } from 'date-fns'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { KpiCard } from '@/components/common/KpiCard'
import { ShiftTabs } from '@/components/common/ShiftTabs'
import { AlertStrip } from '@/components/common/AlertStrip'
import { StationCard } from '@/components/common/StationCard'
import { NgRankChart } from '@/components/charts/NgRankChart'
import { YieldTrendChart } from '@/components/charts/YieldTrendChart'
import { OutputTrendChart } from '@/components/charts/OutputTrendChart'
import { fmtNumber, fmtPct } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

const TODAY = format(new Date(), 'yyyy-MM-dd')

export default function DashboardPage() {
  const [project, setProject] = useState('')
  const [shift, setShift]     = useState('summary')
  const [collecting, setCollecting] = useState(false)
  const [collectProgress, setCollectProgress] = useState<string>('')
  const [collectResult, setCollectResult] = useState<string>('')
  
  // 获取专案列表
  const { data: projectsData } = useSWR('projects', api.projects.list)
  const projects = (projectsData as any[])?.map((p: any) => p.project_name) ?? []
  
  // 默认选择第一个专案
  useEffect(() => {
    if (projects.length > 0 && !project) {
      setProject(projects[0])
    }
  }, [projects, project])

  // 立即采集
  const handleRefresh = async () => {
    setCollecting(true)
    setCollectProgress('正在触发采集任务...')
    setCollectResult('')
    
    try {
      await api.tasks.trigger(shift, TODAY)
      setCollectProgress('采集任务已提交，正在处理...')
      
      // 轮询采集状态
      const checkStatus = async () => {
        const logs = await api.tasks.logs(1)
        const latest = logs[0]
        if (latest) {
          setCollectProgress(`状态: ${latest.status}...`)
          if (latest.status === 'SUCCESS' || latest.status === 'WARN' || latest.status === 'ERROR') {
            setCollecting(false)
            if (latest.status === 'SUCCESS' || latest.status === 'WARN') {
              setCollectResult(`采集完成: ${latest.success_count} 成功, ${latest.failed_count} 失败`)
            } else {
              setCollectResult(`采集失败: ${latest.error_message || latest.message || '未知错误'}`)
            }
            // 刷新数据
            mutate('projects')
            mutate(['kpi', project, shift])
            mutate(['ks', project, shift])
            mutate(['ng', project, shift])
            mutate(['trend', project])
            mutate('output')
            return
          } else if (latest.status === 'RUNNING') {
            // 继续轮询
          }
        }
        setTimeout(checkStatus, 3000)
      }
      setTimeout(checkStatus, 2000)
    } catch (error) {
      setCollecting(false)
      setCollectResult(`采集失败: ${error}`)
    }
  }

  const { data: kpi }      = useSWR(['kpi', project, shift], () => project ? api.dashboard.kpi(project, TODAY, shift) : null, { refreshInterval: 60000 })
  const { data: stations } = useSWR(['ks', project, shift], () => project ? api.dashboard.keyStations(project, TODAY, shift) : null, { refreshInterval: 60000 })
  const { data: ngRank }   = useSWR(['ng', project, shift], () => project ? api.dashboard.ngRank(project, TODAY, shift) : null)
  const { data: trend }    = useSWR(['trend', project], () => project ? api.dashboard.yieldTrend(project, 'OQC', 7) : null)
  const { data: outputRaw }= useSWR('output', () => projects.length >= 2 ? api.dashboard.outputTrend(projects.slice(0, 2).join(','), 7) : null)

  // 异常站点告警
  const alertStations = (stations as any[])?.filter((s: any) => s.status === 'error') ?? []

  // 将 outputRaw 转为图表格式
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

  return (
    <div>
      <Topbar
        title="总览 Dashboard"
        meta={`${TODAY} · Auto_THA`}
        projects={projects}
        activeProject={project}
        onProjectChange={setProject}
        onRefresh={handleRefresh}
        collecting={collecting}
        collectProgress={collectProgress}
        collectResult={collectResult}
      />
      <div className="p-6">
        {alertStations.length > 0 && (
          <AlertStrip
            message={`${alertStations.map((s: any) => s.station_name).join('、')} 良率异常，请关注`}
          />
        )}

        {/* KPI 行 */}
        <div className="grid grid-cols-4 gap-3 mb-5">
          <KpiCard label="今日投入"   value={fmtNumber((kpi as any)?.total_input  ?? 0)} delta="↑ 12% vs 昨日" deltaType="up" />
          <KpiCard label="今日产出"   value={fmtNumber((kpi as any)?.total_output ?? 0)} delta="↑ 9% vs 昨日"  deltaType="up" />
          <KpiCard label="综合良率"   value={fmtPct((kpi as any)?.yield_rate_pct ?? 0)}  highlight="green" delta="↓ 0.4% vs 昨日" deltaType="down" />
          <KpiCard label="今日 NG 数" value={fmtNumber((kpi as any)?.total_ng   ?? 0)}  highlight="red" />
        </div>

        <ShiftTabs value={shift} onChange={setShift} />
        <div className="h-4" />

        {/* 重点站点 + NG 排行 */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">
              重点站点 <span className="text-xs text-gray-400 font-normal ml-1">{project} · 今日</span>
            </div>
            <div className="flex text-[11px] text-gray-400 px-0 pb-1 border-b border-gray-100 gap-3">
              <span className="w-28">站点</span>
              <span className="flex-1 pl-12">良率</span>
              <span className="w-12 text-right">NG</span>
              <span className="w-12 text-right">状态</span>
            </div>
            {(stations as any[])?.map((s: any) => <StationCard key={s.station_name} card={s} />) ?? (
              <div className="py-8 text-center text-sm text-gray-400">暂无数据</div>
            )}
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">
              NG 排行 <span className="text-xs text-gray-400 font-normal ml-1">重点站点 · 今日</span>
            </div>
            {ngRank ? <NgRankChart data={ngRank as any} /> : (
              <div className="py-8 text-center text-sm text-gray-400">暂无数据</div>
            )}
          </div>
        </div>

        {/* 趋势图 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">
              OQC 良率趋势 <span className="text-xs text-gray-400 font-normal ml-1">近 7 天</span>
            </div>
            <YieldTrendChart data={(trend as any) ?? []} stationName="OQC" />
          </div>
          <div className="card">
            <div className="text-sm font-medium text-gray-700 mb-3">
              专案产出趋势 <span className="text-xs text-gray-400 font-normal ml-1">近 7 天</span>
            </div>
            <OutputTrendChart data={outputData} projects={projects.slice(0, 2)} />
          </div>
        </div>
      </div>
    </div>
  )
}
