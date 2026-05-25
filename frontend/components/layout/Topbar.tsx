'use client'
import { RefreshCw, Loader2 } from 'lucide-react'

interface TopbarProps {
  title: string
  meta?: string
  projects?: string[]
  activeProject?: string
  onProjectChange?: (p: string) => void
  onRefresh?: () => void
  collecting?: boolean
  collectProgress?: string
  collectResult?: string
}

export function Topbar({ title, meta, projects, activeProject, onProjectChange, onRefresh, collecting, collectProgress, collectResult }: TopbarProps) {
  return (
    <div className="sticky top-0 z-10 flex items-center justify-between px-6 h-[52px] bg-white border-b border-gray-100">
      <div>
        <h1 className="text-sm font-semibold text-gray-900">{title}</h1>
        {meta && <p className="text-xs text-gray-400">{meta}</p>}
      </div>
      <div className="flex items-center gap-3">
        {/* 采集进度提示 */}
        {(collecting || collectResult) && (
          <div className="flex items-center gap-2 text-xs">
            {collecting && <Loader2 size={14} className="animate-spin text-blue-500" />}
            <span className={collectResult?.includes('失败') ? 'text-red-500' : 'text-gray-600'}>
              {collectProgress || collectResult}
            </span>
          </div>
        )}
        {/* 专案下拉选择 */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500">专案:</label>
          <select
            value={activeProject || ''}
            onChange={(e) => onProjectChange?.(e.target.value)}
            className="px-3 py-1.5 text-xs border border-gray-200 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">请选择专案</option>
            {projects?.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
        <button 
          className="btn-secondary" 
          onClick={onRefresh}
          disabled={collecting}
        >
          {collecting ? <Loader2 size={13} className="animate-spin" /> : <RefreshCw size={13} />}
          {collecting ? '采集中...' : '立即采集'}
        </button>
      </div>
    </div>
  )
}
