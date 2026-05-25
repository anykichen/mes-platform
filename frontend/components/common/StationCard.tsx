import { StationCard as StationCardType } from '@/types'
import { StatusBadge } from './StatusBadge'
import { cn, fmtNumber, fmtPct } from '@/lib/utils'
import { YIELD_THRESHOLDS } from '@/lib/constants'

export function StationCard({ card }: { card: StationCardType }) {
  const barColor =
    card.yield_rate_pct >= YIELD_THRESHOLDS.good ? 'bg-green-500' :
    card.yield_rate_pct >= YIELD_THRESHOLDS.warn ? 'bg-amber-400' : 'bg-red-500'

  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-gray-50 last:border-0">
      <div className="w-28 text-sm font-medium text-gray-900 truncate">{card.station_name}</div>
      {card.show_yield && (
        <div className="flex items-center gap-2 flex-1">
          <span className="text-xs w-12 text-right text-gray-700">{fmtPct(card.yield_rate_pct)}</span>
          <div className="yield-bar">
            <div className={cn('h-full rounded-full transition-all', barColor)}
                 style={{ width: `${card.yield_rate_pct}%` }} />
          </div>
        </div>
      )}
      {card.show_ng && (
        <span className="text-xs text-red-500 w-12 text-right">{fmtNumber(card.ng_qty)}</span>
      )}
      <StatusBadge status={card.status} />
    </div>
  )
}
