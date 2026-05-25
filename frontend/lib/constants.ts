export const SHIFTS = [
  { value: 'summary', label: '汇总' },
  { value: 'day',     label: '白班' },
  { value: 'night',   label: '夜班' },
]

export const STATUS_CONFIG = {
  normal:  { label: '正常', color: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-200' },
  warning: { label: '注意', color: 'text-amber-600',  bg: 'bg-amber-50',  border: 'border-amber-200' },
  error:   { label: '异常', color: 'text-red-600',    bg: 'bg-red-50',    border: 'border-red-200'   },
} as const

export const TASK_STATUS_CONFIG = {
  SUCCESS: { label: '成功', color: 'text-green-600', bg: 'bg-green-50' },
  ERROR:   { label: '失败', color: 'text-red-600',   bg: 'bg-red-50'   },
  WARN:    { label: '警告', color: 'text-amber-600', bg: 'bg-amber-50' },
  RUNNING: { label: '运行中', color: 'text-blue-600', bg: 'bg-blue-50' },
} as const

export const CHART_COLORS = ['#185fa5', '#16a34a', '#d97706', '#7c3aed', '#db2777']

// 良率阈值
export const YIELD_THRESHOLDS = { good: 98, warn: 95 }
