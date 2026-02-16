import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'
import type { User } from '@/types'
import { useMedicationsStore } from './medications'
import { useInteractionHistoryStore } from './interactionHistory'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.name || '')

  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login(email, password)
      const { data } = response.data // Backend wraps in { data: {...} }
      token.value = data.tokens.access_token
      user.value = data.user
      localStorage.setItem('token', data.tokens.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(name: string, email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      // Split name into first and last
      const nameParts = name.trim().split(' ')
      const firstName = nameParts[0] || ''
      const lastName = nameParts.slice(1).join(' ') || ''
      
      const response = await authApi.register({ 
        email, 
        password, 
        name,
        first_name: firstName,
        last_name: lastName
      })
      const { data } = response.data // Backend wraps in { data: {...} }
      token.value = data.tokens.access_token
      user.value = data.user
      localStorage.setItem('token', data.tokens.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile(): Promise<void> {
    if (!token.value) return
    loading.value = true
    try {
      const response = await authApi.getProfile()
      user.value = response.data.data // Backend wraps in { data: {...} }
    } catch {
      logout()
    } finally {
      loading.value = false
    }
  }

  async function validateSession(): Promise<boolean> {
    // Validates the current token with the backend
    // Returns false if token is invalid (e.g., server restarted with new secret)
    if (!token.value) {
      console.log('🔐 No token found, session invalid')
      return false
    }
    loading.value = true
    console.log('🔐 Validating session with backend...')
    try {
      const response = await authApi.getProfile()
      user.value = response.data.data
      console.log('✅ Session valid, user:', user.value?.email)
      return true
    } catch (err) {
      // Token is invalid - clear auth state
      console.log('❌ Session invalid, logging out. Error:', err)
      logout()
      return false
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    
    // Reset other stores to clear cached data
    const medsStore = useMedicationsStore()
    const historyStore = useInteractionHistoryStore()
    medsStore.reset()
    historyStore.reset()
  }

  function clearError(): void {
    error.value = null
  }

  return {
    user, token, loading, error,
    isAuthenticated, userName,
    login, register, logout, fetchProfile, validateSession, clearError,
  }
})
