'use client'
import { useState } from 'react'
import useSWR, { mutate } from 'swr'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { Toggle } from '@/components/common/Toggle'
import { Project } from '@/types'
import { Plus, Trash2, Star } from 'lucide-react'
import Link from 'next/link'

export default function ProjectsPage() {
  const { data, isLoading } = useSWR('projects', api.projects.list)
  const projects = (data as Project[]) ?? []

  async function toggleEnabled(p: Project) {
    await api.projects.update(p.project_name, { enabled: !p.enabled })
    mutate('projects')
  }

  async function deleteProject(name: string) {
    if (!confirm(`确认删除专案 "${name}"？此操作不可撤销。`)) return
    await api.projects.delete(name)
    mutate('projects')
  }

  return (
    <div>
      <Topbar title="专案管理" />
      <div className="p-6">
        <div className="card p-0 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-medium text-gray-700">专案列表</span>
            <button className="btn-primary"><Plus size={13} />新增专案</button>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">序号</th>
                <th>专案名称</th>
                <th>启用</th>
                <th>查询顺序</th>
                <th>趋势分析</th>
                <th>Dashboard 显示</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={7} className="text-center py-8 text-sm text-gray-400">加载中...</td></tr>
              )}
              {projects.map((p, i) => (
                <tr key={p.id}>
                  <td className="pl-4 text-gray-400">{i + 1}</td>
                  <td className="font-medium">{p.project_name}</td>
                  <td><Toggle checked={p.enabled} onChange={() => toggleEnabled(p)} /></td>
                  <td>
                    <input
                      type="number" defaultValue={p.display_order}
                      className="input w-16 text-center text-xs"
                      onBlur={e => api.projects.update(p.project_name, { display_order: +e.target.value })}
                    />
                  </td>
                  <td><Toggle checked={p.enable_trend} onChange={v => api.projects.update(p.project_name, { enable_trend: v }).then(() => mutate('projects'))} /></td>
                  <td><Toggle checked={p.show_in_dashboard} onChange={v => api.projects.update(p.project_name, { show_in_dashboard: v }).then(() => mutate('projects'))} /></td>
                  <td>
                    <div className="flex items-center gap-2">
                      <Link href={`/keystations?project=${p.project_name}`} className="btn-secondary text-xs">
                        <Star size={12} />重点站点
                      </Link>
                      <button onClick={() => deleteProject(p.project_name)} className="btn-danger">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
