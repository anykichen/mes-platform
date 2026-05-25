import { cn } from '@/lib/utils'

interface KpiCardProps {
  label: string
  value: string | number
  delta?: string
  deltaType?: 'up' | 'down' | 'neutral'
  highlight?: 'green' | 'blue' | 'red'
}

export function KpiCard({ label, value, delta, deltaType = 'neutral', highlight }: KpiCardProps) {
  return (
    <div className="card">
      <div className="text-[11px] font-medium text-gray-400 uppercase tracking-wide mb-1.5">{label}</div>
      <div className={cn(
        'text-2xl font-semibold leading-none',
        highlight === 'green' && 'text-green-600',
        highlight === 'blue'  && 'text-blue-600',
        highlight === 'red'   && 'text-red-600',
        !highlight            && 'text-gray-900',
      )}>
        {value}
      </div>
      {delta && (
        <div className={cn(
          'text-xs mt-1.5',
          deltaType === 'up'   && 'text-green-600',
          deltaType === 'down' && 'text-red-500',
          deltaType === 'neutral' && 'text-gray-400',
        )}>
          {delta}
        </div>
      )}
    </div>
  )
}
