import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

export default function App() {
  const apiKey = localStorage.getItem('api_key')
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={apiKey ? <Dashboard /> : <Navigate to="/login" />} />
      <Route path="*" element={<Navigate to={apiKey ? "/dashboard" : "/login"} />} />
    </Routes>
  )
}