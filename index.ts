// ── 专案 & 重点站点 ──────────────────────────────────────
export interface Project {
  id: number
  project_name: string
  enabled: boolean
  display_order: number
  show_in_dashboard: boolean
  enable_trend: boolean
  created_at: string
  updated_at: string
  key_stations: KeyStation[]
}

export interface KeyStation {
  id: number
  project_name: string
  station_name: string
  enabled: boolean
  display_order: number
  show_ng: boolean
  show_yield: boolean
  show_trend: boolean
  created_at: string
}

// ── Dashboard ────────────────────────────────────────────
export interface DashboardKpi {
  total_input: number
  total_output: number
  total_ng: number
  yield_rate: number
  yield_rate_pct: number
}

export interface StationCard {
  station_name: string
  input_qty: number
  ng_qty: number
  yield_rate_pct: number
  status: 'normal' | 'warning' | 'error'
  show_ng: boolean
  show_yield: boolean
  show_trend: boolean
}

export interface NgRankItem {
  station_name: string
  ng_qty: number
  input_qty: number
  yield_rate_pct: number
}

export interface TrendPoint {
  date: string
  yield_rate_pct: number
  ng_qty: number
}

export interface OutputTrendData {
  [project: string]: { date: string; output: number }[]
}

// ── 站点数据 ─────────────────────────────────────────────
export interface StationSummary {
  id: number
  report_date: string
  shift: string
  project: string
  station_name: string
  input_qty: number
  output_qty: number
  ng_qty: number
  yield_rate: number
  material_yield: number
  process_yield: number
}

// ── 账号 ─────────────────────────────────────────────────
export interface MesAccount {
  id: number
  username: string
  last_login_at: string | null
  last_login_ok: boolean | null
  updated_at: string
}

export interface LoginTestResult {
  success: boolean
  message: string
  tested_at: string
}

// ── 任务 ─────────────────────────────────────────────────
export interface TaskLog {
  id: number
  task_name: string
  project: string | null
  shift: string | null
  status: 'SUCCESS' | 'ERROR' | 'WARN' | 'RUNNING'
  message: string | null
  success_count: number
  failed_count: number
  error_message: string | null
  duration_sec: number | null
  started_at: string
  finished_at: string | null
}

export interface SchedulerJob {
  id: string
  name: string
  next_run_time: string | null
  enabled: boolean
}

// ── 系统状态 ─────────────────────────────────────────────
export interface SystemStatus {
  db_online: boolean
  mes_last_login_ok: boolean | null
  mes_last_login_at: string | null
  last_collect_status: string | null
  last_collect_at: string | null
}

// ── 通用 ─────────────────────────────────────────────────
export type Shift = 'summary' | 'day' | 'night'
