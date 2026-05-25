import { YIELD_THRESHOLDS } from './constants'

export function yieldStatus(pct: number): 'normal' | 'warning' | 'error' {
  if (pct >= YIELD_THRESHOLDS.good) return 'normal'
  if (pct >= YIELD_THRESHOLDS.warn) return 'warning'
  return 'error'
}

export function fmtNumber(n: number): string {
  return n.toLocaleString('zh-CN')
}

export function fmtPct(n: number): string {
  return `${n.toFixed(1)}%`
}

export function fmtDatetime(iso: string | null): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit',  minute: '2-digit',
  })
}

export function cn(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}
