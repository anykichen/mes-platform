const BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1`
  : '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`API ${path} failed: ${err}`)
  }
  return res.json()
}

// ── Dashboard ────────────────────────────────────────────
export const api = {
  dashboard: {
    kpi:          (project: string, date: string, shift: string) =>
      request(`/dashboard/kpi?project=${project}&report_date=${date}&shift=${shift}`),
    keyStations:  (project: string, date: string, shift: string) =>
      request(`/dashboard/key-stations?project=${project}&report_date=${date}&shift=${shift}`),
    ngRank:       (project: string, date: string, shift: string) =>
      request(`/dashboard/ng-rank?project=${project}&report_date=${date}&shift=${shift}`),
    yieldTrend:   (project: string, station: string, days = 7, shift = 'summary') =>
      request(`/dashboard/yield-trend?project=${project}&station=${station}&days=${days}&shift=${shift}`),
    outputTrend:  (projects: string, days = 7) =>
      request(`/dashboard/output-trend?projects=${projects}&days=${days}`),
    systemStatus: () => request('/dashboard/system-status'),
  },

  // ── 专案 ────────────────────────────────────────────────
  projects: {
    list:           () => request('/projects/'),
    create:         (data: object) => request('/projects/', { method: 'POST', body: JSON.stringify(data) }),
    update:         (name: string, data: object) => request(`/projects/${name}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete:         (name: string) => request(`/projects/${name}`, { method: 'DELETE' }),
    keyStations:    (name: string) => request(`/projects/${name}/key-stations`),
    createKS:       (name: string, data: object) => request(`/projects/${name}/key-stations`, { method: 'POST', body: JSON.stringify(data) }),
    updateKS:       (name: string, id: number, data: object) => request(`/projects/${name}/key-stations/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    deleteKS:       (name: string, id: number) => request(`/projects/${name}/key-stations/${id}`, { method: 'DELETE' }),
  },

  // ── 站点数据 ─────────────────────────────────────────────
  stations: {
    list:           (project: string, date: string, shift: string) =>
      request(`/stations/?project=${project}&report_date=${date}&shift=${shift}`),
    dates:          (project: string) => request(`/stations/dates?project=${project}`),
  },

  // ── 账号 ─────────────────────────────────────────────────
  account: {
    get:            () => request('/account/'),
    update:         (data: object) => request('/account/', { method: 'PUT', body: JSON.stringify(data) }),
    testLogin:      () => request('/account/test-login', { method: 'POST' }),
  },

  // ── 任务 ─────────────────────────────────────────────────
  tasks: {
    trigger:        (shift: string, date: string) => request(`/tasks/trigger?shift=${shift}&report_date=${date}`, { method: 'POST' }),
    logs:           (limit = 20) => request(`/tasks/logs?limit=${limit}`),
    jobs:           () => request('/tasks/jobs'),
    pause:          (id: string) => request(`/tasks/jobs/${id}/pause`, { method: 'POST' }),
    resume:         (id: string) => request(`/tasks/jobs/${id}/resume`, { method: 'POST' }),
  },
}
