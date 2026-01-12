import axios from 'axios'
import { API_BASE_URL, API_CONFIG, ENDPOINTS, ROUTES } from '@/constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // Use Vue Router instead of hard redirect to preserve app state
      const currentPath = window.location.pathname
      if (currentPath !== ROUTES.LOGIN && currentPath !== ROUTES.REGISTER) {
        window.location.href = `${ROUTES.LOGIN}?redirect=${encodeURIComponent(currentPath)}`
      }
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const authApi = {
  login: (email: string, password: string) =>
    api.post(ENDPOINTS.AUTH.LOGIN, { email, password }),
  register: (data: { email: string; password: string; name?: string; first_name?: string; last_name?: string }) =>
    api.post(ENDPOINTS.AUTH.REGISTER, data),
  logout: () => api.post(ENDPOINTS.AUTH.LOGOUT),
  getProfile: () => api.get(ENDPOINTS.AUTH.PROFILE),
}

// Drug APIs
export const drugApi = {
  search: (query: string) =>
    api.get(ENDPOINTS.DRUGS.SEARCH, { params: { q: query } }),
  getDetails: (name: string) => api.get(ENDPOINTS.DRUGS.DETAILS(name)),
  getInteractions: (name: string) => api.get(ENDPOINTS.DRUGS.INTERACTIONS(name)),
}

// Food APIs
export const foodApi = {
  search: (query: string) =>
    api.get(ENDPOINTS.FOODS.SEARCH, { params: { q: query } }),
  getDetails: (fdcId: string) => api.get(ENDPOINTS.FOODS.DETAILS(fdcId)),
}

// Interaction APIs
export const interactionApi = {
  check: (drug: string, food: string) =>
    api.get(ENDPOINTS.INTERACTIONS.CHECK, { params: { drug, food } }),
  getByDrug: (name: string) => api.get(ENDPOINTS.INTERACTIONS.BY_DRUG(name)),
  getAll: () => api.get(ENDPOINTS.INTERACTIONS.ALL),
}

// User Medication APIs
export const userMedicationApi = {
  getAll: () => api.get(ENDPOINTS.USER_MEDICATIONS.LIST),
  add: (data: { drug_name: string; dosage?: string; frequency?: string }) =>
    api.post(ENDPOINTS.USER_MEDICATIONS.ADD, data),
  remove: (id: number) => api.delete(ENDPOINTS.USER_MEDICATIONS.REMOVE(id)),
  update: (id: number, data: { dosage?: string; frequency?: string }) =>
    api.put(ENDPOINTS.USER_MEDICATIONS.UPDATE(id), data),
}

export default api