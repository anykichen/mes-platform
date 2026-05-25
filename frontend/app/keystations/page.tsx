'use client'
import { useState, useEffect } from 'react'
import useSWR, { mutate } from 'swr'
import { useSearchParams } from 'next/navigation'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { Toggle } from '@/components/common/Toggle'
import { KeyStation } from '@/types'
import { Plus, Trash2 } from 'lucide-react'

export default function KeyStationsPage() {
  const params = useSearchParams()
  const [project, setProject] = useState('')
  const [newStation, setNewStation] = useState('')
  const [adding, setAdding] = useState(false)
  
  // 获取专案列表
  const { data: projectsData } = useSWR('projects', api.projects.list)
  const projects = (projectsData as any[])?.map((p: any) => p.project_name) ?? []
  
  // 默认选择第一个专案或URL参数中的专案
  useEffect(() => {
    const paramProject = params.get('project')
    if (paramProject && projects.includes(paramProject)) {
      setProject(paramProject)
    } else if (projects.length > 0 && !project) {
      setProject(projects[0])
    }
  }, [projects, project, params])

  const key = `keystations-${project}`
  const { data } = useSWR(key, () => project ? api.projects.keyStations(project) : null)
  const stations = (data as KeyStation[]) ?? []

  async function addStation() {
    if (!newStation.trim()) return
    await api.projects.createKS(project, { station_name: newStation.trim() })
    setNewStation('')
    setAdding(false)
    mutate(key)
  }

  async function updateKS(ks: KeyStation, field: keyof KeyStation, value: any) {
    await api.projects.updateKS(project, ks.id, { [field]: value })
    mutate(key)
  }

  async function deleteKS(id: number) {
    if (!confirm('确认删除此重点站点？')) return
    await api.projects.deleteKS(project, id)
    mutate(key)
  }

  return (
    <div>
      <Topbar
        title="重点站点配置"
        projects={projects}
        activeProject={project}
        onProjectChange={setProject}
      />
      <div className="p-6">
        <div className="card p-0 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-medium text-gray-700">{project} · 重点站点</span>
            <button className="btn-primary" onClick={() => setAdding(true)}><Plus size={13} />添加站点</button>
          </div>

          {adding && (
            <div className="flex items-center gap-2 px-4 py-3 bg-blue-50 border-b border-blue-100">
              <input
                autoFocus
                value={newStation}
                onChange={e => setNewStation(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addStation()}
                placeholder="输入站点名称，如 OQC"
                className="input flex-1 text-sm"
              />
              <button className="btn-primary" onClick={addStation}>确认添加</button>
              <button className="btn-secondary" onClick={() => setAdding(false)}>取消</button>
            </div>
          )}

          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">排序</th>
                <th>站点名称</th>
                <th>显示趋势</th>
                <th>显示 NG</th>
                <th>显示良率</th>
                <th>启用</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {stations.map((ks, i) => (
                <tr key={ks.id}>
                  <td className="pl-4">
                    <span className="text-gray-300 mr-2 cursor-grab">⠿</span>
                    <span className="text-gray-400 text-xs">{i + 1}</span>
                  </td>
                  <td className="font-medium">{ks.station_name}</td>
                  <td><Toggle checked={ks.show_trend} onChange={v => updateKS(ks, 'show_trend', v)} /></td>
                  <td><Toggle checked={ks.show_ng}    onChange={v => updateKS(ks, 'show_ng',    v)} /></td>
                  <td><Toggle checked={ks.show_yield} onChange={v => updateKS(ks, 'show_yield', v)} /></td>
                  <td><Toggle checked={ks.enabled}    onChange={v => updateKS(ks, 'enabled',    v)} /></td>
                  <td>
                    <button onClick={() => deleteKS(ks.id)} className="btn-danger">
                      <Trash2 size={12} />
                    </button>
                  </td>
                </tr>
              ))}
              {stations.length === 0 && (
                <tr><td colSpan={7} className="text-center py-8 text-sm text-gray-400">尚未配置重点站点</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
