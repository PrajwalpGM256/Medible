import axios from 'axios'
import { API_BASE_URL, API_CONFIG, ENDPOINTS } from '@/constants'

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
      // Clear token from localStorage
      // The auth store will handle logout and redirect
      localStorage.removeItem('token')
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
  updateProfile: (data: { first_name?: string; last_name?: string; email?: string }) =>
    api.patch(ENDPOINTS.AUTH.UPDATE_PROFILE, data),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.put(ENDPOINTS.AUTH.CHANGE_PASSWORD, { current_password: currentPassword, new_password: newPassword }),
  deleteAccount: (password: string) =>
    api.delete(ENDPOINTS.AUTH.DELETE_ACCOUNT, { data: { password } }),
  exportData: () => api.get(ENDPOINTS.AUTH.EXPORT_DATA),
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
  checkMultiple: (food: string, medications: string[]) =>
    api.post(ENDPOINTS.INTERACTIONS.CHECK_MULTIPLE, { food, medications }),
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

// Food Diary APIs
export const foodDiaryApi = {
  getToday: () => api.get(ENDPOINTS.FOOD_DIARY.TODAY),
  getByDate: (date: string) => api.get(ENDPOINTS.FOOD_DIARY.LIST, { params: { date } }),
  getRange: (startDate: string, endDate: string) =>
    api.get(ENDPOINTS.FOOD_DIARY.LIST, { params: { start_date: startDate, end_date: endDate } }),
  getSummary: (days: number = 7) =>
    api.get(ENDPOINTS.FOOD_DIARY.SUMMARY, { params: { days } }),
  add: (data: {
    food_name: string
    fdc_id?: number
    brand_owner?: string
    servings?: number
    serving_size?: number
    serving_unit?: string
    calories?: number
    protein?: number
    carbs?: number
    fat?: number
    fiber?: number
    sugar?: number
    sodium?: number
    meal_type?: string
    notes?: string
    logged_date?: string
    had_interaction?: boolean
    interaction_count?: number
  }) => api.post(ENDPOINTS.FOOD_DIARY.ADD, data),
  remove: (id: number) => api.delete(ENDPOINTS.FOOD_DIARY.REMOVE(id)),
  update: (id: number, data: any) => api.patch(ENDPOINTS.FOOD_DIARY.UPDATE(id), data),
}

// Interaction History APIs
export const interactionHistoryApi = {
  getAll: (limit: number = 50) =>
    api.get(ENDPOINTS.INTERACTION_HISTORY.LIST, { params: { limit } }),
  save: (data: {
    food_name: string
    medications: string[]
    interactions: any[]
  }) => api.post(ENDPOINTS.INTERACTION_HISTORY.SAVE, data),
  delete: (id: number) => api.delete(ENDPOINTS.INTERACTION_HISTORY.DELETE(id)),
  clear: () => api.delete(ENDPOINTS.INTERACTION_HISTORY.CLEAR),
}

export default api