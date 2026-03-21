import axios from 'axios'

const BASE = 'http://localhost:8000'

export const signup = (data) => axios.post(`${BASE}/auth/signup`, data)
export const login = (data) => axios.post(`${BASE}/auth/login`, data)
export const getRules = (apiKey) => axios.get(`${BASE}/rules/?api_key=${apiKey}`)
export const createRule = (apiKey, data) => axios.post(`${BASE}/rules/?api_key=${apiKey}`, data)
export const deleteRule = (apiKey, id) => axios.delete(`${BASE}/rules/${id}?api_key=${apiKey}`)