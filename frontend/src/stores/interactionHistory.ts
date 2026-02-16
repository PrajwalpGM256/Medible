import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { interactionHistoryApi } from '@/services/api'

export interface HistoryEntry {
  id: number
  food_name: string
  had_interaction: boolean
  interaction_count: number
  max_severity: string | null
  medications_checked: string[]
  created_at: string
}

export const useInteractionHistoryStore = defineStore('interactionHistory', () => {
  const history = ref<HistoryEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const hasFetched = ref(false)

  // Computed
  const highRiskCount = computed(() => 
    history.value.filter(h => h.max_severity === 'high').length
  )
  const totalChecks = computed(() => history.value.length)
  const recentAlerts = computed(() => 
    history.value.filter(h => h.had_interaction).slice(0, 4)
  )

  async function fetchHistory(force = false): Promise<void> {
    // Skip if already fetched, unless forced
    if (hasFetched.value && !force) return
    
    loading.value = true
    error.value = null
    try {
      const { data } = await interactionHistoryApi.getAll(50)
      history.value = data?.data?.history || []
      hasFetched.value = true
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch history'
      console.error('Failed to fetch interaction history:', err)
    } finally {
      loading.value = false
    }
  }

  async function saveCheck(food: string, medications: string[], interactions: any[]): Promise<void> {
    try {
      await interactionHistoryApi.save({
        food_name: food,
        medications,
        interactions,
      })
      // Refresh history to get the new entry
      await fetchHistory(true)
    } catch (err) {
      console.error('Failed to save to history:', err)
    }
  }

  async function deleteEntry(id: number): Promise<void> {
    try {
      await interactionHistoryApi.delete(id)
      history.value = history.value.filter(h => h.id !== id)
    } catch (err) {
      console.error('Failed to delete history item:', err)
    }
  }

  async function clearHistory(): Promise<void> {
    try {
      await interactionHistoryApi.clear()
      history.value = []
    } catch (err) {
      console.error('Failed to clear history:', err)
    }
  }

  function reset(): void {
    history.value = []
    hasFetched.value = false
    error.value = null
  }

  return {
    history,
    loading,
    error,
    hasFetched,
    highRiskCount,
    totalChecks,
    recentAlerts,
    fetchHistory,
    saveCheck,
    deleteEntry,
    clearHistory,
    reset,
  }
})
