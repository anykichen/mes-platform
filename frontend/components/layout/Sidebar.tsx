'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, BarChart2, TrendingUp,
  FolderOpen, Star, Clock, Lock,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV = [
  { section: '监控', items: [
    { href: '/dashboard',   label: '总览 Dashboard', icon: LayoutDashboard },
    { href: '/stations',    label: '站点分析',        icon: BarChart2 },
    { href: '/trend',       label: '趋势报表',        icon: TrendingUp },
  ]},
  { section: '配置', items: [
    { href: '/projects',    label: '专案管理',        icon: FolderOpen },
    { href: '/keystations', label: '重点站点',        icon: Star },
    { href: '/schedule',    label: '定时任务',        icon: Clock },
    { href: '/account',     label: 'MES 账号',        icon: Lock },
  ]},
]

export function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="w-[200px] min-w-[200px] bg-white border-r border-gray-100 flex flex-col">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-gray-100">
        <div className="text-sm font-semibold text-gray-900">MES 分析中台</div>
        <div className="text-xs text-gray-400 mt-0.5">Auto_THA · V2.0</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {NAV.map(({ section, items }) => (
          <div key={section} className="mb-1">
            <div className="px-4 py-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
              {section}
            </div>
            {items.map(({ href, label, icon: Icon }) => {
              const active = pathname.startsWith(href)
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    'flex items-center gap-2.5 px-4 py-2 text-sm transition-colors border-l-2',
                    active
                      ? 'bg-blue-50 text-blue-700 border-blue-500 font-medium'
                      : 'text-gray-600 border-transparent hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon size={15} />
                  {label}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      {/* Status */}
      <div className="px-4 py-3 border-t border-gray-100 space-y-1.5">
        <div className="text-[10px] text-gray-400 font-medium">系统状态</div>
        {[
          { color: 'bg-green-500', label: 'MES 连接正常' },
          { color: 'bg-green-500', label: '数据库在线' },
          { color: 'bg-amber-400', label: '采集中...' },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5 text-[11px] text-gray-500">
            <span className={cn('w-1.5 h-1.5 rounded-full', color)} />
            {label}
          </div>
        ))}
      </div>
    </aside>
  )
}
