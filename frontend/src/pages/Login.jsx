import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { signup, login } from '../api'

export default function Login() {
  const [isSignup, setIsSignup] = useState(false)
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async () => {
    try {
      const res = isSignup ? await signup(form) : await login(form)
      localStorage.setItem('api_key', res.data.api_key)
      localStorage.setItem('token', res.data.access_token)
      navigate('/dashboard')
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong')
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '12px', width: '360px', boxShadow: '0 2px 20px rgba(0,0,0,0.1)' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '600', marginBottom: '8px' }}>RateLimiter Pro</h1>
        <p style={{ color: '#666', marginBottom: '24px', fontSize: '14px' }}>{isSignup ? 'Create your account' : 'Sign in to your account'}</p>

        {isSignup && (
          <input
            placeholder="Username"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
            style={inputStyle}
          />
        )}
        <input
          placeholder="Email"
          value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
          style={inputStyle}
        />
        <input
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
          style={inputStyle}
        />

        {error && <p style={{ color: 'red', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}

        <button onClick={handleSubmit} style={btnStyle}>
          {isSignup ? 'Create Account' : 'Sign In'}
        </button>

        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', color: '#666' }}>
          {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
          <span onClick={() => setIsSignup(!isSignup)} style={{ color: '#4f46e5', cursor: 'pointer' }}>
            {isSignup ? 'Sign in' : 'Sign up'}
          </span>
        </p>
      </div>
    </div>
  )
}

const inputStyle = {
  width: '100%', padding: '10px 12px', marginBottom: '12px',
  border: '1px solid #e5e7eb', borderRadius: '8px', fontSize: '14px', outline: 'none'
}
const btnStyle = {
  width: '100%', padding: '10px', background: '#4f46e5', color: 'white',
  border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '500', cursor: 'pointer'
}