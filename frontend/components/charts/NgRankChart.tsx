'use client'
import { NgRankItem } from '@/types'
import { fmtNumber, fmtPct } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface Props { data: NgRankItem[] }

export function NgRankChart({ data }: Props) {
  const max = data[0]?.ng_qty || 1
  return (
    <div className="space-y-2">
      {data.map((item, i) => (
        <div key={item.station_name} className="flex items-center gap-2">
          <span className={cn(
            'w-5 h-5 rounded-full text-[10px] font-semibold flex items-center justify-center shrink-0',
            i === 0 ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-500'
          )}>
            {i + 1}
          </span>
          <span className="text-xs text-gray-700 w-24 truncate">{item.station_name}</span>
          <div className="flex-1 bg-gray-100 rounded-full h-1.5 overflow-hidden">
            <div className={cn('h-full rounded-full', i === 0 ? 'bg-red-500' : 'bg-amber-400')}
                 style={{ width: `${(item.ng_qty / max) * 100}%` }} />
          </div>
          <span className="text-xs font-medium text-red-500 w-14 text-right">
            {fmtNumber(item.ng_qty)}
          </span>
          <span className="text-xs text-gray-400 w-12 text-right">
            {fmtPct(item.yield_rate_pct)}
          </span>
        </div>
      ))}
    </div>
  )
}
