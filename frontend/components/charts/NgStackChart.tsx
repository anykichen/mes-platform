'use client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { CHART_COLORS } from '@/lib/constants'

interface Props {
  data: { date: string; [station: string]: number | string }[]
  stations: string[]
  height?: number
}

export function NgStackChart({ data, stations, height = 220 }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9ca3af' }} />
        <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {stations.map((s, i) => (
          <Bar key={s} dataKey={s} stackId="ng" fill={CHART_COLORS[i % CHART_COLORS.length]}
               fillOpacity={0.8} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
