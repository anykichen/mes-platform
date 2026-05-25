'use client'
import { AlertTriangle, X } from 'lucide-react'
import { useState } from 'react'

interface AlertStripProps {
  message: string
  onAction?: () => void
  actionLabel?: string
}

export function AlertStrip({ message, onAction, actionLabel = '查看分析' }: AlertStripProps) {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg mb-4 text-xs text-amber-700">
      <AlertTriangle size={14} className="shrink-0" />
      <span className="flex-1">{message}</span>
      {onAction && (
        <button onClick={onAction} className="text-amber-700 font-medium hover:underline shrink-0">
          {actionLabel} ↗
        </button>
      )}
      <button onClick={() => setVisible(false)} className="ml-1 text-amber-400 hover:text-amber-600">
        <X size={13} />
      </button>
    </div>
  )
}
