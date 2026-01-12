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
  const highRiskCount = computed(() => interactions.value.filter(i => i.severity === 'high').length)
  const hasHighRisk = computed(() => highRiskCount.value > 0)

  async function fetchMedications(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await userMedicationApi.getAll()
      // Backend returns { data: { medications: [...] } }
      const meds = response.data?.data?.medications || response.data?.medications || []
      medications.value = meds.map((m: any) => ({
        id: m.id,
        drugName: m.drug_name || m.drugName,
        genericName: m.generic_name || m.genericName,
        dosage: m.dosage,
        frequency: m.frequency,
        createdAt: m.created_at || m.createdAt,
      }))
      await fetchAllInteractions()
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch medications'
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
      const response = await drugApi.search(query)
      // Backend returns { data: { query, count, drugs: [...] } } wrapped in response.data
      const responseData = response.data
      // Handle both wrapped ({ data: { drugs } }) and unwrapped ({ drugs }) formats
      const drugs = responseData?.data?.drugs || responseData?.drugs || []
      console.log('Drug search response:', responseData, 'Extracted drugs:', drugs)
      searchResults.value = drugs.map((d: any) => ({
        brandName: d.brand_name || d.brandName || 'Unknown',
        genericName: d.generic_name || d.genericName || 'Unknown',
        manufacturer: d.manufacturer,
      }))
      console.log('Mapped searchResults:', searchResults.value)
    } catch (err) {
      console.error('Drug search error:', err)
      searchResults.value = []
    } finally {
      searchLoading.value = false
    }
  }

  async function addMedication(drugName: string, dosage?: string, frequency?: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const response = await userMedicationApi.add({ drug_name: drugName, dosage, frequency })
      // Backend returns { data: { medication: {...} } }
      const med = response.data?.data?.medication || response.data?.medication
      if (med) {
        medications.value.push({
          id: med.id,
          drugName: med.drug_name || med.drugName,
          genericName: med.generic_name || med.genericName,
          dosage: med.dosage,
          frequency: med.frequency,
          createdAt: med.created_at || med.createdAt,
        })
      }
      await fetchAllInteractions()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to add medication'
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
