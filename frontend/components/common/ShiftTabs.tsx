'use client'
import { SHIFTS } from '@/lib/constants'
import { cn } from '@/lib/utils'

interface ShiftTabsProps {
  value: string
  onChange: (v: string) => void
}

export function ShiftTabs({ value, onChange }: ShiftTabsProps) {
  return (
    <div className="flex gap-0 bg-gray-100 rounded-lg p-0.5 w-fit">
      {SHIFTS.map(s => (
        <button
          key={s.value}
          onClick={() => onChange(s.value)}
          className={cn(
            'px-3 py-1 text-xs rounded-md transition-all',
            value === s.value
              ? 'bg-white text-gray-900 shadow-sm font-medium'
              : 'text-gray-500 hover:text-gray-700'
          )}
        >
          {s.label}
        </button>
      ))}
    </div>
  )
}
