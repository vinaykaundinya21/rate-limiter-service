import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRules, createRule, deleteRule, getAnalytics } from '../api'

export default function Dashboard() {
  const [rules, setRules] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [form, setForm] = useState({ client_id_pattern: '', algorithm: 'token_bucket', capacity: 10, refill_rate: 1.0, limit: 10, window_seconds: 60 })
  const [error, setError] = useState('')
  const apiKey = localStorage.getItem('api_key')
  const navigate = useNavigate()

  useEffect(() => {
    fetchRules()
    fetchAnalytics()
  }, [])

  const fetchRules = async () => {
    try {
      const res = await getRules(apiKey)
      setRules(res.data)
    } catch (e) { setError('Failed to load rules') }
  }

  const fetchAnalytics = async () => {
    try {
      const res = await getAnalytics(apiKey)
      setAnalytics(res.data)
    } catch (e) { console.log('analytics error', e) }
  }

  const handleCreate = async () => {
    try {
      await createRule(apiKey, form)
      setForm({ client_id_pattern: '', algorithm: 'token_bucket', capacity: 10, refill_rate: 1.0, limit: 10, window_seconds: 60 })
      fetchRules()
    } catch (e) { setError('Failed to create rule') }
  }

  const handleDelete = async (id) => {
    await deleteRule(apiKey, id)
    fetchRules()
  }

  const logout = () => {
    localStorage.clear()
    navigate('/login')
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '600' }}>RateLimiter Pro</h1>
        <button onClick={logout} style={{ padding: '8px 16px', border: '1px solid #e5e7eb', borderRadius: '8px', background: 'white', cursor: 'pointer', fontSize: '14px' }}>Logout</button>
      </div>

      <div style={cardStyle}>
        <h2 style={labelStyle}>Your API Key</h2>
        <code style={{ background: '#f3f4f6', padding: '10px 14px', borderRadius: '8px', display: 'block', fontSize: '13px', wordBreak: 'break-all' }}>{apiKey}</code>
      </div>

      <div style={cardStyle}>
        <h2 style={labelStyle}>Usage Analytics</h2>
        {analytics ? (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
              <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                <p style={{ fontSize: '28px', fontWeight: '600', color: '#16a34a' }}>{analytics.total_requests}</p>
                <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>Total Requests</p>
              </div>
              <div style={{ background: '#eff6ff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                <p style={{ fontSize: '28px', fontWeight: '600', color: '#2563eb' }}>{analytics.allowed}</p>
                <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>Allowed</p>
              </div>
              <div style={{ background: '#fef2f2', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                <p style={{ fontSize: '28px', fontWeight: '600', color: '#dc2626' }}>{analytics.blocked}</p>
                <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>Blocked</p>
              </div>
            </div>
            <p style={{ fontSize: '13px', color: '#6b7280' }}>Block rate: <strong>{analytics.block_rate}%</strong></p>
          </>
        ) : (
          <p style={{ color: '#9ca3af', fontSize: '14px' }}>No requests yet. Make some API calls to see analytics.</p>
        )}
      </div>

      <div style={cardStyle}>
        <h2 style={labelStyle}>Create Rate Limit Rule</h2>
        {error && <p style={{ color: 'red', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <input placeholder="Client ID pattern (e.g. myapp)" value={form.client_id_pattern} onChange={e => setForm({ ...form, client_id_pattern: e.target.value })} style={inputStyle} />
          <select value={form.algorithm} onChange={e => setForm({ ...form, algorithm: e.target.value })} style={inputStyle}>
            <option value="token_bucket">Token Bucket</option>
            <option value="sliding_window">Sliding Window</option>
            <option value="fixed_window">Fixed Window</option>
          </select>
          <input placeholder="Capacity" type="number" value={form.capacity} onChange={e => setForm({ ...form, capacity: parseInt(e.target.value) })} style={inputStyle} />
          <input placeholder="Refill Rate" type="number" value={form.refill_rate} onChange={e => setForm({ ...form, refill_rate: parseFloat(e.target.value) })} style={inputStyle} />
          <input placeholder="Limit" type="number" value={form.limit} onChange={e => setForm({ ...form, limit: parseInt(e.target.value) })} style={inputStyle} />
          <input placeholder="Window (seconds)" type="number" value={form.window_seconds} onChange={e => setForm({ ...form, window_seconds: parseInt(e.target.value) })} style={inputStyle} />
        </div>
        <button onClick={handleCreate} style={{ ...btnStyle, marginTop: '12px' }}>Create Rule</button>
      </div>

      <div style={cardStyle}>
        <h2 style={labelStyle}>Active Rules ({rules.length})</h2>
        {rules.length === 0 ? (
          <p style={{ color: '#9ca3af', fontSize: '14px' }}>No rules yet. Create one above.</p>
        ) : (
          rules.map(rule => (
            <div key={rule.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#f9fafb', borderRadius: '8px', marginBottom: '8px' }}>
              <div>
                <p style={{ fontWeight: '500', fontSize: '14px' }}>{rule.client_id_pattern}</p>
                <p style={{ color: '#6b7280', fontSize: '12px' }}>{rule.algorithm} · capacity {rule.capacity} · refill {rule.refill_rate}/s</p>
              </div>
              <button onClick={() => handleDelete(rule.id)} style={{ padding: '6px 12px', border: '1px solid #fee2e2', borderRadius: '6px', background: '#fef2f2', color: '#dc2626', cursor: 'pointer', fontSize: '13px' }}>Delete</button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const cardStyle = { background: 'white', padding: '1.5rem', borderRadius: '12px', marginBottom: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }
const labelStyle = { fontSize: '15px', fontWeight: '600', marginBottom: '16px' }
const inputStyle = { padding: '10px 12px', border: '1px solid #e5e7eb', borderRadius: '8px', fontSize: '14px', outline: 'none', width: '100%' }
const btnStyle = { padding: '10px 20px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '500', cursor: 'pointer' }