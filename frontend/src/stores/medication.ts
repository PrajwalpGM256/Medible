import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { drugApi, userMedicationApi, interactionApi } from '@/services/api'
import type { Medication, DrugSearchResult, Interaction } from '@/types'

export const useMedicationsStore = defineStore('medications', () => {
  const medications = ref<Medication[]>([])
  const searchResults = ref<DrugSearchResult[]>([])
  const interactions = ref<Interaction[]>([])
  const loading = ref(false)
  const searchLoading = ref(false)
  const error = ref<string | null>(null)

  const count = computed(() => medications.value.length)
  const highRiskCount = computed(() => 
    interactions.value.filter(i => i.severity === 'high').length
  )
  const hasHighRisk = computed(() => highRiskCount.value > 0)

  async function fetchMedications(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const { data } = await userMedicationApi.getAll()
      medications.value = data
      await fetchAllInteractions()
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch medications'
    } finally {
      loading.value = false
    }
  }

  async function searchDrugs(query: string): Promise<void> {
    if (!query.trim()) {
      searchResults.value = []
      return
    }
    searchLoading.value = true
    try {
      const { data } = await drugApi.search(query)
      searchResults.value = data.results || []
    } catch {
      searchResults.value = []
    } finally {
      searchLoading.value = false
    }
  }

  async function addMedication(
    drugName: string, 
    dosage?: string, 
    frequency?: string
  ): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const { data } = await userMedicationApi.add({ drug_name: drugName, dosage, frequency })
      medications.value.push(data)
      await fetchAllInteractions()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to add medication'
      return false
    } finally {
      loading.value = false
    }
  }

  async function removeMedication(id: number): Promise<boolean> {
    loading.value = true
    try {
      await userMedicationApi.remove(id)
      medications.value = medications.value.filter(m => m.id !== id)
      await fetchAllInteractions()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to remove'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchAllInteractions(): Promise<void> {
    if (!medications.value.length) {
      interactions.value = []
      return
    }
    const all: Interaction[] = []
    for (const med of medications.value) {
      try {
        const { data } = await interactionApi.getByDrug(med.drugName)
        if (data.interactions) all.push(...data.interactions)
      } catch { /* skip */ }
    }
    // Deduplicate
    interactions.value = all.filter((item, idx, arr) =>
      idx === arr.findIndex(i => i.drugName === item.drugName && i.foodName === item.foodName)
    )
  }

  function clearSearch(): void {
    searchResults.value = []
  }

  return {
    medications, searchResults, interactions,
    loading, searchLoading, error,
    count, highRiskCount, hasHighRisk,
    fetchMedications, searchDrugs, addMedication,
    removeMedication, clearSearch,
  }
})