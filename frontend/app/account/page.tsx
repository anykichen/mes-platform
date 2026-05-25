'use client'
import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { api } from '@/lib/api'
import { Topbar } from '@/components/layout/Topbar'
import { MesAccount, LoginTestResult } from '@/types'
import { fmtDatetime } from '@/lib/utils'
import { Shield, TestTube, Save, Eye, EyeOff } from 'lucide-react'

export default function AccountPage() {
  const { data: account, mutate } = useSWR('account', api.account.get)
  const acc = account as MesAccount | undefined

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPwd, setShowPwd]   = useState(false)
  const [saving, setSaving]     = useState(false)
  const [testing, setTesting]   = useState(false)
  const [testResult, setTestResult] = useState<LoginTestResult | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (acc) setUsername(acc.username)
  }, [acc])

  async function handleSave() {
    if (!password) { alert('请输入新密码'); return }
    setSaving(true)
    await api.account.update({ username, password })
    setSaved(true)
    setPassword('')
    setSaving(false)
    mutate()
    setTimeout(() => setSaved(false), 3000)
  }

  async function handleTest() {
    setTesting(true)
    setTestResult(null)
    const result = await api.account.testLogin() as LoginTestResult
    setTestResult(result)
    setTesting(false)
  }

  return (
    <div>
      <Topbar title="MES 账号设置" />
      <div className="p-6">
        <div className="max-w-lg space-y-4">
          <div className="card">
            <div className="flex items-center gap-2 mb-4 text-sm font-medium text-gray-700">
              <Shield size={15} className="text-blue-500" />MES 账号配置
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">MES 账号</label>
                <input className="input w-full" value={username} onChange={e => setUsername(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">MES 密码 <span className="text-gray-400">（AES-256 加密存储）</span></label>
                <div className="relative">
                  <input
                    className="input w-full pr-9"
                    type={showPwd ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="输入新密码"
                  />
                  <button
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPwd(!showPwd)}
                  >
                    {showPwd ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
              <button className="btn-secondary flex-1 justify-center" onClick={handleTest} disabled={testing}>
                <TestTube size={13} />
                {testing ? '测试中...' : '测试登录'}
              </button>
              <button className="btn-primary flex-1 justify-center" onClick={handleSave} disabled={saving}>
                <Save size={13} />
                {saving ? '保存中...' : saved ? '✓ 已保存' : '保存设置'}
              </button>
            </div>

            {testResult && (
              <div className={`mt-3 p-3 rounded-lg text-xs flex items-start gap-2 ${
                testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                <span>{testResult.success ? '✓' : '✗'}</span>
                <div>
                  <div className="font-medium">{testResult.success ? '登录成功' : '登录失败'}</div>
                  <div className="mt-0.5 text-xs opacity-75">{testResult.message}</div>
                </div>
              </div>
            )}

            {acc && (
              <div className="mt-3 text-xs text-gray-400 space-y-1">
                <div>上次更新: {fmtDatetime(acc.updated_at)}</div>
                {acc.last_login_at && (
                  <div>上次登录: {fmtDatetime(acc.last_login_at)}
                    <span className={`ml-2 ${acc.last_login_ok ? 'text-green-600' : 'text-red-500'}`}>
                      {acc.last_login_ok ? '成功' : '失败'}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
