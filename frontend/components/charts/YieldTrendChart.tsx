'use client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { TrendPoint } from '@/types'
import { YIELD_THRESHOLDS } from '@/lib/constants'

interface Props {
  data: TrendPoint[]
  stationName?: string
  height?: number
}

export function YieldTrendChart({ data, stationName, height = 200 }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9ca3af' }} />
        <YAxis domain={['auto', 100]} tick={{ fontSize: 11, fill: '#9ca3af' }}
               tickFormatter={v => `${v}%`} />
        <Tooltip
          formatter={(v: number) => [`${v.toFixed(2)}%`, stationName || '良率']}
          labelStyle={{ color: '#374151', fontSize: 12 }}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
        />
        <ReferenceLine y={YIELD_THRESHOLDS.good} stroke="#16a34a" strokeDasharray="4 4"
                       label={{ value: `目标 ${YIELD_THRESHOLDS.good}%`, fill: '#16a34a', fontSize: 10, position: 'right' }} />
        <Line type="monotone" dataKey="yield_rate_pct" stroke="#185fa5"
              strokeWidth={2} dot={{ r: 3, fill: '#185fa5' }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
