'use client'
import useSWR, { mutate } from 'swr'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { Toggle } from '@/components/common/Toggle'
import { TaskStatusBadge } from '@/components/common/StatusBadge'
import { TaskLog, SchedulerJob } from '@/types'
import { fmtDatetime } from '@/lib/utils'
import { format } from 'date-fns'
import { Play } from 'lucide-react'

const TODAY = format(new Date(), 'yyyy-MM-dd')

export default function SchedulePage() {
  const { data: jobs }   = useSWR('jobs',  api.tasks.jobs,  { refreshInterval: 30000 })
  const { data: logs }   = useSWR('logs',  () => api.tasks.logs(30), { refreshInterval: 15000 })

  const jobList = (jobs as SchedulerJob[]) ?? []
  const logList = (logs as TaskLog[]) ?? []

  async function triggerManual(shift: string) {
    await api.tasks.trigger(shift, TODAY)
    setTimeout(() => mutate('logs'), 2000)
  }

  async function toggleJob(job: SchedulerJob) {
    if (job.enabled) {
      await api.tasks.pause(job.id)
    } else {
      await api.tasks.resume(job.id)
    }
    mutate('jobs')
  }

  return (
    <div>
      <Topbar title="定时任务" />
      <div className="p-6 space-y-4">
        {/* 手动触发 */}
        <div className="card">
          <div className="text-sm font-medium text-gray-700 mb-3">手动触发采集</div>
          <div className="flex gap-2">
            {['summary', 'day', 'night'].map(s => (
              <button key={s} onClick={() => triggerManual(s)} className="btn-primary">
                <Play size={12} />
                {s === 'summary' ? '汇总' : s === 'day' ? '白班' : '夜班'} 采集
              </button>
            ))}
          </div>
        </div>

        {/* 定时任务列表 */}
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 text-sm font-medium text-gray-700">定时任务配置</div>
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">任务名</th><th>说明</th>
                <th>下次执行</th><th>状态</th><th>启用</th>
              </tr>
            </thead>
            <tbody>
              {jobList.map(job => (
                <tr key={job.id}>
                  <td className="pl-4 font-medium">{job.name}</td>
                  <td className="text-gray-400 text-xs">{job.id}</td>
                  <td className="text-xs text-gray-600">{fmtDatetime(job.next_run_time)}</td>
                  <td><TaskStatusBadge status={job.enabled ? 'SUCCESS' : 'WARN'} /></td>
                  <td><Toggle checked={job.enabled} onChange={() => toggleJob(job)} /></td>
                </tr>
              ))}
              {jobList.length === 0 && (
                <tr><td colSpan={5} className="text-center py-8 text-sm text-gray-400">调度器未启动</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* 执行日志 */}
        <div className="card">
          <div className="text-sm font-medium text-gray-700 mb-3">执行日志 <span className="text-xs text-gray-400 font-normal">最近 30 条</span></div>
          <div className="font-mono text-xs space-y-1 text-gray-600 max-h-64 overflow-y-auto">
            {logList.map(log => (
              <div key={log.id} className="flex gap-2">
                <span className={
                  log.status === 'SUCCESS' ? 'text-green-600' :
                  log.status === 'ERROR'   ? 'text-red-500'   :
                  log.status === 'WARN'    ? 'text-amber-600' : 'text-blue-500'
                }>
                  [{log.status}]
                </span>
                <span className="text-gray-400">{fmtDatetime(log.started_at)}</span>
                <span className="flex-1 truncate">{log.message ?? log.task_name}</span>
                {log.duration_sec && <span className="text-gray-400">{log.duration_sec}s</span>}
              </div>
            ))}
            {logList.length === 0 && <div className="text-gray-400 py-4 text-center">暂无日志</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
