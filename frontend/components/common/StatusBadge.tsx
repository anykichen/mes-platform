import { cn } from '@/lib/utils'
import { STATUS_CONFIG, TASK_STATUS_CONFIG } from '@/lib/constants'

export function StatusBadge({ status }: { status: 'normal' | 'warning' | 'error' }) {
  const cfg = STATUS_CONFIG[status]
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium', cfg.bg, cfg.color)}>
      {cfg.label}
    </span>
  )
}

export function TaskStatusBadge({ status }: { status: string }) {
  const cfg = TASK_STATUS_CONFIG[status as keyof typeof TASK_STATUS_CONFIG] ?? { label: status, color: 'text-gray-600', bg: 'bg-gray-50' }
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium', cfg.bg, cfg.color)}>
      {cfg.label}
    </span>
  )
}
